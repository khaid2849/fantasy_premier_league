import logging

from odoo import models, fields, api, _
from .fpl_api_mixin import FPLApiMixin
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FPLElements(models.Model, FPLApiMixin):
    _name = 'fpl.elements'
    _description = 'FPL Elements'

    element_id = fields.Integer(string=_('Element ID'))
    fpl_team_id = fields.Many2one('fpl.teams', string=_('FPL Team'))
    team_id = fields.Integer(string=_('Team ID'), related='fpl_team_id.team_id')
    team_code = fields.Char(string=_('Team Code'), related='fpl_team_id.code')
    can_transact = fields.Boolean(string=_('Can Transact'))
    can_select = fields.Boolean(string=_('Can Select'))
    chance_of_playing_next_round = fields.Char(string=_('Chance of Playing Next Round'))
    chance_of_playing_this_round = fields.Char(string=_('Chance of Playing This Round'))
    code = fields.Char(string=_('Code'))
    cost_change_event = fields.Float(string=_('Cost Change Event'))
    cost_change_event_fall = fields.Float(string=_('Cost Change Event Fall'))
    cost_change_start = fields.Float(string=_('Cost Change Start'))
    cost_change_start_fall = fields.Float(string=_('Cost Change Start Fall'))
    dreamteam_count = fields.Integer(string=_('Dreamteam Count'))
    element_type_id = fields.Many2one('fpl.element.types', string=_('Element Type'))
    plural_name = fields.Char(string=_('Plural Name'), related='element_type_id.plural_name')
    ep_next = fields.Char(string=_('EP Next'))
    ep_this = fields.Char(string=_('EP This'))
    event_points = fields.Float(string=_('Event Points'))
    first_name = fields.Char(string=_('First Name'))
    form = fields.Char(string=_('Form'))
    in_dreamteam = fields.Boolean(string=_('In Dreamteam'))
    news = fields.Char(string=_('News'))
    news_added = fields.Char(string=_('News Added'))    
    now_cost = fields.Float(string=_('Now Cost'))
    photo = fields.Binary(string=_('Photo'))
    points_per_game = fields.Float(string=_('Points Per Game'))
    removed = fields.Boolean(string=_('Removed'))
    second_name = fields.Char(string=_('Second Name'))
    selected_by_percent = fields.Char(string=_('Selected By Percent'))
    special = fields.Boolean(string=_('Special'))
    squad_number = fields.Char(string=_('Squad Number'))
    status = fields.Selection(
        [
            ('a', _('Available')), 
            ('u', _('Unavailable')),
            ('s', _('Suspended')),
            ('d', _('Doubtful')),
            ('i', _('Injured')),
            ('n', _('Not Available'))
        ], string=_('Status'))
    total_points = fields.Float(string=_('Total Points'))
    transfers_in = fields.Float(string=_('Transfers In'))
    transfers_in_event = fields.Float(string=_('Transfers In Event'))
    transfers_out = fields.Float(string=_('Transfers Out'))
    transfers_out_event = fields.Float(string=_('Transfers Out Event'))
    value_form = fields.Char(string=_('Value Form'))
    value_season = fields.Char(string=_('Value Season'))
    web_name = fields.Char(string=_('Web Name'))
    country_id = fields.Many2one('res.country', string=_('Country'))
    region = fields.Char(string=_('Region'))
    team_join_date = fields.Date(string=_('Team Join Date'))
    birth_date = fields.Date(string=_('Birth Date'))
    has_temporary_code = fields.Boolean(string=_('Has Temporary Code'))
    opta_code = fields.Char(string=_('Opta Code'))
    minutes = fields.Integer(string=_('Minutes'))
    goals_scored = fields.Integer(string=_('Goals Scored'))
    assists = fields.Integer(string=_('Assists'))
    clean_sheets = fields.Integer(string=_('Clean Sheets'))
    goals_conceded = fields.Integer(string=_('Goals Conceded'))
    own_goals = fields.Integer(string=_('Own Goals'))
    penalties_saved = fields.Integer(string=_('Penalties Saved'))
    penalties_missed = fields.Integer(string=_('Penalties Missed'))
    yellow_cards = fields.Integer(string=_('Yellow Cards'))
    red_cards = fields.Integer(string=_('Red Cards'))
    saves = fields.Integer(string=_('Saves'))
    bonus = fields.Integer(string=_('Bonus'))
    bps = fields.Integer(string=_('BPS'))
    influence = fields.Char(string=_('Influence'))
    creativity = fields.Char(string=_('Creativity'))
    threat = fields.Char(string=_('Threat'))
    ict_index = fields.Char(string=_('ICT Index'))
    clearances_blocks_interceptions = fields.Integer(string=_('Clearances Blocks Interceptions'))
    recoveries = fields.Integer(string=_('Recoveries'))
    tackles = fields.Integer(string=_('Tackles'))
    defensive_contribution = fields.Float(string=_('Defensive Contribution'))
    starts = fields.Integer(string=_('Starts'))
    expected_goals = fields.Char(string=_('Expected Goals'))
    expected_assists = fields.Char(string=_('Expected Assists'))
    expected_goal_involvements = fields.Char(string=_('Expected Goal Involvements'))
    expected_goals_conceded = fields.Char(string=_('Expected Goals Conceded'))
    influence_rank = fields.Integer(string=_('Influence Rank'))
    influence_rank_type = fields.Integer(string=_('Influence Rank Type'))
    creativity_rank = fields.Integer(string=_('Creativity Rank'))
    creativity_rank_type = fields.Integer(string=_('Creativity Rank Type'))
    threat_rank = fields.Integer(string=_('Threat Rank'))
    threat_rank_type = fields.Integer(string=_('Threat Rank Type'))
    ict_index_rank = fields.Integer(string=_('ICT Index Rank'))
    ict_index_rank_type = fields.Integer(string=_('ICT Index Rank Type'))
    corners_and_indirect_freekicks_order = fields.Char(string=_('Corners and Indirect Freekicks Order'))
    corners_and_indirect_freekicks_text = fields.Char(string=_('Corners and Indirect Freekicks Text'))
    direct_freekicks_order = fields.Char(string=_('Direct Freekicks Order'))
    direct_freekicks_text = fields.Char(string=_('Direct Freekicks Text'))
    penalties_order = fields.Char(string=_('Penalties Order'))
    penalties_text = fields.Char(string=_('Penalties Text'))
    expected_goals_per_90 = fields.Float(string=_('Expected Goals Per 90'))
    saves_per_90 = fields.Float(string=_('Saves Per 90'))
    expected_assists_per_90 = fields.Float(string=_('Expected Assists Per 90'))
    expected_goal_involvements_per_90 = fields.Float(string=_('Expected Goal Involvements Per 90'))
    expected_goals_conceded_per_90 = fields.Float(string=_('Expected Goals Conceded Per 90'))
    goals_conceded_per_90 = fields.Float(string=_('Goals Conceded Per 90'))
    now_cost_rank = fields.Integer(string=_('Now Cost Rank'))
    now_cost_rank_type = fields.Integer(string=_('Now Cost Rank Type'))
    form_rank = fields.Integer(string=_('Form Rank'))
    form_rank_type = fields.Integer(string=_('Form Rank Type'))
    points_per_game_rank = fields.Integer(string=_('Points Per Game Rank'))
    points_per_game_rank_type = fields.Integer(string=_('Points Per Game Rank Type'))
    selected_rank = fields.Integer(string=_('Selected Rank'))
    selected_rank_type = fields.Integer(string=_('Selected Rank Type'))
    starts_per_90 = fields.Float(string=_('Starts Per 90'))
    clean_sheets_per_90 = fields.Float(string=_('Clean Sheets Per 90'))
    defensive_contribution_per_90 = fields.Float(string=_('Defensive Contribution Per 90'))
    currency_id = fields.Many2one('res.currency', string=_('Currency'))
    display_name = fields.Char(string=_('Display Name'), compute='_compute_display_name')
    history_ids = fields.One2many('fpl.element.summary.history', 'element_id', string=_('History IDs'))
    history_past_ids = fields.One2many('fpl.element.summary.history.past', 'element_id', string=_('History Past IDs'))
    fixutres_ids = fields.One2many('fpl.element.summary.fixture', 'element_id', string=_('Fixutres IDs'))
    summary_name_form = fields.Html(compute='_compute_summary_name_form')
    
    # @api.model
    # def get_views(self, views, options=None):
    #     return super().get_view(views, options)

    @api.depends('first_name', 'second_name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.first_name} {rec.second_name}"

    @api.depends('fpl_team_id', 'web_name', 'plural_name')
    def _compute_summary_name_form(self):
        for rec in self:
            rec.summary_name_form = f'<b>{rec.web_name}</b> <br/><span style="color: #af99b1; font-size:11px">{rec.fpl_team_id.name} {rec.element_type_id.singular_name_short}</span>'
           
    def cron_get_data_element_summary(self):
        try:
            elements = self.search([('removed', '=', False)])
            for element in elements:
                element_summary = self.sync_from_fpl_api('get_element_summary', player_id=element.element_id)
                history = element_summary.get('history')
                history_past = element_summary.get('history_past')
                fixtures = element_summary.get('fixtures')

                self._sync_element_history_data(element, history)
                self._sync_element_history_past_data(element, history_past)
                self._sync_element_fixture_data(element, fixtures)

            _logger.info("Element summary data sync completed successfully")
            
        except Exception as e:
            _logger.error(f"Unexpected error during sync: {str(e)}")
            raise UserError(f"Unexpected error during sync: {str(e)}")

    
    def _sync_element_history_data(self, element, history):
        for history_item in history:
            fixture_id = self.env['fpl.gameweek.fixtures'].search([('gw_fixture_id', '=', history_item.get('fixture'))])
            element_history = self.env['fpl.element.summary.history'].search([('element_id', '=', element.id), ('fixture_id', '=', fixture_id.id)])

            history_item.update({
                'element_id': element.id,
                'fixture_id': fixture_id.id,
                'opponent_team': self.env['fpl.teams'].search([('team_id', '=', history_item.get('opponent_team'))]).id,
                'kickoff_time': fixture_id.kickoff_time,
                'is_modified': history_item.get('modified'),
                'value': history_item.get('value') / 10,
            })
            history_item.pop('element')
            history_item.pop('fixture')
            history_item.pop('modified')

            if element_history:
                element_history.write(history_item)
            else:
                self.env['fpl.element.summary.history'].create(history_item)
    
    def _sync_element_history_past_data(self, element, history_past):
        for past in history_past:
            element_history_past = self.env['fpl.element.summary.history.past'].search([('season_name', '=', past.get('season_name')),('element_id', '=', element.id), ('element_code', '=', past.get('element_code'))])
            past.update({
                'element_id': element.id,
                'element_code': past.get('element_code'),
                'start_cost': past.get('start_cost') / 10,
                'end_cost': past.get('end_cost') / 10,
            })
            
            if element_history_past:
                element_history_past.write(past)
            else:
                self.env['fpl.element.summary.history.past'].create(past)
    
    def _sync_element_fixture_data(self, element, fixtures):
        for fixture in fixtures:
            fixture_id = self.env['fpl.gameweek.fixtures'].search([('gw_fixture_id', '=', fixture.get('id'))])
            element_fixture = self.env['fpl.element.summary.fixture'].search(
                [
                    ('element_id', '=', element.id), 
                    ('fixture_id', '=', fixture_id.id),
                ]
            )

            fixture.update({
                'element_id': element.id,
                'fixture_id': fixture_id.id,
                'kickoff_time': fixture_id.kickoff_time,
                'event_name': fixture_id.event_id.name
            })
            fixture.pop('id')
            fixture.pop('event')

            if element_fixture:
                element_fixture.update(fixture)
            else:
                self.env['fpl.element.summary.fixture'].create(fixture)