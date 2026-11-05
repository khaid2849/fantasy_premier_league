from markupsafe import Markup

from odoo import api, fields, models

RESULT_BADGE = Markup(
    '<span style="color: #fff; border-radius: 10px; padding: 2px 5px; background-color: %s; '
    'font-size: 7px; font-weight: bold;">%s</span>'
)
RESULT_COLORS = {'W': '#008000', 'L': '#ff0000', 'D': '#808080'}


def _opponent_html(team, home_away, font_size, suffix=''):
    return Markup(
        '<img src="%s" style="width: 20px; height: 20px; border-radius: 10px;"/> '
        '<span style="font-size: %spx;">%s (%s)</span> %s'
    ) % (team._logo_url(), font_size, team.short_name or '', home_away, suffix)


class FPLElementSummaryHistory(models.Model):
    _name = 'fpl.element.summary.history'
    _description = 'FPL Element Summary History'
    _order = 'round desc, kickoff_time desc'

    element_id = fields.Many2one('fpl.elements', string='Element', required=True, index=True, ondelete='cascade')
    fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Fixture', index=True, ondelete='cascade')
    opponent_team = fields.Many2one('fpl.teams', string='Opponent Team')
    total_points = fields.Float(string='Total Points')
    was_home = fields.Boolean(string='Was Home')
    kickoff_time = fields.Datetime(string='Kickoff Time')
    team_h_score = fields.Integer(string='Team H Score')
    team_a_score = fields.Integer(string='Team A Score')
    is_modified = fields.Boolean(string='Modified')
    round = fields.Integer(string='Round')
    minutes = fields.Integer(string='Minutes')
    goals_scored = fields.Integer(string='Goals Scored')
    assists = fields.Integer(string='Assists')
    clean_sheets = fields.Integer(string='Clean Sheets')
    goals_conceded = fields.Integer(string='Goals Conceded')
    own_goals = fields.Integer(string='Own Goals')
    penalties_saved = fields.Integer(string='Penalties Saved')
    penalties_missed = fields.Integer(string='Penalties Missed')
    yellow_cards = fields.Integer(string='Yellow Cards')
    red_cards = fields.Integer(string='Red Cards')
    saves = fields.Integer(string='Saves')
    bonus = fields.Integer(string='Bonus')
    bps = fields.Integer(string='BPS')
    influence = fields.Float(string='Influence')
    creativity = fields.Float(string='Creativity')
    threat = fields.Float(string='Threat')
    ict_index = fields.Float(string='ICT Index')
    clearances_blocks_interceptions = fields.Integer(string='Clearances Blocks Interceptions')
    recoveries = fields.Integer(string='Recoveries')
    tackles = fields.Integer(string='Tackles')
    defensive_contribution = fields.Float(string='Defensive Contribution')
    starts = fields.Integer(string='Starts')
    expected_goals = fields.Float(string='Expected Goals')
    expected_assists = fields.Float(string='Expected Assists')
    expected_goal_involvements = fields.Float(string='Expected Goal Involvements')
    expected_goals_conceded = fields.Float(string='Expected Goals Conceded')
    value = fields.Float(string='Value')
    transfers_balance = fields.Integer(string='Transfers Balance')
    selected = fields.Integer(string='Selected')
    transfers_in = fields.Float(string='Transfers In')
    transfers_out = fields.Float(string='Transfers Out')
    currency_id = fields.Many2one('res.currency')
    opponent_team_display = fields.Html(string='Opponent', compute='_compute_opponent_team_display', sanitize=False)

    _sql_constraints = [
        ('element_fixture_uniq', 'unique(element_id, fixture_id)',
         'A player can only have one history line per fixture.'),
    ]

    def _get_summary_key(self):
        return self.fixture_id.id

    @api.depends('opponent_team', 'was_home', 'team_h_score', 'team_a_score')
    def _compute_opponent_team_display(self):
        for rec in self:
            if not rec.opponent_team:
                rec.opponent_team_display = False
                continue
            own, other = (rec.team_h_score, rec.team_a_score) if rec.was_home else (rec.team_a_score, rec.team_h_score)
            result = 'W' if own > other else ('L' if own < other else 'D')
            badge = RESULT_BADGE % (RESULT_COLORS[result], result)
            rec.opponent_team_display = _opponent_html(rec.opponent_team, 'H' if rec.was_home else 'A', 9, badge)


class FPLElementSummaryHistoryPast(models.Model):
    _name = 'fpl.element.summary.history.past'
    _description = 'FPL Element Summary History Past'
    _order = 'season_name desc'

    element_id = fields.Many2one('fpl.elements', string='Element', required=True, index=True, ondelete='cascade')
    element_code = fields.Integer(string='Element Code')
    season_name = fields.Char(string='Season Name')
    start_cost = fields.Float(string='Start Cost')
    end_cost = fields.Float(string='End Cost')
    total_points = fields.Integer(string='Total Points')
    minutes = fields.Integer(string='Minutes')
    goals_scored = fields.Integer(string='Goals Scored')
    assists = fields.Integer(string='Assists')
    clean_sheets = fields.Integer(string='Clean Sheets')
    goals_conceded = fields.Integer(string='Goals Conceded')
    own_goals = fields.Integer(string='Own Goals')
    penalties_saved = fields.Integer(string='Penalties Saved')
    penalties_missed = fields.Integer(string='Penalties Missed')
    yellow_cards = fields.Integer(string='Yellow Cards')
    red_cards = fields.Integer(string='Red Cards')
    saves = fields.Integer(string='Saves')
    bonus = fields.Integer(string='Bonus')
    bps = fields.Integer(string='BPS')
    influence = fields.Float(string='Influence')
    creativity = fields.Float(string='Creativity')
    threat = fields.Float(string='Threat')
    ict_index = fields.Float(string='ICT Index')
    clearances_blocks_interceptions = fields.Integer(string='Clearances Blocks Interceptions')
    recoveries = fields.Integer(string='Recoveries')
    tackles = fields.Integer(string='Tackles')
    defensive_contribution = fields.Integer(string='Defensive Contribution')
    starts = fields.Integer(string='Starts')
    expected_goals = fields.Float(string='Expected Goals')
    expected_assists = fields.Float(string='Expected Assists')
    expected_goal_involvements = fields.Float(string='Expected Goal Involvements')
    expected_goals_conceded = fields.Float(string='Expected Goals Conceded')
    currency_id = fields.Many2one('res.currency')

    _sql_constraints = [
        ('element_season_uniq', 'unique(element_id, season_name)',
         'A player can only have one line per past season.'),
    ]

    def _get_summary_key(self):
        return self.season_name


class FplElementSummaryFixture(models.Model):
    _name = 'fpl.element.summary.fixture'
    _description = 'FPL Element Summary Fixture'
    _order = 'kickoff_time, id'

    element_id = fields.Many2one('fpl.elements', required=True, index=True, ondelete='cascade')
    fixture_id = fields.Many2one('fpl.gameweek.fixtures', index=True, ondelete='cascade')
    code = fields.Integer(string='Code')
    team_h = fields.Many2one('fpl.teams')
    team_h_score = fields.Integer()
    team_a = fields.Many2one('fpl.teams')
    team_a_score = fields.Integer()
    event_id = fields.Many2one('fpl.events', index=True)
    season = fields.Char(string='Season', related='event_id.season', store=True, index=True)
    finished = fields.Boolean()
    minutes = fields.Integer()
    provisional_start_time = fields.Boolean()
    kickoff_time = fields.Datetime()
    is_home = fields.Boolean()
    difficulty = fields.Integer()
    event_name = fields.Char(string='Event Name')
    gameweek = fields.Integer(string='Gameweek', related='fixture_id.gameweek')
    opponent_team_display = fields.Html(string='Opponent', compute='_compute_opponent_team_display', sanitize=False)

    _sql_constraints = [
        ('element_fixture_uniq', 'unique(element_id, fixture_id)',
         'A player can only have one line per upcoming fixture.'),
    ]

    def _get_summary_key(self):
        return self.fixture_id.id

    @api.depends('is_home', 'team_h', 'team_a')
    def _compute_opponent_team_display(self):
        for rec in self:
            opponent = rec.team_a if rec.is_home else rec.team_h
            rec.opponent_team_display = _opponent_html(opponent, 'H' if rec.is_home else 'A', 10) if opponent else False
