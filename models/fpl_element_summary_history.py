from odoo import models, fields, api

class FPLElementSummaryHistory(models.Model):
    _name = 'fpl.element.summary.history'
    _description = 'FPL Element Summary History'

    element_id = fields.Many2one('fpl.elements', string='Element')
    fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Fixture')
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
    value = fields.Integer(string='Value')
    transfers_balance = fields.Integer(string='Transfers Balance')
    selected = fields.Integer(string='Selected')
    transfers_in = fields.Float(string='Transfers In')
    transfers_out = fields.Float(string='Transfers Out')
    currency_id = fields.Many2one('res.currency')
    opponent_team_display = fields.Html(string='Opponent', compute='_compute_opponent_team_display')

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
            if not rec.opponent_team:
                rec.opponent_team_display = False
                continue
            opponent_team_photo_src = f'/fantasy_premier_league/static/src/img/teams_logo/{rec.opponent_team.code}.svg'
            rec.opponent_team_display = f'<img src="{opponent_team_photo_src}" style="width: 18x; height: 20px; border-radius: 10px;"/> <span style="font-size: 9px;">{rec.opponent_team.short_name} ({home_away})</span> {result}'
    

class FPLElementSummaryHistoryPast(models.Model):
    _name = 'fpl.element.summary.history.past'
    _description = 'FPL Element Summary History Past'

    element_id = fields.Many2one('fpl.elements', string='Element')
    element_code = fields.Integer(string='Element Code')
    season_name = fields.Char(string='Season Name')
    start_cost = fields.Integer(string='Start Cost')
    end_cost = fields.Integer(string='End Cost')
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
    recoveries= fields.Integer(string='Recoveries')
    tackles = fields.Integer(string='Tackles')
    defensive_contribution = fields.Integer(string='Defensive Contribution')
    starts = fields.Integer(string='Starts')
    expected_goals = fields.Float(string='Expected Goals')
    expected_assists = fields.Float(string='Expected Assists')
    expected_goal_involvements = fields.Float(string='Expected Goal Involvements')
    expected_goals_conceded = fields.Float(string='Expected Goals Conceded')
    currency_id = fields.Many2one('res.currency')

class FplElementSummaryFixture(models.Model):
    _name = 'fpl.element.summary.fixture'
    _description = 'FPL Element Summary Fixture'

    element_id = fields.Many2one('fpl.elements')
    fixture_id = fields.Many2one('fpl.gameweek.fixtures')
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
    opponent_team_display = fields.Html(string='Opponent', compute='_compute_opponent_team_display')

    @api.depends('fixture_id.team_h', 'fixture_id.team_a')
    def _compute_opponent_team_display(self):
        for rec in self:
            team_a = rec.fixture_id.team_a
            team_h = rec.fixture_id.team_h
            home_away = 'H' if rec.is_home else 'A'
            opponent_team = team_h if rec.element_id.fpl_team_id != team_h else team_a

            if not opponent_team:
                rec.opponent_team_display = False
                continue
            opponent_team_photo_src = f'/fantasy_premier_league/static/src/img/teams_logo/{opponent_team.code}.svg'
            rec.opponent_team_display = f'<img src="{opponent_team_photo_src}" style="width: 18x; height: 20px; border-radius: 10px;"/> <span style="font-size: 10px;">{opponent_team.short_name} ({home_away})</span>'