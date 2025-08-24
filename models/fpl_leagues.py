import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .fpl_api_mixin import FPLApiMixin
from ..services.fpl_api_client import FPLApiException

_logger = logging.getLogger(__name__)

class FPLLeagues(models.Model, FPLApiMixin):
    _name = 'fpl.leagues'
    _description = 'FPL Leagues'

    type = fields.Selection([('classic', _('Classic')), ('h2h', _('H2H'))], string=_('League Type'))
    manager_id = fields.Many2one('fpl.manager.team', string=_('Manager ID'))
    league_id = fields.Integer(string=_('League ID'))
    name = fields.Char(string=_('Name'))
    short_name = fields.Char(string=_('Short Name'))
    created = fields.Datetime(string=_('Created'))
    closed = fields.Boolean(string=_('Closed'))
    max_entries = fields.Integer(string=_('Max Entries'))
    league_type = fields.Char(string=_('League Type'))
    scoring = fields.Char(string=_('Scoring'))
    admin_entry = fields.Integer(string=_('Admin Entry'))
    start_event = fields.Integer(string=_('Start Event'))
    entry_can_leave = fields.Boolean(string=_('Entry Can Leave'))
    entry_can_admin = fields.Boolean(string=_('Entry Can Admin'))
    entry_can_invite = fields.Boolean(string=_('Entry Can Invite'))
    has_cup = fields.Boolean(string=_('Has Cup'))
    cup_league = fields.Boolean(string=_('Cup League'))
    cup_qualified = fields.Boolean(string=_('Cup Qualified'))
    rank_count = fields.Integer(string=_('Rank Count'))
    entry_percentile_rank = fields.Integer(string=_('Entry Percentile Rank'))
    entry_rank = fields.Integer(string=_('Entry Rank'))
    entry_last_rank = fields.Integer(string=_('Entry Last Rank'))
    active_phases_ids = fields.One2many('fpl.league.active.phases', 'league_id', string=_('Active Phases'))
    overall_points = fields.Integer(string=_('Overall Points'), compute='_compute_overall_points')
    entry_rank_form = fields.Html(string=_('Current rank'), compute='_compute_entry_rank_form')
    standing_result_ids = fields.One2many('fpl.league.standings.results', 'league_id', string=_('Overall'))
    standing_result_august_ids = fields.One2many('fpl.league.standings.results', 'league_id', string=_('August'))
    standing_result_september_ids = fields.One2many('fpl.league.standings.results', 'league_id', string=_('September'))
    standing_result_october_ids = fields.One2many('fpl.league.standings.results', 'league_id', string=_('October'))
    standing_result_november_ids = fields.One2many('fpl.league.standings.results', 'league_id', string=_('November'))
    standing_result_december_ids = fields.One2many('fpl.league.standings.results', 'league_id', string=_('December'))
    standing_result_january_ids = fields.One2many('fpl.league.standings.results', 'league_id', string=_('January'))
    standing_result_february_ids = fields.One2many('fpl.league.standings.results', 'league_id', string=_('February'))
    standing_result_march_ids = fields.One2many('fpl.league.standings.results', 'league_id', string=_('March'))
    standing_result_april_ids = fields.One2many('fpl.league.standings.results', 'league_id', string=_('April'))
    standing_result_may_ids = fields.One2many('fpl.league.standings.results', 'league_id', string=_('May'))
    last_updated_data = fields.Datetime(string=_('Last updated'))

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


    @api.depends('active_phases_ids')
    def _compute_league_standing_phase(self):
        for rec in self:
            rec.is_august = True if any(phase.phase_id.name == 'August' for phase in rec.active_phases_ids) else False
            rec.is_september = True if any(phase.phase_id.name == 'September' for phase in rec.active_phases_ids) else False
            rec.is_october = True if any(phase.phase_id.name == 'October' for phase in rec.active_phases_ids) else False
            rec.is_november = True if any(phase.phase_id.name == 'November' for phase in rec.active_phases_ids) else False
            rec.is_december = True if any(phase.phase_id.name == 'December' for phase in rec.active_phases_ids) else False
            rec.is_january = True if any(phase.phase_id.name == 'January' for phase in rec.active_phases_ids) else False
            rec.is_february = True if any(phase.phase_id.name == 'February' for phase in rec.active_phases_ids) else False
            rec.is_march = True if any(phase.phase_id.name == 'March' for phase in rec.active_phases_ids) else False
            rec.is_april = True if any(phase.phase_id.name == 'April' for phase in rec.active_phases_ids) else False
            rec.is_may = True if any(phase.phase_id.name == 'May' for phase in rec.active_phases_ids) else False

    @api.depends('entry_last_rank', 'entry_rank')
    def _compute_entry_rank_form(self):
        for rec in self:
            if rec.entry_rank > rec.entry_last_rank:
                rec.entry_rank_form = f'<p><i class="fa fa-arrow-circle-down" style="color: #E60023"></i> {format(rec.entry_rank, ",")}</p>'
            elif rec.entry_rank < rec.entry_last_rank:
                rec.entry_rank_form = f'<p><i class="fa fa-arrow-circle-up" style="color: #34a853"></i> {format(rec.entry_rank, ",")}</p>'
            elif rec.entry_rank == rec.entry_last_rank:
                rec.entry_rank_form = f'<p><i class="fa fa-circle" style="color: #87668a"></i> {format(rec.entry_rank, ",")}</p>'

    @api.depends('active_phases_ids')
    def _compute_overall_points(self):
        for league in self:
            if league.active_phases_ids:
                league.overall_points = league.active_phases_ids.search([('phase_id', '=', 1)], limit=1).total
            else:
                league.overall_points = 0
    
    # def cron_get_data_league_standings(self):
    #     try:
            
                        
    #     except FPLApiException as e:
    #         _logger.error(f"FPL API error during league standings sync: {str(e)}")
    #         raise UserError(f"FPL API error during league standings sync: {str(e)}")
    #     except Exception as e:
    #         _logger.error(f"Unexpected error during sync: {str(e)}")
    #         raise UserError(f"Unexpected error during sync: {str(e)}")