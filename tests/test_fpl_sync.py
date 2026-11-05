import base64
import copy
import hashlib
import io
import json
import os
import shutil
import tempfile
from datetime import datetime
from unittest.mock import patch

from PIL import Image

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

from ..models.fpi_import_data import PLAYER_PHOTO_URL, TEAM_BADGE_URL, TEAM_SHIRT_URL
from ..models.fpl_api_mixin import FPLApiMixin
from ..services.fpl_api_client import FPLApiClient, FPLApiException

# A far-future season, so that the tests never collide with synced data
SEASON = '2031/2032'
DEADLINE = datetime(2031, 8, 15, 10, 0)


class FakeApi:
    """Replaces every FPL / Pulse Live API call (no network in tests)."""

    def __init__(self):
        self.responses = {}
        self.calls = []

    def set(self, method, args, response):
        self.responses[(method, tuple(args))] = response

    def __call__(self, model, client, method, *args, **kwargs):
        self.calls.append((method, args))
        key = (method, args)
        if key not in self.responses:
            raise AssertionError(f"Unexpected API call {key}")
        response = self.responses[key]
        if isinstance(response, Exception):
            raise response
        return copy.deepcopy(response)


@tagged('post_install', '-at_install', 'fantasy_premier_league')
class FplSyncCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.api = FakeApi()
        cls.event = cls.env['fpl.events'].create({
            'event_id': 1, 'name': 'Gameweek 1', 'deadline_time': DEADLINE, 'is_current': True,
        })
        cls.home, cls.away = cls.env['fpl.teams'].create([
            {'name': 'Home FC', 'short_name': 'HOM', 'code': '9901', 'team_id': 901},
            {'name': 'Away FC', 'short_name': 'AWA', 'code': '9902', 'team_id': 902},
        ])
        cls.fwd_type = cls.env['fpl.element.types'].create({
            'element_type_id': '904', 'singular_name_short': 'FWD', 'plural_name_short': 'FWD',
        })
        cls.striker, cls.keeper = cls.env['fpl.elements'].create([
            {'element_id': 90001, 'code': '880001', 'web_name': 'Striker', 'fpl_team_id': cls.home.id,
             'element_type_id': cls.fwd_type.id},
            {'element_id': 90002, 'code': '880002', 'web_name': 'Keeper', 'fpl_team_id': cls.away.id,
             'element_type_id': cls.fwd_type.id},
        ])

    def setUp(self):
        super().setUp()
        self.api.responses.clear()
        self.api.calls.clear()
        api = self.api

        def fake_call(model, client, method, *args, **kwargs):
            return api(model, client, method, *args, **kwargs)

        patcher = patch.object(FPLApiMixin, '_fpl_call', fake_call)
        patcher.start()
        self.addCleanup(patcher.stop)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _fixture_payload(self, **overrides):
        payload = {
            'code': 7700001, 'id': 9001, 'event': 1, 'finished': False, 'finished_provisional': False,
            'kickoff_time': '2031-08-16T14:00:00Z', 'minutes': 10, 'provisional_start_time': False,
            'started': True, 'team_h': 901, 'team_a': 902, 'team_h_score': 0, 'team_a_score': 0,
            'team_h_difficulty': 2, 'team_a_difficulty': 3, 'pulse_id': 0, 'stats': [],
        }
        payload.update(overrides)
        return payload

    @staticmethod
    def _stat(identifier, home=(), away=()):
        return {
            'identifier': identifier,
            'h': [{'element': element, 'value': value} for element, value in home],
            'a': [{'element': element, 'value': value} for element, value in away],
        }


@tagged('post_install', '-at_install', 'fantasy_premier_league')
class TestUpsert(FplSyncCase):

    def test_unchanged_values_are_not_written(self):
        Mixin = self.env['fpl.api.mixin']
        existing = {self.striker.code: self.striker}
        with patch.object(type(self.striker), 'write', autospec=True) as write:
            Mixin._fpl_upsert('fpl.elements', existing, {self.striker.code: {
                'web_name': 'Striker', 'element_id': 90001, 'fpl_team_id': self.home.id, 'now_cost': 0.0,
            }})
            write.assert_not_called()
            Mixin._fpl_upsert('fpl.elements', existing, {self.striker.code: {
                'web_name': 'Striker', 'now_cost': 7.5,
            }})
            write.assert_called_once()
            self.assertEqual(write.call_args.args[1], {'now_cost': 7.5})

    def test_unlink_missing(self):
        Chips = self.env['fpl.event.chip.plays']
        plays = Chips.create([
            {'event_id': self.event.id, 'chip_name': 'wildcard', 'num_played': 1},
            {'event_id': self.event.id, 'chip_name': 'bboost', 'num_played': 1},
        ])
        existing = {play.chip_name: play for play in plays}
        result = self.env['fpl.api.mixin']._fpl_upsert(Chips, existing, {
            'wildcard': {'event_id': self.event.id, 'chip_name': 'wildcard', 'num_played': 5},
            '3xc': {'event_id': self.event.id, 'chip_name': '3xc', 'num_played': 2},
        }, unlink_missing=True)
        self.assertFalse(plays[1].exists())
        self.assertEqual(result['wildcard'], plays[0])
        self.assertEqual(plays[0].num_played, 5)
        self.assertEqual(result['3xc'].num_played, 2)

    def test_parse_datetime_to_naive_utc(self):
        Mixin = self.env['fpl.api.mixin']
        self.assertEqual(Mixin._fpl_parse_datetime('2031-08-16T14:00:00Z'), datetime(2031, 8, 16, 14, 0))
        self.assertEqual(Mixin._fpl_parse_datetime('2031-08-16T16:00:00+02:00'), datetime(2031, 8, 16, 14, 0))
        self.assertFalse(Mixin._fpl_parse_datetime(None))
        self.assertFalse(Mixin._fpl_parse_datetime('not a date'))


@tagged('post_install', '-at_install', 'fantasy_premier_league')
class TestBootstrap(FplSyncCase):

    def test_teams_matched_by_code_across_seasons(self):
        """team_id is re-assigned every season: the club code is the identity."""
        Import = self.env['fpl.import.data']
        Import._sync_teams_data([
            {'id': 902, 'code': 9901, 'name': 'Home FC', 'short_name': 'HOM'},  # same club, new id
            {'id': 901, 'code': 9903, 'name': 'Promoted FC', 'short_name': 'PRO'},  # new club, old id
        ])
        self.assertEqual(self.home.team_id, 902, "The club keeps its record, with its new id")
        self.assertFalse(self.away.active, "A club that left the league is archived")
        self.assertEqual(self.away.team_id, 0, "...and its id is freed for the new club")
        teams = self.env['fpl.teams']._get_teams_by_api_id()
        self.assertEqual(teams[901].name, 'Promoted FC')
        self.assertEqual(teams[902], self.home)

    def test_events_of_past_seasons_lose_current_flag(self):
        new_season_event = {
            'id': 1, 'name': 'Gameweek 1', 'deadline_time': '2032-08-14T10:00:00Z', 'is_current': False,
            'is_next': True, 'finished': False, 'chip_plays': [{'chip_name': 'bboost', 'num_played': 3}],
        }
        self.env['fpl.import.data']._sync_events_data([new_season_event])
        self.assertFalse(self.event.is_current)
        new_event = self.env['fpl.events'].search([('season', '=', '2032/2033'), ('event_id', '=', 1)])
        self.assertTrue(new_event, "Same event id, new season: a new record")
        self.assertEqual(new_event.event_chip_plays_ids.num_played, 3)
        self.assertEqual(self.env['fpl.events']._get_current_season(), '2032/2033')


@tagged('post_install', '-at_install', 'fantasy_premier_league')
class TestFixtures(FplSyncCase):

    def _channel_messages(self):
        channel = self.env.ref('fantasy_premier_league.channel_fpl_live')
        return self.env['mail.message'].search([('model', '=', 'discuss.channel'), ('res_id', '=', channel.id)])

    def test_live_fixture_sync_stats_and_notifications(self):
        Fixtures = self.env['fpl.gameweek.fixtures']
        first = self._fixture_payload(stats=[self._stat('bps', home=[(90001, 10)], away=[(90002, 4)])])
        changed = Fixtures._sync_fixtures([first])
        fixture = Fixtures.search([('code', '=', '7700001')])
        self.assertEqual(changed, fixture)
        self.assertEqual((fixture.team_h, fixture.team_a, fixture.season), (self.home, self.away, SEASON))
        self.assertEqual(fixture.team_h_bps_ids.element_id, self.striker)
        self.assertEqual(fixture.team_a_bps_ids.value, 4)

        messages = self._channel_messages()
        goal = self._fixture_payload(minutes=55, team_h_score=1, stats=[
            self._stat('goals_scored', home=[(90001, 1)]),
            self._stat('red_cards', away=[(90002, 1)]),
            self._stat('bps', home=[(90001, 30)], away=[(90002, 4)]),
        ])
        self.assertEqual(Fixtures._sync_fixtures([goal]), fixture)
        self.assertEqual(fixture.team_h_score, 1)
        self.assertEqual(fixture.team_h_goals_scored_ids.element_id, self.striker)
        self.assertEqual(fixture.team_h_bps_ids.value, 30)
        self.assertEqual(len(fixture.stat_ids), 4)
        new_messages = self._channel_messages() - messages
        self.assertEqual(len(new_messages), 1, "One message per update, in the FPL Live channel")
        self.assertIn('GOAL! Home FC scored', new_messages.body)
        self.assertIn('RED CARD! Away FC', new_messages.body)

        # Same data again: nothing changes, nothing is announced
        self.assertFalse(Fixtures._sync_fixtures([goal]))
        self.assertEqual(len(self._channel_messages()), len(messages) + 1)

        # A finished fixture is not processed again
        Fixtures._sync_fixtures([self._fixture_payload(finished=True, finished_provisional=True, minutes=90,
                                                       team_h_score=1)])
        self.assertTrue(fixture.finished)
        self.assertFalse(Fixtures._sync_fixtures([self._fixture_payload(team_h_score=5)]))
        self.assertEqual(fixture.team_h_score, 1)

    def test_current_season_search(self):
        Fixtures = self.env['fpl.gameweek.fixtures']
        Fixtures._sync_fixtures([self._fixture_payload()], send_live_notifications=False)
        current = Fixtures.search([('is_current_season', '=', True)])
        self.assertEqual(current.mapped('season'), [SEASON])
        self.assertNotIn(SEASON, Fixtures.search([('is_current_season', '=', False)]).mapped('season'))

    def test_polling_needed_only_around_matches(self):
        Fixtures = self.env['fpl.gameweek.fixtures']
        self.assertFalse(Fixtures._needs_live_polling())
        Fixtures._sync_fixtures([self._fixture_payload(kickoff_time='2020-01-01T15:00:00Z')],
                                send_live_notifications=False)
        self.assertTrue(Fixtures._needs_live_polling(), "Kicked off and not finished: keep polling")
        self.assertTrue(Fixtures._needs_live_polling(strict=True))


@tagged('post_install', '-at_install', 'fantasy_premier_league')
class TestGameweekPicks(FplSyncCase):

    def test_points_multiplier_and_entry_history(self):
        Fixtures = self.env['fpl.gameweek.fixtures']
        Fixtures._sync_fixtures([self._fixture_payload()], send_live_notifications=False)
        manager = self.env['fpl.manager.team'].create({'manager_id': 99999901, 'name': 'Test Team'})
        self.api.set('get_gameweek_picks', (99999901, 1), {
            'active_chip': '3xc',
            'automatic_subs': [{'entry': 99999901, 'element_in': 90001, 'element_out': 90002, 'event': 1}],
            'entry_history': {'points': 40, 'total_points': 40, 'rank': 1234, 'bank': 5, 'value': 1003,
                              'event_transfers': 1, 'event_transfers_cost': 4, 'points_on_bench': 2},
            'picks': [
                {'element': 90001, 'position': 9, 'multiplier': 3, 'is_captain': True,
                 'is_vice_captain': False, 'element_type': 904},
                {'element': 90002, 'position': 12, 'multiplier': 0, 'is_captain': False,
                 'is_vice_captain': False, 'element_type': 904},
            ],
        })
        explain = [{'fixture': 9001, 'stats': [{'identifier': 'minutes', 'points': 2, 'value': 90},
                                               {'identifier': 'goals_scored', 'points': 4, 'value': 1},
                                               {'identifier': 'some_new_rule', 'points': 1, 'value': 1}]}]
        self.api.set('get_element_gameweek_live', (1,), {'elements': [
            {'id': 90001, 'stats': {'total_points': 7}, 'explain': explain},
            {'id': 90002, 'stats': {'total_points': 2}, 'explain': []},
        ]})

        self.keeper.write({'status': 'd', 'chance_of_playing_this_round': '75', 'news': 'Knock'})

        data = self.env['fpl.gameweek.picks'].get_gameweek_picks_data(manager.id, self.event.id)
        self.assertTrue(data['found'])
        summary = data['summary']
        self.assertEqual(summary['bank'], 0.5)
        self.assertEqual(summary['value'], 100.3)
        self.assertEqual(summary['event_transfers_cost'], 4, "A transfer hit is a number of points")
        self.assertEqual(summary['active_chip_name'], 'Triple Captain')
        (captain,), = data['rows']
        bench, = data['bench']
        self.assertEqual(captain['points'], 21, "Triple captain: 7 x 3")
        self.assertEqual((captain['raw_points'], captain['multiplier']), (7, 3))
        self.assertEqual(bench['points'], 2, "Bench: raw points")
        self.assertEqual(bench['bench_order'], 1)
        self.assertEqual((captain['auto_sub'], bench['auto_sub']), ('in', 'out'))
        self.assertEqual((captain['status'], captain['chance']), ('a', None))
        self.assertEqual((bench['status'], bench['status_label'], bench['chance'], bench['news']),
                         ('d', 'Doubtful', 75, 'Knock'))
        self.assertEqual(captain['shirt_url'], f'/web/image/fpl.teams/{self.home.id}/shirt_image')

        # The fixture of each team, seen from the player's side, with its breakdown
        fixture, = captain['fixtures']
        self.assertEqual((fixture['is_home'], fixture['opponent'], fixture['live']), (True, 'AWA', True))
        self.assertEqual([stat['points'] for stat in fixture['stats']], [2, 4, 1])
        away_fixture, = bench['fixtures']
        self.assertEqual((away_fixture['is_home'], away_fixture['opponent'], away_fixture['stats']),
                         (False, 'HOM', []))
        self.assertTrue(data['has_live'])
        captain_line = captain['id']

        line = self.env['fpl.gameweek.pick.lines'].browse(captain_line)
        self.assertEqual(len(line.element_stats_ids), 3, "Unknown scoring identifiers are kept")
        self.assertEqual(line.gw_fixture_id.code, '7700001')
        action = line.action_open_player_stats(line.id)
        self.assertEqual((action['res_model'], action['res_id']), ('fpl.gameweek.pick.lines', line.id))

        # The current gameweek was synced less than a minute ago: no new API call
        calls = len(self.api.calls)
        self.env['fpl.gameweek.picks'].get_gameweek_picks_data(manager.id, self.event.id)
        self.assertEqual(len(self.api.calls), calls)


@tagged('post_install', '-at_install', 'fantasy_premier_league')
class TestManagerSync(FplSyncCase):

    def _standings(self, entries):
        return {'last_updated_data': '2031-08-20T10:00:00Z', 'standings': {'results': [
            {'entry': entry, 'entry_name': f'Team {entry}', 'player_name': f'<b>Player {entry}</b>',
             'rank': rank, 'last_rank': rank, 'rank_sort': rank, 'total': 100 - rank, 'event_total': 10}
            for rank, entry in enumerate(entries, start=1)
        ]}}

    def test_public_sync_and_standings_without_duplicates(self):
        overall = self.env['fpl.phases'].search([('phase_id', '=', 1)], limit=1) \
            or self.env['fpl.phases'].create({'phase_id': 1, 'name': 'Overall'})
        manager_id = 99999902
        self.api.set('get_entry_summary', (manager_id,), {
            'id': manager_id, 'name': 'My Team', 'summary_overall_points': 100, 'favourite_team': 901,
            'joined_time': '2031-07-01T10:00:00Z', 'last_deadline_bank': 15, 'unknown_new_key': 'ignored',
            'leagues': {'classic': [{'id': 555001, 'name': 'Mini League', 'created': '2031-07-01T10:00:00Z',
                                     'entry_rank': 2, 'entry_last_rank': 3,
                                     'active_phases': [{'phase': 1, 'rank': 2, 'total': 100}]}],
                        'h2h': []},
        })
        self.api.set('get_entry_history', (manager_id,), {
            'current': [{'event': 1, 'points': 50, 'total_points': 50, 'bank': 5, 'value': 1000,
                         'event_transfers_cost': 4}],
            'past': [{'season_name': '2030/31', 'total_points': 2000, 'rank': 1000}],
        })
        self.api.set('get_league_standings', (555001, 1, 1), self._standings([11, 12, 13]))

        Managers = self.env['fpl.manager.team']
        manager = Managers.sync_manager_data(manager_id=str(manager_id), public_only=True)
        self.assertEqual((manager.name, manager.favourite_team), ('My Team', self.home))
        self.assertEqual(manager.last_deadline_bank, 1.5)
        self.assertEqual(manager.entry_history_ids.value, 100.0)
        self.assertEqual(manager.entry_history_ids.event_transfer_cost, 4)
        league = manager.league_classic_ids
        self.assertEqual(league.overall_points, 100)
        self.assertEqual(league.standing_result_ids.mapped('entry'), [11, 12, 13])
        self.assertNotIn('<b>', league.standing_result_ids[0].name, "Player names are escaped")

        # Second sync, one entry left the first page: no duplicates, stale row removed
        self.api.set('get_league_standings', (555001, 1, 1), self._standings([12, 11, 14]))
        Managers.sync_manager_data(manager_id=manager_id, public_only=True)
        self.assertEqual(sorted(league.standing_result_ids.mapped('entry')), [11, 12, 14])
        self.assertEqual(len(self.env['fpl.league.standings.results'].search([('league_id', '=', league.id)])), 3)
        self.assertEqual(league.standing_result_ids.phase_id, overall)

        # A standing that cannot be fetched keeps its last known rows
        self.api.set('get_league_standings', (555001, 1, 1), RuntimeError('API down'))
        Managers.sync_manager_data(manager_id=manager_id, public_only=True)
        self.assertEqual(len(league.standing_result_ids), 3)

        # Opening the form right after a sync does not call the API again
        calls = len(self.api.calls)
        self.assertFalse(manager.action_sync_on_open())
        self.assertEqual(len(self.api.calls), calls)


@tagged('post_install', '-at_install', 'fantasy_premier_league')
class TestElementSummary(FplSyncCase):

    def test_summary_batch_replaces_played_fixtures(self):
        Fixtures = self.env['fpl.gameweek.fixtures']
        Fixtures._sync_fixtures([
            self._fixture_payload(),
            self._fixture_payload(code=7700002, id=9002, started=False, kickoff_time='2031-08-23T14:00:00Z'),
        ], send_live_notifications=False)
        played, upcoming = Fixtures.search([('code', 'in', ['7700001', '7700002'])], order='code')
        self.env['fpl.element.summary.fixture'].create({
            'element_id': self.striker.id, 'fixture_id': played.id, 'is_home': True, 'team_a': self.away.id,
        })
        summary = {
            'history': [{'element': 90001, 'fixture': 9001, 'opponent_team': 902, 'total_points': 7,
                         'was_home': True, 'kickoff_time': '2031-08-16T14:00:00Z', 'round': 1,
                         'value': 75, 'modified': False, 'brand_new_api_key': 1}],
            'history_past': [{'season_name': '2030/31', 'element_code': 880001, 'start_cost': 70,
                              'end_cost': 72, 'total_points': 150}],
            'fixtures': [{'id': 9002, 'code': 7700002, 'team_h': 902, 'team_a': 901, 'event': 1,
                          'is_home': False, 'difficulty': 4, 'kickoff_time': '2031-08-23T14:00:00Z'}],
        }
        self.api.set('get_element_summary', (90001,), summary)
        self.api.set('get_element_summary', (90002,), RuntimeError('API down'))

        (self.striker | self.keeper)._sync_element_summaries()

        self.assertEqual(self.striker.history_ids.value, 7.5)
        self.assertEqual(self.striker.history_ids.opponent_team, self.away)
        self.assertEqual(self.striker.history_past_ids.end_cost, 7.2)
        self.assertEqual(self.striker.fixture_ids.fixture_id, upcoming, "Played fixtures are removed")
        self.assertEqual(self.striker.fixture_ids.team_h, self.away)
        self.assertTrue(self.keeper.summary_synced_at, "A failed player is not retried in a loop")

        # Idempotent
        self.striker._sync_element_summaries()
        self.assertEqual(len(self.striker.history_ids), 1)
        self.assertEqual(len(self.striker.fixture_ids), 1)


@tagged('post_install', '-at_install', 'fantasy_premier_league')
class TestFplToken(FplSyncCase):

    def setUp(self):
        super().setUp()
        self.manager = self.env['fpl.manager.team'].create({'manager_id': 99999903, 'name': 'Token Team'})
        self.api.set('get_entry_summary', (99999903,), {'id': 99999903, 'name': 'Token Team', 'leagues': {}})
        self.api.set('get_entry_history', (99999903,), {'current': [], 'past': []})
        self.session_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.session_dir)
        self.env['ir.config_parameter'].set_param('fantasy_premier_league.browser_session_dir', self.session_dir)
        # The token code commits on purpose (rotated tokens must survive a later error); tests may not
        patcher = patch.object(self.env.cr, 'commit', lambda: None)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _messages(self):
        return self.env['mail.message'].search_count([
            ('model', '=', 'fpl.manager.team'), ('res_id', '=', self.manager.id), ('body', 'ilike', 'login has expired'),
        ])

    def _patch_browser(self, result):
        return patch.object(type(self.manager), '_run_browser_auth', autospec=True, return_value=result)

    def test_valid_access_token_is_reused(self):
        self.manager.sudo().write({'access_token': 'still-valid', 'refresh_token': 'refresh',
                                   'access_token_expiry': datetime(2099, 1, 1)})
        with patch.object(FPLApiClient, 'refresh_access_token') as refresh:
            self.assertEqual(self.manager._get_fpl_access_token(), 'still-valid')
            refresh.assert_not_called()

    def test_rejected_token_is_cleared_and_reported_once(self):
        self.manager.sudo().refresh_token = 'dead-token'
        rejected = FPLApiException("invalid_grant", status_code=400)
        with patch.object(FPLApiClient, 'refresh_access_token', side_effect=rejected) as refresh:
            warning = self.manager.action_sync_on_open()
            self.assertTrue(warning, "The user is warned that only public data was synced")
            self.assertFalse(self.manager.has_fpl_token, "A rejected token is forgotten")
            self.manager.last_sync_date = False
            self.assertFalse(self.manager.action_sync_on_open(), "...and not retried at the next sync")
            self.assertEqual(refresh.call_count, 1)
        self.assertEqual(self._messages(), 1)
        self.assertEqual(self.manager.name, 'Token Team')

    def test_network_error_keeps_the_token(self):
        self.manager.sudo().refresh_token = 'good-token'
        with patch.object(FPLApiClient, 'refresh_access_token', side_effect=FPLApiException("timeout")):
            with self.assertRaises(UserError):
                self.manager._get_fpl_access_token()
        self.assertEqual(self.manager.sudo().refresh_token, 'good-token')
        self.assertEqual(self._messages(), 0)

    def test_browser_session_gives_a_new_token_chain(self):
        """Refresh token rejected: a new chain is started from the SSO session."""
        session = {'cookies': [{'name': 'sso', 'value': 'old'}], 'origins': []}
        with open(os.path.join(self.session_dir, 'fpl_99999903.json'), 'w') as session_file:
            json.dump(session, session_file)
        self.manager.sudo().refresh_token = 'dead-token'
        renewed = {'cookies': [{'name': 'sso', 'value': 'renewed'}], 'origins': []}
        with patch.object(FPLApiClient, 'refresh_access_token',
                          side_effect=FPLApiException("invalid_grant", status_code=400)), \
                self._patch_browser({'status': 'ok', 'code': 'abc', 'code_verifier': 'xyz',
                                     'redirect_uri': 'https://fantasy.premierleague.com/',
                                     'storage_state': renewed}) as browser, \
                patch.object(FPLApiClient, 'exchange_authorization_code', return_value={
                    'access_token': 'new-access', 'refresh_token': 'new-refresh', 'expires_in': 3600,
                }) as exchange:
            self.assertEqual(self.manager._get_fpl_access_token(), 'new-access')
        self.assertEqual(browser.call_args.args[1]['storage_state'], session, "The saved session file is used")
        self.assertEqual(exchange.call_args.args[:3], ('abc', 'xyz', 'https://fantasy.premierleague.com/'))
        manager = self.manager.sudo()
        self.assertEqual(manager.refresh_token, 'new-refresh')
        self.assertEqual(json.loads(manager.browser_session), renewed, "Renewed SSO cookies are kept")
        self.assertTrue(manager.browser_session_date)
        self.assertFalse(self.manager._get_new_browser_session_file(), "The file is not imported twice")
        self.assertEqual(self._messages(), 0)

    def test_expired_browser_session_is_reported_once(self):
        self.manager.sudo().browser_session = json.dumps({'cookies': [], 'origins': []})
        # Not assertRaises: its savepoint would roll back what the code
        # commits on purpose before raising (commit is a no-op in tests)
        with self._patch_browser({'status': 'login_required'}):
            try:
                self.manager._get_fpl_access_token()
            except UserError:
                pass
            else:
                self.fail("UserError expected")
        self.assertFalse(self.manager.sudo().browser_session)
        self.assertFalse(self.manager.has_fpl_token)
        self.assertEqual(self._messages(), 1)


@tagged('post_install', '-at_install', 'fantasy_premier_league')
class TestImages(FplSyncCase):

    def _png(self):
        output = io.BytesIO()
        Image.new('RGBA', (4, 4), (255, 0, 0, 255)).save(output, format='PNG')
        return output.getvalue()

    def test_images_downloaded_into_database(self):
        Import = self.env['fpl.import.data']
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10"><rect width="20" height="10"/></svg>'
        png = self._png()
        cdn = {
            TEAM_BADGE_URL.format(code='9901'): svg,
            TEAM_SHIRT_URL.format(name='shirt_9901-110.webp'): b'outfield kit',
            TEAM_SHIRT_URL.format(name='shirt_9901_1-110.webp'): b'goalkeeper kit',
            PLAYER_PHOTO_URL.format(code='880001'): png,
        }
        requested = []

        def fake_get(url):
            requested.append(url)
            return cdn.get(url)  # None: 404, the image does not exist

        teams = self.home | self.away
        with patch('odoo.addons.fantasy_premier_league.models.fpi_import_data.http_get_bytes', fake_get):
            self.assertEqual(Import._download_team_logos(teams), 1)
            self.assertEqual(Import._download_team_shirts(teams), 2)
            self.assertEqual(Import._download_player_photos(self.striker | self.keeper), 1)

            self.assertTrue(self.home.photo)
            self.assertEqual(self.home.photo_checksum, hashlib.sha1(svg).hexdigest())
            self.assertEqual(base64.b64decode(self.home.shirt_gkp_image), b'goalkeeper kit')
            self.assertEqual(base64.b64decode(self.striker.photo), png)
            self.assertFalse(self.away.photo, "404: nothing stored")
            self.assertTrue(self.away.logo_checked_at and self.away.shirts_checked_at and self.keeper.images_checked_at)
            self.assertIn(self.home._logo_url(), self.env['fpl.picks'].new({'element_id': self.striker.id}).team_display)

            # Next run: the stored images are not fetched again, the missing
            # ones only after IMAGE_RETRY_DELAY
            requested.clear()
            self.assertEqual(Import.cron_download_images(), 0)
            self.assertFalse([url for url in requested if '9901' in url or '9902' in url or '88000' in url])

            # Forced: everything is fetched, but only what changed is written
            requested.clear()
            self.assertEqual(Import._download_team_logos(teams, force=True), 0)
            self.assertEqual(len(requested), 2)

    def test_new_players_trigger_the_image_download(self):
        cron = self.env.ref('fantasy_premier_league.ir_cron_download_fpl_images')
        triggers = self.env['ir.cron.trigger'].search_count([('cron_id', '=', cron.id)])
        self.env['fpl.import.data']._sync_elements_data([
            {'id': 90001, 'code': 880001, 'web_name': 'Striker', 'team': 901, 'element_type': 904},
            {'id': 90003, 'code': 880003, 'web_name': 'New Signing', 'team': 901, 'element_type': 904},
        ])
        self.assertEqual(self.env['ir.cron.trigger'].search_count([('cron_id', '=', cron.id)]), triggers + 1)
        self.assertFalse(self.keeper.active, "Players no longer returned by the API are archived")
