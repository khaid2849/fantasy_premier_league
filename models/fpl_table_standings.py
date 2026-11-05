import logging
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..services.fpl_api_client import fetch_many

_logger = logging.getLogger(__name__)

RESULT_SELECTION = [('W', 'Win'), ('D', 'Draw'), ('L', 'Loss')]
# The list view syncs on every open; skip the API calls if the data is fresher than that
SYNC_THROTTLE = timedelta(seconds=60)
FORM_LENGTH = 5


class FplTableStandings(models.Model):
    _name = 'fpl.table.standings'
    _inherit = ['fpl.api.mixin']
    _description = 'FPL Live Table Standings (Premier League source)'
    _order = 'position asc'

    team_id = fields.Many2one('fpl.teams', string='Team', required=True, index=True, ondelete='cascade')
    team_code = fields.Char(related='team_id.code', string='Team Code', store=True)
    season = fields.Char(string='Season')

    position = fields.Integer(string='Position')
    starting_position = fields.Integer(string='Starting Position')
    played = fields.Integer(string='Played')
    won = fields.Integer(string='Won')
    drawn = fields.Integer(string='Drawn')
    lost = fields.Integer(string='Lost')
    goals_for = fields.Integer(string='Goals For')
    goals_against = fields.Integer(string='Goals Against')
    goal_difference = fields.Integer(string='Goal Difference', compute='_compute_goal_difference', store=True)
    points = fields.Integer(string='Points')

    record_ids = fields.One2many('fpl.table.standings.record', 'standings_id', string='Home / Away Breakdown')
    form_ids = fields.One2many('fpl.table.standings.form', 'standings_id', string='Form')

    next_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Next Fixture')
    next_opponent_id = fields.Many2one('fpl.teams', string='Next Opponent')
    next_opponent_code = fields.Char(related='next_opponent_id.code', string='Next Opponent Code', store=True)
    next_kickoff_time = fields.Datetime(string='Next Kickoff')
    next_is_home = fields.Boolean(string='Next Match at Home')

    last_synced = fields.Datetime(string='Last Synced')

    _sql_constraints = [
        ('team_id_uniq', 'unique(team_id)',
         'A standings row already exists for this team.'),
    ]

    @api.depends('goals_for', 'goals_against')
    def _compute_goal_difference(self):
        for rec in self:
            rec.goal_difference = rec.goals_for - rec.goals_against

    @api.model
    def action_sync_standings(self, force=False):
        """Refresh the whole table from the Premier League pulselive API.

        Called by the "League Standings" list view on every open (fpl.teams's
        own standings fields are no longer kept up to date by the FPL API),
        throttled to one refresh per ``SYNC_THROTTLE``.
        """
        if not force:
            last_synced = self.search([], order='last_synced desc', limit=1).last_synced
            if last_synced and fields.Datetime.now() - last_synced < SYNC_THROTTLE:
                return False

        season = self._get_current_pulse_season()
        if not season:
            raise UserError(_("No FPL event/season found. Sync the FPL bootstrap data first."))

        results, errors = fetch_many({
            'standings': lambda: self.sync_from_pulse_live_api('get_standings', season),
            'form': lambda: self.sync_from_pulse_live_api('get_team_form', season),
        }, max_workers=2)
        if 'standings' in errors:
            raise self._fpl_user_error(_("Failed to fetch live standings"), errors['standings'])
        if 'form' in errors:
            _logger.warning("Pulse Live team form unavailable: %s", errors['form'])

        entries = ((results['standings'] or {}).get('tables') or [{}])[0].get('entries') or []
        form_by_code = {str(item.get('id')): item for item in (results.get('form') or [])}
        self._sync_standings(entries, form_by_code, season)
        return True

    @api.model
    def _get_current_pulse_season(self):
        """Season used in the Pulse Live API URL, e.g. '2026' for '2026/2027'."""
        season = self.env['fpl.events']._get_current_season()
        return season.split('/')[0] if season else False

    @api.model
    def _sync_standings(self, entries, form_by_code, season):
        teams_by_code = self.env['fpl.teams']._get_teams_by_code()
        match_codes = {
            str(match['matchId'])
            for item in form_by_code.values()
            for match in [item.get('next') or {}] + (item.get('form') or [])[-FORM_LENGTH:]
            if match.get('matchId')
        }
        fixtures_by_code = {
            fixture.code: fixture
            for fixture in self.env['fpl.gameweek.fixtures'].search([('code', 'in', list(match_codes))])
        }

        existing = {row.team_id.id: row for row in self.search([])}
        now = fields.Datetime.now()
        vals_by_key, details = {}, {}
        for entry in entries:
            team_info = entry.get('team') or {}
            team_code = str(team_info.get('id') or '')
            team = teams_by_code.get(team_code)
            if not team:
                _logger.warning("Table Standings sync: no fpl.teams match for Pulse team %r (code %r) - skipped.",
                                team_info.get('name'), team_code)
                continue
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
                vals.update(self._get_next_fixture_vals(form_item, team, teams_by_code, fixtures_by_code))
            vals_by_key[team.id] = vals
            details[team.id] = (entry, form_item, team)

        # Relegated clubs are separate (archived) records now: drop their rows,
        # unless the API returned an empty table
        rows = self._fpl_upsert(self, existing, vals_by_key, unlink_missing=bool(vals_by_key))
        self._sync_breakdowns(rows, details, teams_by_code, fixtures_by_code)

    @api.model
    def _get_next_fixture_vals(self, form_item, team, teams_by_code, fixtures_by_code):
        next_match = form_item.get('next') or {}
        fixture = fixtures_by_code.get(str(next_match.get('matchId')))
        home_team = next_match.get('homeTeam') or {}
        away_team = next_match.get('awayTeam') or {}
        is_home = str(home_team.get('id')) == str(team.code)
        opponent_info = away_team if is_home else home_team
        if fixture:
            opponent = fixture.team_a if fixture.team_h == team else fixture.team_h
        else:
            opponent = teams_by_code.get(str(opponent_info.get('id')), self.env['fpl.teams'])
        return {
            'next_fixture_id': fixture.id if fixture else False,
            'next_opponent_id': opponent.id,
            'next_kickoff_time': self._parse_pulse_datetime(next_match.get('kickoff')),
            'next_is_home': is_home,
        }

    @api.model
    def _sync_breakdowns(self, rows, details, teams_by_code, fixtures_by_code):
        """Home/away breakdown and last results of every team, in batch."""
        Record = self.env['fpl.table.standings.record']
        Form = self.env['fpl.table.standings.form']
        standings_ids = [row.id for row in rows.values()]

        existing_records = {
            (rec.standings_id.id, rec.record_type): rec
            for rec in Record.search([('standings_id', 'in', standings_ids)])
        }
        record_vals = {}
        existing_forms = {
            (form.standings_id.id, form.sequence): form
            for form in Form.search([('standings_id', 'in', standings_ids)])
        }
        form_vals = {}
        no_team = self.env['fpl.teams']
        for team_id, row in rows.items():
            entry, form_item, team = details[team_id]
            for record_type in ('home', 'away'):
                data = entry.get(record_type) or {}
                record_vals[(row.id, record_type)] = {
                    'standings_id': row.id,
                    'record_type': record_type,
                    'played': data.get('played', 0),
                    'won': data.get('won', 0),
                    'drawn': data.get('drawn', 0),
                    'lost': data.get('lost', 0),
                    'goals_for': data.get('goalsFor', 0),
                    'goals_against': data.get('goalsAgainst', 0),
                    'points': data.get('points', 0),
                }
            if not form_item:
                continue
            recent = sorted((form_item.get('form') or [])[-FORM_LENGTH:], key=lambda m: m.get('kickoff') or '')
            sequence = 0
            for match in recent:
                home_team = match.get('homeTeam') or {}
                away_team = match.get('awayTeam') or {}
                is_home = str(home_team.get('id')) == str(team.code)
                own_score = (home_team if is_home else away_team).get('score')
                opponent_info = away_team if is_home else home_team
                opponent_score = opponent_info.get('score')
                if own_score is None or opponent_score is None:
                    continue
                sequence += 1
                fixture = fixtures_by_code.get(str(match.get('matchId')))
                form_vals[(row.id, sequence)] = {
                    'standings_id': row.id,
                    'sequence': sequence,
                    'result': 'W' if own_score > opponent_score else ('L' if own_score < opponent_score else 'D'),
                    'fixture_id': fixture.id if fixture else False,
                    'opponent_id': teams_by_code.get(str(opponent_info.get('id')), no_team).id,
                    'match_date': self._parse_pulse_datetime(match.get('kickoff')),
                }

        self._fpl_upsert(Record, existing_records, record_vals, unlink_missing=True)
        self._fpl_upsert(Form, existing_forms, form_vals, unlink_missing=True)

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

    standings_id = fields.Many2one('fpl.table.standings', string='Standings', required=True, index=True,
                                   ondelete='cascade')
    record_type = fields.Selection([('home', 'Home'), ('away', 'Away')], string='Record Type', required=True)
    played = fields.Integer(string='Played')
    won = fields.Integer(string='Won')
    drawn = fields.Integer(string='Drawn')
    lost = fields.Integer(string='Lost')
    goals_for = fields.Integer(string='Goals For')
    goals_against = fields.Integer(string='Goals Against')
    points = fields.Integer(string='Points')


class FplTableStandingsForm(models.Model):
    _name = 'fpl.table.standings.form'
    _description = 'FPL Table Standings Recent Form'
    _order = 'sequence asc'

    standings_id = fields.Many2one('fpl.table.standings', string='Standings', required=True, index=True,
                                   ondelete='cascade')
    sequence = fields.Integer(string='Sequence')
    result = fields.Selection(RESULT_SELECTION, string='Result')
    fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Fixture')
    opponent_id = fields.Many2one('fpl.teams', string='Opponent')
    match_date = fields.Datetime(string='Match Date')
