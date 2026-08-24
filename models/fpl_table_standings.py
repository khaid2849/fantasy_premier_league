import logging
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from .fpl_api_mixin import FPLApiMixin
from ..services.fpl_pulse_api_client import FPLPulseLiveApiException

_logger = logging.getLogger(__name__)

RESULT_SELECTION = [('W', _('Win')), ('D', _('Draw')), ('L', _('Loss'))]


class FplTableStandings(models.Model, FPLApiMixin):
    _name = 'fpl.table.standings'
    _description = 'FPL Live Table Standings (Premier League source)'
    _order = 'position asc'

    team_id = fields.Many2one('fpl.teams', string=_('Team'), required=True, index=True, ondelete='cascade')
    team_code = fields.Char(related='team_id.code', string=_('Team Code'), store=True)
    season = fields.Char(string=_('Season'))

    position = fields.Integer(string=_('Position'))
    starting_position = fields.Integer(string=_('Starting Position'))
    played = fields.Integer(string=_('Played'))
    won = fields.Integer(string=_('Won'))
    drawn = fields.Integer(string=_('Drawn'))
    lost = fields.Integer(string=_('Lost'))
    goals_for = fields.Integer(string=_('Goals For'))
    goals_against = fields.Integer(string=_('Goals Against'))
    goal_difference = fields.Integer(string=_('Goal Difference'), compute='_compute_goal_difference', store=True)
    points = fields.Integer(string=_('Points'))

    record_ids = fields.One2many('fpl.table.standings.record', 'standings_id', string=_('Home / Away Breakdown'))
    form_ids = fields.One2many('fpl.table.standings.form', 'standings_id', string=_('Form'))

    next_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Next Fixture'))
    next_opponent_id = fields.Many2one('fpl.teams', string=_('Next Opponent'))
    next_opponent_code = fields.Char(related='next_opponent_id.code', string=_('Next Opponent Code'), store=True)
    next_kickoff_time = fields.Datetime(string=_('Next Kickoff'))
    next_is_home = fields.Boolean(string=_('Next Match at Home'))

    last_synced = fields.Datetime(string=_('Last Synced'))

    _sql_constraints = [
        ('team_id_uniq', 'unique(team_id)',
         'A standings row already exists for this team.'),
    ]

    @api.depends('goals_for', 'goals_against')
    def _compute_goal_difference(self):
        for rec in self:
            rec.goal_difference = rec.goals_for - rec.goals_against

    @api.model
    def action_sync_standings(self):
        """Refresh the whole table from the Premier League pulselive API.

        Called from the "Table Standings" menu/list controller on every
        open so the data is always current, since fpl.teams's own
        standings fields are no longer kept up to date by the FPL API sync.
        """
        season = self._get_current_pulse_season()
        if not season:
            raise UserError(_("No FPL event/season found. Sync the FPL bootstrap data first."))

        try:
            standings_response = self.sync_from_pulse_live_api('get_standings', season)
            form_response = self.sync_from_pulse_live_api('get_team_form', season)
        except FPLPulseLiveApiException as e:
            _logger.error(f"Pulse Live API error during table standings sync: {str(e)}")
            raise UserError(_("Failed to fetch live standings: %s") % str(e))

        teams_by_code = self._get_teams_by_code()
        entries = (standings_response.get('tables') or [{}])[0].get('entries') or []
        form_by_code = {str(item.get('id')): item for item in (form_response or [])}

        match_ids = self._collect_match_ids(form_by_code)
        fixtures_by_code = self._get_fixtures_by_code(match_ids)

        now = fields.Datetime.now()
        for entry in entries:
            self._sync_standings_entry(entry, season, teams_by_code, form_by_code, fixtures_by_code, now)

        return True

    @api.model
    def _get_current_pulse_season(self):
        """Season used in the Pulse Live API URL, e.g. '2026' for '2026/2027'."""
        current_event = self.env['fpl.events'].search([], order='season desc', limit=1)
        if not current_event or not current_event.season:
            return False
        return current_event.season.split('/')[0]

    @api.model
    def _get_teams_by_code(self):
        teams = self.env['fpl.teams'].search([])
        return {team.code: team for team in teams if team.code}

    @api.model
    def _collect_match_ids(self, form_by_code):
        """All Pulse matchIds referenced by any team's form/next, in one pass,
        so fixtures can be prefetched with a single search instead of one
        search per match (avoids an N+1 query pattern)."""
        match_ids = set()
        for form_item in form_by_code.values():
            next_match = form_item.get('next') or {}
            if next_match.get('matchId'):
                match_ids.add(next_match['matchId'])
            for form_match in (form_item.get('form') or [])[-5:]:
                if form_match.get('matchId'):
                    match_ids.add(form_match['matchId'])
        return match_ids

    @api.model
    def _get_fixtures_by_code(self, match_ids):
        if not match_ids:
            return {}
        codes = [int(mid) for mid in match_ids if str(mid).isdigit()]
        fixtures = self.env['fpl.gameweek.fixtures'].search([('code', 'in', codes)])
        return {fixture.code: fixture for fixture in fixtures}

    def _sync_standings_entry(self, entry, season, teams_by_code, form_by_code, fixtures_by_code, now):
        team_info = entry.get('team') or {}
        team_code = str(team_info.get('id') or '')
        team = teams_by_code.get(team_code)
        if not team:
            _logger.warning(
                f"Table Standings sync: no fpl.teams match for Pulse team "
                f"'{team_info.get('name')}' (code {team_code!r}) - skipped."
            )
            return

        overall = entry.get('overall') or {}
        vals = {
            'team_id': team.id,
            'season': season,
            'position': overall.get('position'),
            'starting_position': overall.get('startingPosition'),
            'played': overall.get('played', 0),
            'won': overall.get('won', 0),
            'drawn': overall.get('drawn', 0),
            'lost': overall.get('lost', 0),
            'goals_for': overall.get('goalsFor', 0),
            'goals_against': overall.get('goalsAgainst', 0),
            'points': overall.get('points', 0),
            'last_synced': now,
        }

        form_item = form_by_code.get(team_code)
        if form_item:
            vals.update(self._get_next_fixture_vals(form_item, team, fixtures_by_code))

        standings = self.search([('team_id', '=', team.id)], limit=1)
        if standings:
            standings.write(vals)
        else:
            standings = self.create(vals)

        self._sync_record_breakdown(standings, entry)
        if form_item:
            self._sync_form_lines(standings, form_item, team, fixtures_by_code)

    def _get_next_fixture_vals(self, form_item, team, fixtures_by_code):
        next_match = form_item.get('next') or {}
        match_id = next_match.get('matchId')
        code = int(match_id) if match_id and str(match_id).isdigit() else False
        fixture = fixtures_by_code.get(str(code)) if code else False

        home_team = next_match.get('homeTeam') or {}
        away_team = next_match.get('awayTeam') or {}
        is_home = str(home_team.get('id')) == str(team.code)
        opponent_info = away_team if is_home else home_team

        opponent = False
        if fixture:
            opponent = fixture.team_a if fixture.team_h.id == team.id else fixture.team_h
        if not opponent and opponent_info.get('id'):
            opponent = self.env['fpl.teams'].search([('code', '=', str(opponent_info['id']))], limit=1)

        return {
            'next_fixture_id': fixture.id if fixture else False,
            'next_opponent_id': opponent.id if opponent else False,
            'next_kickoff_time': self._parse_pulse_datetime(next_match.get('kickoff')),
            'next_is_home': is_home,
        }

    def _sync_record_breakdown(self, standings, entry):
        record_model = self.env['fpl.table.standings.record']
        record_model.search([('standings_id', '=', standings.id)]).unlink()
        for record_type in ('home', 'away'):
            data = entry.get(record_type) or {}
            record_model.create({
                'standings_id': standings.id,
                'record_type': record_type,
                'played': data.get('played', 0),
                'won': data.get('won', 0),
                'drawn': data.get('drawn', 0),
                'lost': data.get('lost', 0),
                'goals_for': data.get('goalsFor', 0),
                'goals_against': data.get('goalsAgainst', 0),
                'points': data.get('points', 0),
            })

    def _sync_form_lines(self, standings, form_item, team, fixtures_by_code):
        form_model = self.env['fpl.table.standings.form']
        form_model.search([('standings_id', '=', standings.id)]).unlink()

        team_code = str(team.code)
        recent_matches = sorted(
            (form_item.get('form') or [])[-5:],
            key=lambda m: m.get('kickoff') or '',
        )

        for sequence, match in enumerate(recent_matches, start=1):
            home_team = match.get('homeTeam') or {}
            away_team = match.get('awayTeam') or {}
            is_home = str(home_team.get('id')) == team_code
            own_score = home_team.get('score') if is_home else away_team.get('score')
            opponent_score = away_team.get('score') if is_home else home_team.get('score')
            opponent_info = away_team if is_home else home_team

            if own_score is None or opponent_score is None:
                continue
            result = 'W' if own_score > opponent_score else ('L' if own_score < opponent_score else 'D')

            match_id = match.get('matchId')
            code = int(match_id) if match_id and str(match_id).isdigit() else False
            fixture = fixtures_by_code.get(str(code)) if code else False

            opponent = False
            if opponent_info.get('id'):
                opponent = self.env['fpl.teams'].search([('code', '=', str(opponent_info['id']))], limit=1)

            form_model.create({
                'standings_id': standings.id,
                'sequence': sequence,
                'result': result,
                'fixture_id': fixture.id if fixture else False,
                'opponent_id': opponent.id if opponent else False,
                'match_date': self._parse_pulse_datetime(match.get('kickoff')),
            })

    @api.model
    def _parse_pulse_datetime(self, value):
        if not value:
            return False
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return False


class FplTableStandingsRecord(models.Model):
    _name = 'fpl.table.standings.record'
    _description = 'FPL Table Standings Home/Away Breakdown'

    standings_id = fields.Many2one('fpl.table.standings', string=_('Standings'), required=True, ondelete='cascade')
    record_type = fields.Selection([('home', _('Home')), ('away', _('Away'))], string=_('Record Type'), required=True)
    played = fields.Integer(string=_('Played'))
    won = fields.Integer(string=_('Won'))
    drawn = fields.Integer(string=_('Drawn'))
    lost = fields.Integer(string=_('Lost'))
    goals_for = fields.Integer(string=_('Goals For'))
    goals_against = fields.Integer(string=_('Goals Against'))
    points = fields.Integer(string=_('Points'))


class FplTableStandingsForm(models.Model):
    _name = 'fpl.table.standings.form'
    _description = 'FPL Table Standings Recent Form'
    _order = 'sequence asc'

    standings_id = fields.Many2one('fpl.table.standings', string=_('Standings'), required=True, ondelete='cascade')
    sequence = fields.Integer(string=_('Sequence'))
    result = fields.Selection(RESULT_SELECTION, string=_('Result'))
    fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Fixture'))
    opponent_id = fields.Many2one('fpl.teams', string=_('Opponent'))
    match_date = fields.Datetime(string=_('Match Date'))
