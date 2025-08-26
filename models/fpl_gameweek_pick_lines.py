from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .fpl_api_mixin import FPLApiMixin
from ..services.fpl_api_client import FPLApiException
import logging

_logger = logging.getLogger(__name__)

class FplGameweekPickLines(models.Model, FPLApiMixin):
    _name = 'fpl.gameweek.pick.lines'
    _description = 'FPL Gameweek Pick Lines'

    gameweek_pick_id = fields.Many2one('fpl.gameweek.picks', string=_('Gameweek Pick'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    position = fields.Integer(string=_('Points'))
    multiplier = fields.Integer(string=_('Multiplier'))
    is_captain = fields.Boolean(string=_('Is Captain'))
    is_vice_captain = fields.Boolean(string=_('Is Vice Captain'))
    element_type_id = fields.Many2one('fpl.element.types', string=_('Element Type'))
    team_id = fields.Many2one('fpl.teams', string=_('Team'))
    team_name = fields.Char(related='team_id.name')
    parent_id = fields.Many2one('fpl.gameweek.pick.lines', string=_('Parent'))
    web_name = fields.Char(related='element_id.web_name')
    plural_name_short= fields.Char(related='element_type_id.plural_name_short')
    child_ids = fields.One2many('fpl.gameweek.pick.lines', 'parent_id', string=_('Children'))

    @api.model
    def sync_gameweek_picks(self, manager_team, gw):
        try:
            exist_pick = self.env['fpl.gameweek.picks'].search([('manager_id', '=', manager_team.get('id')), ('event_id', '=', gw.get('id'))])
            # if exist_pick and not gw.is_current:
            if exist_pick:
                return

            # if gw.is_current:
                # gw_picks = manager_team.sync_from_fpl_api('get_gameweek_picks', team_id=manager_team.manager_id, gw_id=gw.event_id)

            gw_picks = {
            "active_chip": None,
            "automatic_subs": [
                {
                    "entry": 894358,
                    "element_in": 568,
                    "element_out": 235,
                    "event": 2
                }
            ],
            "entry_history": {
                "event": 2,
                "points": 47,
                "total_points": 97,
                "rank": 6465899,
                "rank_sort": 6479547,
                "overall_rank": 6131779,
                "percentile_rank": 65,
                "bank": 5,
                "value": 1000,
                "event_transfers": 0,
                "event_transfers_cost": 0,
                "points_on_bench": 10
            },
            "picks": [
                {
                    "element": 470,
                    "position": 1,
                    "multiplier": 1,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 1
                },
                {
                    "element": 261,
                    "position": 2,
                    "multiplier": 1,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 2
                },
                {
                    "element": 191,
                    "position": 3,
                    "multiplier": 1,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 2
                },
                {
                    "element": 505,
                    "position": 4,
                    "multiplier": 1,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 2
                },
                {
                    "element": 568,
                    "position": 5,
                    "multiplier": 1,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 2
                },
                {
                    "element": 449,
                    "position": 6,
                    "multiplier": 1,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 3
                },
                {
                    "element": 381,
                    "position": 7,
                    "multiplier": 2,
                    "is_captain": True,
                    "is_vice_captain": False,
                    "element_type": 3
                },
                {
                    "element": 299,
                    "position": 8,
                    "multiplier": 1,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 3
                },
                {
                    "element": 242,
                    "position": 9,
                    "multiplier": 1,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 3
                },
                {
                    "element": 283,
                    "position": 10,
                    "multiplier": 1,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 4
                },
                {
                    "element": 64,
                    "position": 11,
                    "multiplier": 1,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 4
                },
                {
                    "element": 220,
                    "position": 12,
                    "multiplier": 0,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 1
                },
                {
                    "element": 235,
                    "position": 13,
                    "multiplier": 0,
                    "is_captain": False,
                    "is_vice_captain": True,
                    "element_type": 3
                },
                {
                    "element": 575,
                    "position": 14,
                    "multiplier": 0,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 2
                },
                {
                    "element": 252,
                    "position": 15,
                    "multiplier": 0,
                    "is_captain": False,
                    "is_vice_captain": False,
                    "element_type": 4
                }
            ]
        }
            entry_history = gw_picks.get('entry_history')
            gw_pick_lines = gw_picks.get('picks')
            gw_pick_val = {
                'event_id': gw.get('id'),
                'manager_id': manager_team.get('id'),
                'points': entry_history.get('points'),
                'total_points': entry_history.get('total_points'),
                'rank': entry_history.get('rank'),
                'rank_sort': entry_history.get('rank_sort'),
                'overall_rank': entry_history.get('overall_rank'),
                'percentile_rank': entry_history.get('percentile_rank'),
                'bank': entry_history.get('bank') / 10,
                'value': entry_history.get('value') / 10,
                'event_transfers': entry_history.get('event_transfers'),
                'event_transfers_cost': entry_history.get('event_transfers_cost') / 10,
                'points_on_bench': entry_history.get('points_on_bench'),
            }

            if exist_pick:
                exist_pick.update(gw_pick_val)
            else:
                create_gw_pick = self.env['fpl.gameweek.picks'].create(gw_pick_val)
                exist_pick = create_gw_pick

            self._get_gw_picks_lines(gw_pick_lines, exist_pick)

        except FPLApiException as e:
            _logger.error(f"Failed to sync manager data: {str(e)}")
            raise UserError(f"Failed to sync manager data: {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error during sync: {str(e)}")
            raise UserError(f"Unexpected error during sync: {str(e)}")
    
    def _get_gw_picks_lines(self, picks, gw_pick):
        line_vals =[]
        for pick in picks:
            element_id = self.env['fpl.elements'].search([('element_id', '=', pick.get('element'))])
            val = {
                'gameweek_pick_id': gw_pick.id,
                'element_id': element_id.id,
                'element_type_id': self.env['fpl.element.types'].search([('element_type_id', '=', pick.get('element_type'))]).id,
                'team_id': element_id.fpl_team_id.id,
                'position': pick.get('position'),
                'multiplier': pick.get('multiplier'),
                'is_captain': pick.get('is_captain'),
                'is_vice_captain': pick.get('is_vice_captain'),
            }
            line_vals.append(val)

        self.env['fpl.gameweek.pick.lines'].search([('gameweek_pick_id', '=', gw_pick.id)]).unlink()

        if line_vals:
            self.env['fpl.gameweek.pick.lines'].create(line_vals)
            # self._get_pick_formations(create_line_picks)

    @api.model
    def get_pick_formations(self, picks):
        lineup_gkp = []
        lineup_def = []
        lineup_mid = []
        lineup_fwd = []

        sub_elements = []

        lineups_element_mapping = {
            'GKP': lineup_gkp,
            'DEF': lineup_def,
            'MID': lineup_mid,
            'FWD': lineup_fwd,
        }

        for pick in picks:
            # Handle both recordset objects and dictionary data
            if hasattr(pick, 'position'):
                # This is a recordset object
                position = pick.position
                pick_id = pick.id
                plural_name_short = pick.element_type_id.plural_name_short
            else:
                # This is dictionary data from JavaScript
                position = pick['position']
                pick_id = pick['id']
                plural_name_short = pick['element_type_id']['plural_name_short']
            
            if position in [12, 13, 14, 15]:
                sub_elements.append(pick_id)
            
            for pos, elements in lineups_element_mapping.items():
                if position == 1 and plural_name_short == pos:
                    elements.append(pick_id)
                
                elif position in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11] and plural_name_short == pos:
                    elements.append(pick_id)

        return {
            'lineup_gkp': lineup_gkp,
            'lineup_def': lineup_def,
            'lineup_mid': lineup_mid,
            'lineup_fwd': lineup_fwd,
            'sub_elements': sub_elements,
        }