import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..services.fpl_api_client import FPLApiException

_logger = logging.getLogger(__name__)

POSITION_KEYS = {'GKP': 'lineup_gkp', 'DEF': 'lineup_def', 'MID': 'lineup_mid', 'FWD': 'lineup_fwd'}
STARTING_XI = 11
# Picks of a gameweek that is not final are refreshed at most that often
LIVE_RESYNC_DELAY = timedelta(minutes=1)


class FplGameweekPicks(models.Model):
    _name = 'fpl.gameweek.picks'
    _inherit = ['fpl.api.mixin']
    _description = 'FPL Gameweek Picks'
    _order = 'event_id desc'

    manager_id = fields.Many2one('fpl.manager.team', string='Manager', required=True, index=True,
                                 ondelete='cascade')
    event_id = fields.Many2one('fpl.events', string='Event', required=True, index=True, ondelete='cascade')
    active_chip = fields.Char(string='Active Chip')
    points = fields.Integer(string='Points')
    total_points = fields.Integer(string='Total Points')
    rank = fields.Integer(string='Rank')
    rank_sort = fields.Integer(string='Rank Sort')
    overall_rank = fields.Integer(string='Overall Rank')
    percentile_rank = fields.Integer(string='Percentile Rank')
    bank = fields.Float(string='Bank')
    value = fields.Float(string='Value')
    event_transfers = fields.Integer(string='Event Transfers')
    event_transfers_cost = fields.Integer(string='Event Transfers Cost')
    points_on_bench = fields.Integer(string='Points on Bench')
    pick_lines = fields.One2many('fpl.gameweek.pick.lines', 'gameweek_pick_id', string='Pick Lines')
    synced_at = fields.Datetime(string='Synced At', readonly=True)

    _sql_constraints = [
        ('manager_event_uniq', 'unique(manager_id, event_id)', 'Picks already exist for this manager and gameweek.'),
    ]

    @api.depends('manager_id.name', 'event_id.name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'{rec.manager_id.name or ""} - {rec.event_id.name or ""}'

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------

    @api.model
    def _sync_gameweek_picks(self, manager, event):
        """Fetch the picks of ``manager`` for ``event`` and the gameweek live
        data (points breakdown), then store them."""
        results, errors = self._fpl_fetch_many({
            'picks': ('get_gameweek_picks', (manager.manager_id, event.event_id)),
            'live': ('get_element_gameweek_live', (event.event_id,)),
        })
        if 'picks' in errors:
            error = errors['picks']
            if isinstance(error, FPLApiException) and error.status_code == 404:
                # The manager joined after this gameweek: nothing to show
                return self.browse()
            raise self._fpl_user_error(_("Failed to sync gameweek picks"), error) from error
        if 'live' in errors:
            _logger.warning("Live data of %s unavailable: %s", event.name, errors['live'])

        data = results['picks'] or {}
        entry_history = data.get('entry_history') or {}
        vals = {
            'manager_id': manager.id,
            'event_id': event.id,
            'active_chip': data.get('active_chip') or False,
            'points': entry_history.get('points'),
            'total_points': entry_history.get('total_points'),
            'rank': entry_history.get('rank'),
            'rank_sort': entry_history.get('rank_sort'),
            'overall_rank': entry_history.get('overall_rank'),
            'percentile_rank': entry_history.get('percentile_rank'),
            'bank': self._fpl_tenths(entry_history.get('bank')),
            'value': self._fpl_tenths(entry_history.get('value')),
            'event_transfers': entry_history.get('event_transfers'),
            # A transfer hit is a number of points, not a price
            'event_transfers_cost': entry_history.get('event_transfers_cost'),
            'points_on_bench': entry_history.get('points_on_bench'),
            'synced_at': fields.Datetime.now(),
        }
        existing = self.search([('manager_id', '=', manager.id), ('event_id', '=', event.id)], limit=1)
        gameweek_pick = self._fpl_upsert(self, {1: existing} if existing else {}, {1: vals})[1]
        live_elements = {element.get('id'): element for element in (results.get('live') or {}).get('elements') or []}
        self.env['fpl.gameweek.pick.lines']._sync_pick_lines(gameweek_pick, data.get('picks') or [], live_elements,
                                                              event)
        return gameweek_pick

    def _needs_sync(self, event):
        """A gameweek whose data is final never changes again; the others
        (live / current one) are refreshed at most every minute."""
        if not self:
            return True
        if event.finished and (event.data_checked or not event.is_current):
            return False
        return not self.synced_at or fields.Datetime.now() - self.synced_at > LIVE_RESYNC_DELAY

    # ------------------------------------------------------------------
    # Client API (pitch view)
    # ------------------------------------------------------------------

    @api.model
    def get_gameweek_picks_data(self, manager_id, event_id, force_sync=False):
        """Everything the pitch view needs in a single RPC.

        Syncs from the FPL API only when needed (see ``_needs_sync``) or when
        ``force_sync`` is set.
        """
        manager = self.env['fpl.manager.team'].browse(int(manager_id)).exists()
        event = self.env['fpl.events'].browse(int(event_id)).exists()
        if not manager or not event:
            raise UserError(_("Invalid gameweek or manager selection."))
        gameweek_pick = self.search([('manager_id', '=', manager.id), ('event_id', '=', event.id)], limit=1)
        if force_sync or gameweek_pick._needs_sync(event):
            gameweek_pick = self._sync_gameweek_picks(manager, event)
        if not gameweek_pick:
            return {'found': False}
        return gameweek_pick._get_pitch_data()

    def _get_pitch_data(self):
        self.ensure_one()
        formation = {key: [] for key in POSITION_KEYS.values()}
        formation['sub_elements'] = []
        players = {}
        for line in self.pick_lines.sorted('position'):
            position_name = line.element_type_id.plural_name_short or ''
            if line.position > STARTING_XI:
                formation['sub_elements'].append(line.id)
            elif position_name in POSITION_KEYS:
                formation[POSITION_KEYS[position_name]].append(line.id)
            players[line.id] = {
                'name': line.web_name or line.element_id.web_name,
                'team': line.team_name,
                'position': position_name,
                'multiplier': line.multiplier,
                'is_captain': line.is_captain,
                'is_vice_captain': line.is_vice_captain,
                'total_points': line.total_points,
                'team_code': line.team_code or '',
                'team_id': line.team_id.id,
            }
        return {
            'found': True,
            'formation': formation,
            'players': players,
            'stats': {
                'points': self.points,
                'total_points': self.total_points,
                'rank': self.rank,
                'bank': self.bank,
                'value': self.value,
                'event_transfers': self.event_transfers,
                'event_transfers_cost': self.event_transfers_cost,
                'active_chip': self.active_chip,
            },
        }
