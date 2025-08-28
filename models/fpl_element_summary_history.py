from odoo import models, fields, api, _

class FPLElementSummaryHistory(models.Model):
    _name = 'fpl.element.summary.history'
    _description = 'FPL Element Summary History'

    element_id = fields.Many2one('fpl.elements', string=_('Element'))
    fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Fixture'))
    opponent_team = fields.Many2one('fpl.teams', string=_('Opponent Team'))
    total_points = fields.Float(string=_('Total Points'))
    was_home = fields.Boolean(string=_('Was Home'))
    kickoff_time = fields.Datetime(string=_('Kickoff Time'))
    team_h_score = fields.Integer(string=_('Team H Score'))
    team_a_score = fields.Integer(string=_('Team A Score'))
    is_modified = fields.Boolean(string=_('Modified'))
    round = fields.Integer(string=_('Round'))
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
    expected_goals = fields.Float(string=_('Expected Goals'))
    expected_assists = fields.Float(string=_('Expected Assists'))
    expected_goal_involvements = fields.Float(string=_('Expected Goal Involvements'))
    expected_goals_conceded = fields.Float(string=_('Expected Goals Conceded'))
    value = fields.Integer(string=_('Value'))
    transfers_balance = fields.Integer(string=_('Transfers Balance'))
    selected = fields.Integer(string=_('Selected'))
    transfers_in = fields.Float(string=_('Transfers In'))
    transfers_out = fields.Float(string=_('Transfers Out'))
    currency_id = fields.Many2one('res.currency')
    opponent_team_display = fields.Html(string=_('Opponent'), compute='_compute_opponent_team_display')

    @api.depends('opponent_team')
    def _compute_opponent_team_display(self):
        for rec in self:
            team_a = rec.fixture_id.team_a
            team_h = rec.fixture_id.team_h
            home_away = 'H' if rec.was_home else 'A'
            result = ''
            win = '<span style="color: #fff; border-radius: 10px; padding: 2px 5px; background-color: #008000; font-size: 7px; font-weight: bold;">W</span>'
            lose = '<span style="color: #fff; border-radius: 10px; padding: 2px 5px; background-color: #ff0000; font-size: 7px; font-weight: bold;">L</span>'
            draw = '<span style="color: #fff; border-radius: 10px; padding: 2px 5px; background-color: #808080; font-size: 7px; font-weight: bold;">D</span>'
            if rec.element_id.fpl_team_id == team_h:
                if rec.team_h_score > rec.team_a_score:
                    result = win
                elif rec.team_h_score < rec.team_a_score:
                    result = lose
                else:
                    result = draw
            elif rec.element_id.fpl_team_id == team_a: 
                if rec.team_a_score > rec.team_h_score:
                    result = win
                elif rec.team_a_score < rec.team_h_score:
                    result = lose
                else:
                    result = draw

            rec.opponent_team_display = f'<img src="{rec.opponent_team.photo}" style="width: 18x; height: 20px; border-radius: 10px;"/> <span style="font-size: 10px;">{rec.opponent_team.short_name + " " + f"({home_away})"}</span> {result}'
    

class FPLElementSummaryHistoryPast(models.Model):
    _name = 'fpl.element.summary.history.past'
    _description = 'FPL Element Summary History Past'

    element_id = fields.Many2one('fpl.elements', string=_('Element'))
    element_code = fields.Integer(string=_('Element Code'))
    season_name = fields.Char(string=_('Season Name'))
    start_cost = fields.Integer(string=_('Start Cost'))
    end_cost = fields.Integer(string=_('End Cost'))
    total_points = fields.Integer(string=_('Total Points'))
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
    influence = fields.Float(string=_('Influence'))
    creativity = fields.Float(string=_('Creativity'))
    threat = fields.Float(string=_('Threat'))
    ict_index = fields.Float(string=_('ICT Index'))
    clearances_blocks_interceptions = fields.Integer(string=_('Clearances Blocks Interceptions'))
    recoveries= fields.Integer(string=_('Recoveries'))
    tackles = fields.Integer(string=_('Tackles'))
    defensive_contribution = fields.Integer(string=_('Defensive Contribution'))
    starts = fields.Integer(string=_('Starts'))
    expected_goals = fields.Float(string=_('Expected Goals'))
    expected_assists = fields.Float(string=_('Expected Assists'))
    expected_goal_involvements = fields.Float(string=_('Expected Goal Involvements'))
    expected_goals_conceded = fields.Float(string=_('Expected Goals Conceded'))
    currency_id = fields.Many2one('res.currency')

class FplElementSummaryFixture(models.Model):
    _name = 'fpl.element.summary.fixture'

    element_id = fields.Many2one('fpl.elements')
    fixture_id = fields.Many2one('fpl.gameweek.fixtures')
    code = fields.Integer(string=_('Code'))
    team_h = fields.Many2one('fpl.teams')
    team_h_score = fields.Integer()
    team_a = fields.Many2one('fpl.teams')
    team_a_score = fields.Integer()
    event_id = fields.Many2one('fpl.events')
    finished = fields.Boolean()
    minutes = fields.Integer()
    provisional_start_time = fields.Boolean()
    kickoff_time = fields.Datetime()
    is_home = fields.Boolean()
    difficulty = fields.Integer()
    event_name = fields.Char(string=_('Event Name'))
    gameweek = fields.Integer(string=_('Gameweek'), related='fixture_id.gameweek')
    opponent_team_display = fields.Html(string=_('Opponent'), compute='_compute_opponent_team_display')

    @api.depends('fixture_id.team_h', 'fixture_id.team_a')
    def _compute_opponent_team_display(self):
        for rec in self:
            team_a = rec.fixture_id.team_a
            team_h = rec.fixture_id.team_h
            home_away = 'H' if rec.is_home else 'A'
            opponent_team = team_h if rec.is_home else team_a

            rec.opponent_team_display = f'<img src="{opponent_team.photo}" style="width: 18x; height: 20px; border-radius: 10px;"/> <span style="font-size: 10px;">{opponent_team.short_name + " " + f"({home_away})"}</span>'

    "id": 23,
            "code": 2561917,
            "team_h": 7,
            "team_h_score": null,
            "team_a": 10,
            "team_a_score": null,
            "event": 3,
            "finished": false,
            "minutes": 0,
            "provisional_start_time": false,
            "kickoff_time": "2025-08-30T11:30:00Z",
            "event_name": "Gameweek 3",
            "is_home": true,
            "difficulty": 3
        }