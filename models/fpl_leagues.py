from markupsafe import Markup

from odoo import api, fields, models

from .fpl_phases import OVERALL_PHASE_ID

# FPL phase id -> (league field suffix, phase name); phase 1 is the overall standing
MONTH_PHASES = {
    2: 'august', 3: 'september', 4: 'october', 5: 'november', 6: 'december',
    7: 'january', 8: 'february', 9: 'march', 10: 'april', 11: 'may',
}


def rank_form_html(rank, last_rank):
    """Rank with an up/down/same arrow, as shown on the FPL website."""
    if rank > last_rank:
        icon, color = 'fa-arrow-circle-down', '#E60023'
    elif rank < last_rank:
        icon, color = 'fa-arrow-circle-up', '#34a853'
    else:
        icon, color = 'fa-circle', '#87668a'
    return Markup('<p><i class="fa %s" style="color: %s"></i> %s</p>') % (icon, color, format(rank or 0, ','))


def _standing_o2m(phase_id, string):
    return fields.One2many(
        'fpl.league.standings.results', 'league_id', string=string, readonly=True,
        domain=[('phase_id.phase_id', '=', phase_id)],
    )


class FPLLeagues(models.Model):
    _name = 'fpl.leagues'
    _description = 'FPL Leagues'
    _order = 'type, league_id'

    type = fields.Selection([('classic', 'Classic'), ('h2h', 'H2H')], string='League Type')
    manager_id = fields.Many2one('fpl.manager.team', string='Manager ID', index=True, ondelete='cascade')
    league_id = fields.Integer(string='League ID', index=True)
    name = fields.Char(string='Name')
    short_name = fields.Char(string='Short Name')
    created = fields.Datetime(string='Created')
    closed = fields.Boolean(string='Closed')
    max_entries = fields.Integer(string='Max Entries')
    league_type = fields.Char(string='League Type')
    scoring = fields.Char(string='Scoring')
    admin_entry = fields.Integer(string='Admin Entry')
    start_event = fields.Integer(string='Start Event')
    entry_can_leave = fields.Boolean(string='Entry Can Leave')
    entry_can_admin = fields.Boolean(string='Entry Can Admin')
    entry_can_invite = fields.Boolean(string='Entry Can Invite')
    has_cup = fields.Boolean(string='Has Cup')
    cup_league = fields.Boolean(string='Cup League')
    cup_qualified = fields.Boolean(string='Cup Qualified')
    rank_count = fields.Integer(string='Rank Count')
    entry_percentile_rank = fields.Integer(string='Entry Percentile Rank')
    entry_rank = fields.Integer(string='Entry Rank')
    entry_last_rank = fields.Integer(string='Entry Last Rank')
    active_phases_ids = fields.One2many('fpl.league.active.phases', 'league_id', string='Active Phases')
    overall_points = fields.Integer(string='Overall Points', compute='_compute_overall_points')
    entry_rank_form = fields.Html(string='Current rank', compute='_compute_entry_rank_form', sanitize=False)
    standing_result_ids = _standing_o2m(OVERALL_PHASE_ID, 'Overall')
    standing_result_august_ids = _standing_o2m(2, 'August')
    standing_result_september_ids = _standing_o2m(3, 'September')
    standing_result_october_ids = _standing_o2m(4, 'October')
    standing_result_november_ids = _standing_o2m(5, 'November')
    standing_result_december_ids = _standing_o2m(6, 'December')
    standing_result_january_ids = _standing_o2m(7, 'January')
    standing_result_february_ids = _standing_o2m(8, 'February')
    standing_result_march_ids = _standing_o2m(9, 'March')
    standing_result_april_ids = _standing_o2m(10, 'April')
    standing_result_may_ids = _standing_o2m(11, 'May')
    last_updated_data = fields.Datetime(string='Last updated')

    is_august = fields.Boolean(compute='_compute_league_standing_phase')
    is_september = fields.Boolean(compute='_compute_league_standing_phase')
    is_october = fields.Boolean(compute='_compute_league_standing_phase')
    is_november = fields.Boolean(compute='_compute_league_standing_phase')
    is_december = fields.Boolean(compute='_compute_league_standing_phase')
    is_january = fields.Boolean(compute='_compute_league_standing_phase')
    is_february = fields.Boolean(compute='_compute_league_standing_phase')
    is_march = fields.Boolean(compute='_compute_league_standing_phase')
    is_april = fields.Boolean(compute='_compute_league_standing_phase')
    is_may = fields.Boolean(compute='_compute_league_standing_phase')

    _sql_constraints = [
        ('manager_league_uniq', 'unique(manager_id, type, league_id)', 'This league is already linked to the manager.'),
    ]

    @api.depends('active_phases_ids.phase_id.phase_id')
    def _compute_league_standing_phase(self):
        for rec in self:
            active = set(rec.active_phases_ids.phase_id.mapped('phase_id'))
            for phase_id, month in MONTH_PHASES.items():
                rec[f'is_{month}'] = phase_id in active

    @api.depends('entry_last_rank', 'entry_rank')
    def _compute_entry_rank_form(self):
        for rec in self:
            rec.entry_rank_form = rank_form_html(rec.entry_rank, rec.entry_last_rank)

    @api.depends('active_phases_ids.total', 'active_phases_ids.phase_id.phase_id')
    def _compute_overall_points(self):
        for league in self:
            overall = league.active_phases_ids.filtered(lambda phase: phase.phase_id.phase_id == OVERALL_PHASE_ID)
            league.overall_points = overall[:1].total
