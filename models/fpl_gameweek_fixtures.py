import logging
import time
from collections import Counter, defaultdict
from datetime import timedelta

import pytz
from markupsafe import Markup, escape

from odoo import _, api, fields, models

from .fpl_fixture_stat import FIXTURE_STAT_KEYS

_logger = logging.getLogger(__name__)

LIVE_CHANNEL = 'fantasy_premier_league.fixtures_live'
LIVE_NOTIFICATION = 'fpl.fixtures/update'
# When nothing is being played, the whole season's fixtures are refreshed at
# most this often (rescheduled kick-off times, postponed matches...)
FULL_REFRESH_INTERVAL = timedelta(minutes=30)
FULL_REFRESH_PARAM = 'fantasy_premier_league.fixtures_last_full_refresh'

# (identifier, message) of the live events announced in Discuss
LIVE_STAT_EVENTS = [
    ('red_cards', "🟥 RED CARD! %(team)s player sent off!"),
    ('own_goals', "⚽ OWN GOAL! %(team)s scored an own goal!"),
    ('penalties_saved', "🥅 PENALTY SAVED! %(team)s goalkeeper made a penalty save!"),
    ('penalties_missed', "❌ PENALTY MISSED! %(team)s player missed a penalty!"),
]


def _stat_o2m(side, identifier, string):
    return fields.One2many(
        'fpl.fixture.stat', 'fixture_id', string=string, readonly=True,
        domain=[('side', '=', side), ('identifier', '=', identifier)],
    )


class FplGameweekFixtures(models.Model):
    _name = 'fpl.gameweek.fixtures'
    _inherit = ['fpl.api.mixin']
    _description = 'FPL Gameweek Fixtures'
    _order = 'kickoff_time, id'

    gameweek = fields.Integer(string='Gameweek')
    # Unique fixture identifier across seasons (gw_fixture_id is 1..380 every season)
    code = fields.Char(string='Code', index=True)
    event_id = fields.Many2one('fpl.events', string='Gameweek', index=True, group_expand='_read_group_event_ids',
                               readonly=True)
    season = fields.Char(string='Season', index=True)
    finished = fields.Boolean(string='Finished')
    finished_provisional = fields.Boolean(string='Finished provisional')
    gw_fixture_id = fields.Integer(string='Gameweek ID', index=True)
    kickoff_time = fields.Datetime(string='Kickoff Time')
    minutes = fields.Integer(string='Minutes')
    provisional_start_time = fields.Boolean(string='Provisional start time')
    started = fields.Boolean(string='Started')
    team_a = fields.Many2one('fpl.teams', string='Away team')
    team_h = fields.Many2one('fpl.teams', string='Home team')
    team_a_code = fields.Char()
    team_h_code = fields.Char()
    # Not stored: the badge already lives on fpl.teams, copying it on all 380
    # fixtures only duplicated attachments
    team_a_photo = fields.Image(related='team_a.photo')
    team_h_photo = fields.Image(related='team_h.photo')
    team_a_score = fields.Integer(string='Away Team Score')
    team_h_score = fields.Integer(string='Home Team Score')
    team_a_difficulty = fields.Integer(string='Away Team Difficulty')
    team_h_difficulty = fields.Integer(string='Home Team Difficulty')
    pulse_id = fields.Integer(string='Pulse id', index=True)

    stat_ids = fields.One2many('fpl.fixture.stat', 'fixture_id', string='Player Stats', readonly=True)
    team_a_goals_scored_ids = _stat_o2m('a', 'goals_scored', 'Away Team Goals Scored')
    team_a_assists_ids = _stat_o2m('a', 'assists', 'Away Team Assists')
    team_a_own_goals_ids = _stat_o2m('a', 'own_goals', 'Away Team Own Goals')
    team_a_penalties_saved_ids = _stat_o2m('a', 'penalties_saved', 'Away Team Penalties Saved')
    team_a_penalties_missed_ids = _stat_o2m('a', 'penalties_missed', 'Away Team Penalties Missed')
    team_a_yellow_cards_ids = _stat_o2m('a', 'yellow_cards', 'Away Team Yellow Cards')
    team_a_red_cards_ids = _stat_o2m('a', 'red_cards', 'Away Team Red Cards')
    team_a_saves_ids = _stat_o2m('a', 'saves', 'Away Team Saves')
    team_a_bonus_ids = _stat_o2m('a', 'bonus', 'Away Team Bonus')
    team_a_bps_ids = _stat_o2m('a', 'bps', 'Away Team Bonus Points System')
    team_a_defensive_contribution_ids = _stat_o2m('a', 'defensive_contribution', 'Away Team Defensive Contribution')

    team_h_goals_scored_ids = _stat_o2m('h', 'goals_scored', 'Home Team Goals Scored')
    team_h_assists_ids = _stat_o2m('h', 'assists', 'Home Team Assists')
    team_h_own_goals_ids = _stat_o2m('h', 'own_goals', 'Home Team Own Goals')
    team_h_penalties_saved_ids = _stat_o2m('h', 'penalties_saved', 'Home Team Penalties Saved')
    team_h_penalties_missed_ids = _stat_o2m('h', 'penalties_missed', 'Home Team Penalties Missed')
    team_h_yellow_cards_ids = _stat_o2m('h', 'yellow_cards', 'Home Team Yellow Cards')
    team_h_red_cards_ids = _stat_o2m('h', 'red_cards', 'Home Team Red Cards')
    team_h_saves_ids = _stat_o2m('h', 'saves', 'Home Team Saves')
    team_h_bonus_ids = _stat_o2m('h', 'bonus', 'Home Team Bonus')
    team_h_bps_ids = _stat_o2m('h', 'bps', 'Home Team Bonus Points System')
    team_h_defensive_contribution_ids = _stat_o2m('h', 'defensive_contribution', 'Home Team Defensive Contribution')

    is_current_season = fields.Boolean(compute='_compute_is_current_season', search='_search_is_current_season')
    match_result_display = fields.Html(string='Match Result', compute='_compute_match_result_display',
                                       sanitize=False)

    @api.depends('gameweek', 'team_h.name', 'team_a.name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'GW {rec.gameweek}: {rec.team_h.name or "?"} vs {rec.team_a.name or "?"}'

    @api.depends('season')
    def _compute_is_current_season(self):
        current_season = self.env['fpl.events']._get_current_season()
        for rec in self:
            rec.is_current_season = bool(current_season) and rec.season == current_season

    def _search_is_current_season(self, operator, value):
        if operator not in ('=', '!='):
            raise NotImplementedError(_("Unsupported search on 'is current season'."))
        positive = (operator == '=') == bool(value)
        return [('season', '=' if positive else '!=', self.env['fpl.events']._get_current_season())]

    @api.depends('started', 'finished_provisional', 'kickoff_time', 'team_h_score', 'team_a_score',
                 'team_h.name', 'team_a.name', 'team_h.photo_checksum', 'team_a.photo_checksum')
    @api.depends_context('tz')
    def _compute_match_result_display(self):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        logo = Markup("<img src='%s' style='width: 20px; border-radius: 10px;'/>")
        for rec in self:
            logo_h = logo % rec.team_h._logo_url() if rec.team_h else ''
            logo_a = logo % rec.team_a._logo_url() if rec.team_a else ''
            team_h = Markup('<strong>%s</strong> ') % (rec.team_h.name or '') + logo_h
            team_a = logo_a + Markup(' <strong>%s</strong>') % (rec.team_a.name or '')
            if rec.finished_provisional or rec.started:
                middle = Markup(' <strong>%s - %s</strong> ') % (rec.team_h_score, rec.team_a_score)
            elif rec.kickoff_time:
                kickoff = pytz.utc.localize(rec.kickoff_time).astimezone(user_tz).strftime('%H:%M')
                middle = Markup(" <span style='font-weight: bold; color: #34495E;'>%s</span> ") % kickoff
            else:
                middle = Markup(" <span class='text-muted'>%s</span> ") % _("TBC")
            rec.match_result_display = team_h + middle + team_a

    @api.model
    def _read_group_event_ids(self, events, domain):
        # Only the groups that have fixtures; needed so read_group returns the
        # fpl.events 'fold' flag (__fold) to the kanban view
        return events.sorted(lambda e: (e.season or '', e.event_id))

    @api.model
    def _get_fixtures_by_api_id(self, season=None):
        """``{FPL fixture id: record}`` of a season (the current one by default)."""
        season = season or self.env['fpl.events']._get_current_season()
        return {fixture.gw_fixture_id: fixture for fixture in self.search([('season', '=', season)])}

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------

    @api.model
    def cron_get_data_gameweek_fixutres(self, get_all=False, manual_gameweek=None, send_live_notifications=True,
                                        live_poll_interval=15, live_poll_budget=50):
        """Sync gameweek fixtures from the FPL API.

        ``ir.cron`` has no sub-minute interval, so when this runs as the
        scheduled live-tracking job (no ``manual_gameweek``/``get_all``) it
        loops internally every ``live_poll_interval`` seconds - committing
        after each pass so the kanban bus push lands right away - for up to
        ``live_poll_budget`` seconds. If a match is still live once that
        budget runs out, it re-queues itself to run again immediately via
        ``ir.cron``'s trigger mechanism rather than waiting for the next
        scheduled minute.

        When nothing is being played, the API is not called at all, except
        for a full season refresh every ``FULL_REFRESH_INTERVAL`` (kick-off
        time changes, postponements...).

        ``live_poll_interval`` defaults to 15s: FPL's own backend only
        refreshes its live data roughly once a minute, polling faster just
        re-processes identical data.
        """
        # ir.cron holds a row lock on this job until the transaction commits:
        # release it right away instead of for the whole live loop.
        self.env.cr.commit()

        if manual_gameweek or get_all:
            self._poll_fixtures_once(None if get_all else [manual_gameweek], include_finished=True,
                                     send_live_notifications=send_live_notifications)
            return

        if not self._needs_live_polling():
            self._full_refresh_if_due()
            return

        deadline = time.monotonic() + live_poll_budget
        while True:
            self._poll_fixtures_once(self._get_live_polling_gameweeks(),
                                     send_live_notifications=send_live_notifications)
            self.env.cr.commit()
            live_now = self._needs_live_polling(strict=True)
            if not live_now or time.monotonic() >= deadline:
                break
            time.sleep(live_poll_interval)

        if live_now:
            self.env.ref('fantasy_premier_league.ir_cron_get_gameweek_fixtures')._trigger()

    @api.model
    def _needs_live_polling(self, strict=False):
        """True when a match is being played, or has been played but its
        data is not final yet (bonus points are confirmed later on).

        :param bool strict: only matches in progress (used to decide whether
            to keep looping within the same cron run)
        """
        if strict:
            domain = [('started', '=', True), ('finished_provisional', '=', False)]
        else:
            domain = [('kickoff_time', '<=', fields.Datetime.now()), ('finished', '=', False)]
        return bool(self.search_count(domain + [('is_current_season', '=', True)], limit=1))

    @api.model
    def _full_refresh_if_due(self):
        ICP = self.env['ir.config_parameter'].sudo()
        last_refresh = fields.Datetime.to_datetime(ICP.get_param(FULL_REFRESH_PARAM) or False)
        now = fields.Datetime.now()
        if last_refresh and now - last_refresh < FULL_REFRESH_INTERVAL:
            return
        Events = self.env['fpl.events']
        if not Events.search_count([('season', '=', Events._get_current_season()), ('finished', '=', False)]):
            # Off-season: the new season's fixtures re-use the event/team ids,
            # so the events and teams must be synced first (the bootstrap cron
            # only runs every 6 hours).
            self.env['fpl.import.data'].cron_get_data_boostrap_static()
        self._poll_fixtures_once(None, send_live_notifications=False)
        ICP.set_param(FULL_REFRESH_PARAM, fields.Datetime.to_string(now))

    @api.model
    def _get_live_polling_gameweeks(self):
        """Gameweeks worth an API call: the current one plus any gameweek that
        still has a fixture in progress (bonus points settling just after
        full time, near a gameweek boundary)."""
        gameweeks = set()
        current_event = self.env['fpl.events'].search([('is_current', '=', True)], limit=1)
        if current_event:
            gameweeks.add(current_event.event_id)
        in_progress = self.search([
            ('is_current_season', '=', True),
            ('kickoff_time', '<=', fields.Datetime.now()),
            ('finished', '=', False),
        ])
        gameweeks.update(in_progress.mapped('gameweek'))
        return sorted(gw for gw in gameweeks if gw)

    @api.model
    def _poll_fixtures_once(self, gameweeks, include_finished=False, send_live_notifications=True):
        """Fetch and store the fixtures of ``gameweeks`` (``None``: whole season).

        :return: the fixtures whose score/status changed
        """
        if gameweeks is None:
            calls = {'all': ('get_gameweek_fixtures', (None,))}
        else:
            calls = {gw: ('get_gameweek_fixtures', (gw,)) for gw in gameweeks}
        results, errors = self._fpl_fetch_many(calls)
        if errors and not results:
            error = next(iter(errors.values()))
            raise self._fpl_user_error(_("FPL API error during gameweek fixtures sync"), error) from error
        for gameweek, error in errors.items():
            _logger.warning("Fixtures of gameweek %s could not be fetched: %s", gameweek, error)

        fixtures_data = [fixture for result in results.values() for fixture in (result or [])]
        return self._sync_fixtures(fixtures_data, include_finished=include_finished,
                                   send_live_notifications=send_live_notifications)

    @api.model
    def _sync_fixtures(self, fixtures_data, include_finished=False, send_live_notifications=True):
        Events = self.env['fpl.events']
        season = Events._get_current_season()
        events = Events._get_events_by_api_id(season)
        teams = self.env['fpl.teams']._get_teams_by_api_id()
        existing = {
            fixture.code: fixture
            for fixture in self.search([('code', 'in', [str(data['code']) for data in fixtures_data])])
        }

        vals_by_key, data_by_key, snapshots = {}, {}, {}
        for data in fixtures_data:
            key = str(data['code'])
            fixture = existing.get(key)
            # A finished fixture (bonus confirmed) never changes again
            if fixture and fixture.finished and not include_finished:
                continue
            if fixture:
                snapshots[key] = fixture._get_fixture_snapshot()
            event = events.get(data.get('event'))
            team_h = teams.get(data.get('team_h'))
            team_a = teams.get(data.get('team_a'))
            vals_by_key[key] = {
                'code': key,
                'gw_fixture_id': data.get('id'),
                'gameweek': data.get('event') or 0,
                'event_id': event.id if event else False,
                'season': season,
                'finished': bool(data.get('finished')),
                'finished_provisional': bool(data.get('finished_provisional')),
                'kickoff_time': self._fpl_parse_datetime(data.get('kickoff_time')),
                'minutes': data.get('minutes'),
                'provisional_start_time': bool(data.get('provisional_start_time')),
                'started': bool(data.get('started')),
                'team_h': team_h.id if team_h else False,
                'team_h_code': team_h.code if team_h else False,
                'team_a': team_a.id if team_a else False,
                'team_a_code': team_a.code if team_a else False,
                'team_h_score': data.get('team_h_score'),
                'team_a_score': data.get('team_a_score'),
                'team_h_difficulty': data.get('team_h_difficulty'),
                'team_a_difficulty': data.get('team_a_difficulty'),
                'pulse_id': data.get('pulse_id'),
            }
            data_by_key[key] = data

        if not vals_by_key:
            return self.browse()

        fixtures = self._fpl_upsert(self, existing, vals_by_key)
        changed = self.browse([
            fixture.id for key, fixture in fixtures.items()
            if key not in snapshots or fixture._get_fixture_snapshot() != snapshots[key]
        ])
        stat_changes = self._sync_fixture_stats(
            {fixtures[key]: data_by_key[key].get('stats') or [] for key in fixtures}
        )
        changed |= self.browse([fixture.id for fixture in stat_changes])

        if send_live_notifications:
            for key, fixture in fixtures.items():
                if key in snapshots and fixture.started and not fixture.finished:
                    fixture._check_and_notify_live_updates(snapshots[key], stat_changes.get(fixture))
        if changed:
            self._notify_kanban_refresh(changed)
        return changed

    @api.model
    def _sync_fixture_stats(self, stats_by_fixture):
        """Store the player stats of several fixtures with one read and batched writes.

        :param dict stats_by_fixture: ``{fixture record: API 'stats' list}``
        :return: ``{fixture: (old Counter, new Counter)}`` of the fixtures whose
            stats changed; counters are keyed by ``(identifier, side)``
        """
        Stat = self.env['fpl.fixture.stat']
        element_ids = {
            player_stat.get('element')
            for stats in stats_by_fixture.values()
            for group in stats if group.get('identifier') in FIXTURE_STAT_KEYS
            for side in ('h', 'a')
            for player_stat in group.get(side) or []
        }
        elements = {
            element.element_id: element.id
            for element in self.env['fpl.elements'].search([('element_id', 'in', list(element_ids))])
        }

        fixture_ids = [fixture.id for fixture in stats_by_fixture]
        existing = {
            (stat.fixture_id.id, stat.side, stat.identifier, stat.element_id.id): stat
            for stat in Stat.search([('fixture_id', 'in', fixture_ids)])
        }
        old_counts = defaultdict(Counter)
        for (fixture_id, side, identifier, _element_id), stat in existing.items():
            old_counts[fixture_id][(identifier, side)] += stat.value

        vals_by_key = {}
        new_counts = defaultdict(Counter)
        for fixture, stats in stats_by_fixture.items():
            for group in stats:
                identifier = group.get('identifier')
                if identifier not in FIXTURE_STAT_KEYS:
                    continue
                for side in ('h', 'a'):
                    for player_stat in group.get(side) or []:
                        element_id = elements.get(player_stat.get('element'))
                        if not element_id:
                            continue
                        value = player_stat.get('value') or 0
                        vals_by_key[(fixture.id, side, identifier, element_id)] = {
                            'fixture_id': fixture.id,
                            'side': side,
                            'identifier': identifier,
                            'element_id': element_id,
                            'value': value,
                        }
                        new_counts[fixture.id][(identifier, side)] += value

        self._fpl_upsert(Stat, existing, vals_by_key, unlink_missing=True)
        return {
            fixture: (old_counts[fixture.id], new_counts[fixture.id])
            for fixture in stats_by_fixture
            if old_counts[fixture.id] != new_counts[fixture.id]
        }

    def _get_fixture_snapshot(self):
        """Data whose change is pushed to the live scoreboard."""
        self.ensure_one()
        return (self.team_h_score, self.team_a_score, self.minutes, self.started, self.finished_provisional,
                self.finished, self.kickoff_time)

    @api.model
    def _notify_kanban_refresh(self, fixtures):
        """Ping the live-scoreboard kanban so open clients reload. The payload
        only carries the changed ids - the client re-fetches through the
        normal view read."""
        self.env['bus.bus']._sendone(LIVE_CHANNEL, LIVE_NOTIFICATION, {'fixture_ids': fixtures.ids})

    # ------------------------------------------------------------------
    # Live notifications (Discuss)
    # ------------------------------------------------------------------

    def _check_and_notify_live_updates(self, old_snapshot, stat_change):
        self.ensure_one()
        notifications = []
        old_h_score, old_a_score = old_snapshot[0] or 0, old_snapshot[1] or 0
        score = f"{self.team_h.name} {self.team_h_score} - {self.team_a_score} {self.team_a.name}"
        if (self.team_h_score or 0) > old_h_score:
            notifications.append(f"⚽ GOAL! {self.team_h.name} scored! {score}")
        if (self.team_a_score or 0) > old_a_score:
            notifications.append(f"⚽ GOAL! {self.team_a.name} scored! {score}")

        if stat_change:
            old_counts, new_counts = stat_change
            for identifier, message in LIVE_STAT_EVENTS:
                for side, team in (('h', self.team_h), ('a', self.team_a)):
                    if new_counts[(identifier, side)] > old_counts[(identifier, side)]:
                        notifications.append(message % {'team': team.name})

        if notifications:
            self._send_live_notifications(notifications)

    def _send_live_notifications(self, notifications):
        """Post the live updates of this fixture in the "FPL Live" channel.

        One message per update in a shared channel (users may leave or mute
        it) rather than a private chat per user: the cost does not grow with
        the number of users, and no bot user gets a DM it would answer.
        """
        self.ensure_one()
        channel = self.env.ref('fantasy_premier_league.channel_fpl_live', raise_if_not_found=False)
        if not channel:
            _logger.info("FPL Live channel deleted: live notifications are disabled")
            return
        bot_partner = self.env.ref('fantasy_premier_league.fpl_bot_partner', raise_if_not_found=False)
        match_info = f"GW{self.gameweek}: {self.team_h.name} vs {self.team_a.name} ({self.minutes}')"
        body = Markup('<p><strong>🔴 LIVE MATCH UPDATE</strong></p><p><strong>%s</strong></p>') % match_info
        body += Markup('').join(Markup('<p>%s</p>') % escape(notification) for notification in notifications)
        try:
            # A messaging failure must never roll back the fixture sync
            with self.env.cr.savepoint():
                channel.sudo().message_post(
                    author_id=bot_partner.id if bot_partner else False,
                    body=body,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                )
            _logger.info("Live notification sent for %s: %s", match_info, notifications)
        except Exception:  # noqa: BLE001
            _logger.exception("Could not post the live notification of %s", match_info)

    @api.model
    def _init_live_channel_members(self):
        """Subscribe the internal users to the "FPL Live" channel (install/upgrade)."""
        channel = self.env.ref('fantasy_premier_league.channel_fpl_live', raise_if_not_found=False)
        if not channel:
            return
        users = self.env['res.users'].search([('share', '=', False)])
        channel.sudo().add_members(partner_ids=users.partner_id.ids, post_joined_message=False)
