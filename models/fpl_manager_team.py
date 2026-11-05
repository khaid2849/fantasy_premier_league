import json
import logging
import os
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..services.fpl_api_client import FPLApiClient, FPLApiException
from .master_data import REGIONS

_logger = logging.getLogger(__name__)

REGION_ISO_BY_ID = {region['id']: region['iso_code_short'] for region in REGIONS}
# Opening a manager form syncs it, but not more often than that
SYNC_ON_OPEN_THROTTLE = timedelta(minutes=2)
CHIP_STATES = [('available', 'Available'), ('used', 'Used'), ('unavailable', 'Not available')]
CHIP_STATE_FIELDS = {
    'wildcard': 'chip_wildcard_state',
    'freehit': 'chip_free_hit_state',
    'bboost': 'chip_bench_boost_state',
    '3xc': 'chip_triple_captain_state',
}
TOKEN_EXPIRED_MESSAGE = ("The FPL login has expired, only public data was synced. Log in again: run "
                         "docker/fpl-login.sh %(manager)s on the server, or click 'Update FPL Token' and "
                         "paste a new refresh token.")
TOKEN_FIELDS = ['refresh_token', 'access_token', 'access_token_expiry', 'browser_session']
# Postgres advisory lock namespace ('FPL') for the token refresh of a manager
TOKEN_LOCK_NAMESPACE = 0x46504C
TOKEN_LOCK_TIMEOUT = '150s'
# Browser session (Premier League SSO cookies) used to get new tokens, see
# scripts/fpl_browser_auth.py and docker/fpl-login.sh
BROWSER_AUTH_SCRIPT = str(Path(__file__).resolve().parent.parent / 'scripts' / 'fpl_browser_auth.py')
BROWSER_AUTH_TIMEOUT = 150
BROWSER_SESSION_DIR_PARAM = 'fantasy_premier_league.browser_session_dir'
DEFAULT_BROWSER_SESSION_DIR = '/var/lib/odoo/alobo_profiles/fpl'


class FPLManagerTeam(models.Model):
    _name = 'fpl.manager.team'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'fpl.api.mixin']
    _description = 'FPL Manager Team'
    _order = 'name, id'

    manager_id = fields.Integer(string='Manager ID', index=True)
    # FPL OIDC tokens: the refresh token rotates on every exchange, see _get_fpl_access_token
    refresh_token = fields.Char(string='FPL Refresh Token', groups='base.group_system', copy=False)
    access_token = fields.Char(string='FPL Access Token', groups='base.group_system', copy=False)
    access_token_expiry = fields.Datetime(string='Access Token Expiry', groups='base.group_system', copy=False)
    has_fpl_token = fields.Boolean(string='FPL Token Connected', compute='_compute_has_fpl_token')
    # Browser state (Premier League SSO cookies) able to start a new token
    # chain without asking for the password again, see _fpl_browser_login
    browser_session = fields.Text(string='FPL Browser Session', groups='base.group_system', copy=False)
    browser_session_date = fields.Datetime(string='Browser Session Updated', readonly=True, copy=False)
    last_sync_date = fields.Datetime(string='Last Sync', readonly=True, copy=False)
    # Manager Data
    manager_data_id = fields.Integer(string='Manager Data ID')
    date_of_birth = fields.Date(string='Date of Birth', tracking=True)
    default_event = fields.Integer(string='Default Event')
    dirty = fields.Boolean(string='Dirty')
    first_name = fields.Char(string='First Name', tracking=True)
    last_name = fields.Char(string='Last Name', tracking=True)
    full_name = fields.Char(string='Full Name', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    gender = fields.Selection([('M', 'Male'), ('F', 'Female')], string='Gender', tracking=True)
    manger_data_id = fields.Integer(string='ID')
    region = fields.Char(string='Region')
    country_id = fields.Many2one('res.country', string='Country', tracking=True)
    entry_email = fields.Boolean(string='Entry Email')
    entry_language = fields.Char(string='Entry Language')
    sso_id = fields.Char(string='SSO ID')
    # Manager Entry Summary
    joined_time = fields.Datetime(string='Joined Time')
    started_event = fields.Integer(string='Started Event')
    favourite_team = fields.Many2one('fpl.teams', string='Favourite Team', tracking=True)
    player_first_name = fields.Char(string='Player First Name')
    player_last_name = fields.Char(string='Player Last Name')
    player_region_id = fields.Char(string='Player Region ID')
    player_region_name = fields.Char(string='Player Region Name')
    player_region_iso_code_short = fields.Char(string='Player Region ISO Code Short')
    player_region_iso_code_long = fields.Char(string='Player Region ISO Code Long')
    years_active = fields.Integer(string='Years Active')
    summary_overall_points = fields.Integer(string='Summary Overall Points', tracking=True)
    summary_overall_rank = fields.Integer(string='Summary Overall Rank', tracking=True)
    summary_event_points = fields.Integer(string='Current Gameweek points', tracking=True)
    summary_event_rank = fields.Integer(string='Current Gameweek Rank', tracking=True)
    current_event = fields.Integer(string='Current Gameweek', tracking=True)
    name = fields.Char(string='Name', tracking=True)
    name_change_blocked = fields.Boolean(string='Name Change Blocked')
    kits = fields.Char(string='Kits')
    last_deadline_bank = fields.Float(string='Last Deadline Bank')
    last_deadline_value = fields.Float(string='Last Deadline Value')
    last_deadline_total_transfers = fields.Integer(string='Last Deadline Total Transfers')
    club_badge_src = fields.Char(string='Club Badge Src')
    league_classic_ids = fields.One2many('fpl.leagues', 'manager_id', string='League Classic IDs',
                                         domain=[('type', '=', 'classic')])
    league_h2h_ids = fields.One2many('fpl.leagues', 'manager_id', string='League H2H IDs',
                                     domain=[('type', '=', 'h2h')])
    pick_ids = fields.One2many('fpl.picks', 'manager_id', string='Element IDs')
    manager_chip_ids = fields.One2many('fpl.manager.chips', 'manager_id', string='Manager Chips')
    picks_last_updated = fields.Datetime(string='Picks Last Updated')

    # Transfer Info
    cost = fields.Integer(string='Cost', tracking=True)
    status = fields.Char(string='Status')
    limit = fields.Integer(string='Transfers Limit', tracking=True)
    made = fields.Float(string='Transfers Made', tracking=True)
    bank = fields.Float(string='In the Bank', tracking=True)
    value = fields.Float(string='Squad Value', tracking=True)
    status_for_entry = fields.Selection([('available', 'Available'), ('played', 'Played'), ('used', 'Used'),
                                         ('unavailable', 'Unavailable')], string='Status for Entry')

    chip_wildcard_state = fields.Selection(CHIP_STATES, string='Wildcard', compute='_compute_chip_states')
    chip_free_hit_state = fields.Selection(CHIP_STATES, string='Free Hit', compute='_compute_chip_states')
    chip_bench_boost_state = fields.Selection(CHIP_STATES, string='Bench Boost', compute='_compute_chip_states')
    chip_triple_captain_state = fields.Selection(CHIP_STATES, string='Triple Captain', compute='_compute_chip_states')

    # Entry History
    entry_history_ids = fields.One2many('fpl.entry.history', 'manager_id', string='Entry History')
    entry_past_ids = fields.One2many('fpl.past', 'manager_id', string='Entry Past')

    _sql_constraints = [
        ('manager_id_uniq', 'unique(manager_id)', 'This FPL manager already exists.'),
    ]

    @api.depends('refresh_token', 'browser_session', 'browser_session_date')
    def _compute_has_fpl_token(self):
        for rec in self:
            manager = rec.sudo()
            rec.has_fpl_token = bool(
                manager.refresh_token or manager.browser_session or rec._get_new_browser_session_file()
            )

    @api.depends('manager_chip_ids.status_for_entry', 'manager_chip_ids.chip_id.name')
    def _compute_chip_states(self):
        for rec in self:
            for chip_name, field_name in CHIP_STATE_FIELDS.items():
                statuses = set(rec.manager_chip_ids.filtered(lambda c: c.name == chip_name).mapped('status_for_entry'))
                if 'available' in statuses:
                    rec[field_name] = 'available'
                elif statuses & {'played', 'used'}:
                    rec[field_name] = 'used'
                else:
                    rec[field_name] = 'unavailable'

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_open_entry_history(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id(
            'fantasy_premier_league.fpl_manager_team_history_wizard_action')
        action['context'] = {
            'default_entry_history_ids': self.entry_history_ids.ids,
            'default_entry_past_ids': self.entry_past_ids.ids,
        }
        return action

    def action_verify_manager_data(self):
        """Open the wizard to (re)connect the FPL token of this manager"""
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('fantasy_premier_league.fpl_manager_team_wizard_action')
        action['context'] = {'default_manager_id': self.manager_id, 'is_readonly': True}
        return action

    def action_sync_manager_data(self):
        """Sync this manager with the stored FPL token, without asking for credentials"""
        self.ensure_one()
        self.sync_manager_data(manager_id=self.manager_id)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Manager data has been synced from FPL API'),
                'type': 'success',
                'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
            },
        }

    def action_sync_on_open(self):
        """Called by the form view each time a record is opened: refresh its data
        from the FPL API (at most every ``SYNC_ON_OPEN_THROTTLE``).

        Falls back to public data when the stored token can no longer be
        refreshed, so that opening the record never asks for credentials.

        :return: a warning message, or False
        """
        self.ensure_one()
        if self.last_sync_date and fields.Datetime.now() - self.last_sync_date < SYNC_ON_OPEN_THROTTLE:
            return False
        public_only = False
        warning = False
        if self.has_fpl_token:
            try:
                self._get_fpl_access_token()
            except UserError:
                public_only = True
                warning = _(TOKEN_EXPIRED_MESSAGE, manager=self.manager_id)
        self.sync_manager_data(manager_id=self.manager_id, public_only=public_only)
        return warning

    # ------------------------------------------------------------------
    # FPL tokens
    # ------------------------------------------------------------------

    @api.model
    def _fpl_exchange_refresh_token(self, refresh_token):
        client_id = self.env['ir.config_parameter'].sudo().get_param('fantasy_premier_league.oidc_client_id')
        try:
            return FPLApiClient.refresh_access_token(refresh_token, client_id=client_id)
        except FPLApiException as e:
            raise UserError(_("%s\nPlease click 'Update FPL Token' and paste a new refresh token.", e)) from e

    def _store_fpl_tokens(self, token_data):
        self.ensure_one()
        self.sudo().write({
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token') or self.sudo().refresh_token,
            'access_token_expiry': fields.Datetime.now() + timedelta(seconds=token_data.get('expires_in') or 3600),
        })
        # The old refresh token is already revoked by FPL: commit now so that
        # a later sync error cannot roll back the rotated one.
        self.env.cr.commit()

    def _get_valid_access_token(self):
        manager = self.sudo()
        if manager.access_token and manager.access_token_expiry \
                and manager.access_token_expiry > fields.Datetime.now() + timedelta(minutes=2):
            return manager.access_token
        return False

    @contextmanager
    def _fpl_token_lock(self):
        """Only one process refreshes the tokens of a manager at a time.

        Refresh tokens rotate: two processes (e.g. the cron and a user opening
        the form) refreshing with the same token make FPL see a re-used token,
        which revokes the whole chain. The lock lives in its own transaction,
        so it is released even if the caller's transaction fails.
        """
        self.ensure_one()
        with self.pool.cursor() as lock_cr:
            lock_cr.execute(f"SET LOCAL lock_timeout = '{TOKEN_LOCK_TIMEOUT}'")
            try:
                lock_cr.execute("SELECT pg_advisory_xact_lock(%s, %s)", [TOKEN_LOCK_NAMESPACE, self.id])
            except psycopg2.errors.LockNotAvailable as e:
                raise UserError(_("The FPL token of manager %s is being refreshed by another process, "
                                  "please try again in a moment.", self.manager_id)) from e
            yield

    def _get_fpl_access_token(self):
        """Return a valid access token, getting a new one when needed: with
        the refresh token, or else with the browser session."""
        self.ensure_one()
        token = self._get_valid_access_token()
        if token:
            return token
        with self._fpl_token_lock():
            # Another process may have refreshed the tokens while we waited
            # for the lock: a new transaction sees what it committed.
            self.env.cr.commit()
            self.sudo().invalidate_recordset(TOKEN_FIELDS)
            token = self._get_valid_access_token()
            if token:
                return token
            token_data = self._fpl_new_tokens()
            self._store_fpl_tokens(token_data)
            return token_data['access_token']

    def _fpl_new_tokens(self):
        """Refresh the tokens; when FPL rejects the refresh token (expired or
        revoked), start a new token chain from the browser session.

        Credentials that FPL rejects are forgotten, and the user is told once.
        """
        manager = self.sudo()
        client_id = self.env['ir.config_parameter'].sudo().get_param('fantasy_premier_league.oidc_client_id')
        rejected = False
        if manager.refresh_token:
            try:
                return FPLApiClient.refresh_access_token(manager.refresh_token, client_id=client_id)
            except FPLApiException as e:
                if e.status_code not in (400, 401):
                    # Network error, FPL down...: keep the token for the next try
                    raise UserError(_("Could not refresh the FPL token: %s", e)) from e
                _logger.warning("FPL refresh token of manager %s rejected: %s", self.manager_id, e)
                manager.write({'refresh_token': False, 'access_token': False, 'access_token_expiry': False})
                rejected = True

        status, token_data = self._fpl_browser_login()
        if token_data:
            _logger.info("New FPL token chain for manager %s from the browser session", self.manager_id)
            return token_data
        if rejected or status == 'login_required':
            self.message_post(body=_(TOKEN_EXPIRED_MESSAGE, manager=self.manager_id))
            # Committed so that it survives the UserError raised below
            self.env.cr.commit()
        raise UserError(_(TOKEN_EXPIRED_MESSAGE, manager=self.manager_id))

    def _get_browser_session_dir(self):
        return self.env['ir.config_parameter'].sudo().get_param(BROWSER_SESSION_DIR_PARAM, DEFAULT_BROWSER_SESSION_DIR)

    def _get_new_browser_session_file(self):
        """The session file saved by docker/fpl-login.sh for this manager, when
        it is newer than the session already in database."""
        self.ensure_one()
        if not self.manager_id:
            return False
        path = os.path.join(self._get_browser_session_dir(), f'fpl_{self.manager_id}.json')
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).replace(tzinfo=None)
            # Odoo datetimes have no microseconds
            mtime = mtime.replace(microsecond=0)
        except OSError:
            return False
        if self.browser_session_date and mtime <= self.browser_session_date:
            return False
        return path

    def _import_browser_session_file(self):
        path = self._get_new_browser_session_file()
        if not path:
            return
        try:
            with open(path, encoding='utf-8') as session_file:
                state = json.load(session_file)
        except (OSError, ValueError) as e:
            _logger.warning("Unreadable FPL browser session %s: %s", path, e)
            return
        self.sudo().write({'browser_session': json.dumps(state), 'browser_session_date': fields.Datetime.now()})
        _logger.info("FPL browser session of manager %s imported from %s", self.manager_id, path)

    def _fpl_browser_login(self):
        """Get a new token chain with the browser session (silent OIDC login).

        :return: ``(status, token_data)``; status is 'ok', 'login_required'
            (the SSO session expired: it is forgotten) or 'no_session'
        """
        self.ensure_one()
        self._import_browser_session_file()
        manager = self.sudo()
        if not manager.browser_session:
            return 'no_session', None
        client_id = self.env['ir.config_parameter'].sudo().get_param('fantasy_premier_league.oidc_client_id')
        result = self._run_browser_auth({
            'storage_state': json.loads(manager.browser_session),
            'client_id': client_id or None,
        })
        status = result.get('status')
        if status == 'login_required':
            _logger.warning("FPL browser session of manager %s expired", self.manager_id)
            manager.write({'browser_session': False})
            return status, None
        if status != 'ok':
            if result.get('storage_state'):
                # The SSO cookies rotate on use: keep the latest ones
                manager.write({'browser_session': json.dumps(result['storage_state'])})
                self.env.cr.commit()
            raise UserError(_("FPL login with the browser session failed: %s", result.get('message')))
        # The SSO cookies rotate on every use (the previous ones no longer
        # work): saved and committed first, whatever happens next.
        manager.write({
            'browser_session': json.dumps(result.get('storage_state') or json.loads(manager.browser_session)),
            'browser_session_date': fields.Datetime.now(),
        })
        self.env.cr.commit()
        try:
            token_data = FPLApiClient.exchange_authorization_code(
                result['code'], result['code_verifier'], result['redirect_uri'], client_id=client_id,
            )
        except FPLApiException as e:
            raise UserError(_("FPL login with the browser session failed: %s", e)) from e
        return status, token_data

    @api.model
    def _run_browser_auth(self, payload):
        """Run scripts/fpl_browser_auth.py --silent in a separate process.

        Playwright cannot run inside an Odoo worker (gevent / prefork break
        Chromium's process management).
        """
        try:
            process = subprocess.run(
                [sys.executable, BROWSER_AUTH_SCRIPT, '--silent'],
                input=json.dumps(payload), capture_output=True, text=True, timeout=BROWSER_AUTH_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return {'status': 'error', 'message': f'timeout after {BROWSER_AUTH_TIMEOUT}s'}
        except OSError as e:
            return {'status': 'error', 'message': str(e)}
        try:
            return json.loads(process.stdout)
        except ValueError:
            _logger.error("fpl_browser_auth.py failed (exit %s): %s", process.returncode, process.stderr[-2000:])
            return {'status': 'error', 'message': f'browser script failed (exit {process.returncode})'}

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------

    @api.model
    def sync_manager_data(self, refresh_token=None, manager_id=None, public_only=False):
        """Sync a manager from the FPL API, creating the record when needed.

        Public endpoints (entry summary, history, leagues) only need the
        manager id. Private endpoints (/me/, /my-team/) use a newly pasted
        refresh token, or the token stored on the record; they are skipped
        when no token is available.

        :return: the synced manager
        """
        manager = self.browse()
        if manager_id:
            try:
                manager = self.search([('manager_id', '=', int(manager_id))], limit=1)
            except ValueError as e:
                raise UserError(_("The manager ID must be a number.")) from e

        token_data = access_token = False
        if refresh_token:
            token_data = self._fpl_exchange_refresh_token(refresh_token.strip())
            access_token = token_data['access_token']
        elif manager and not public_only and manager.has_fpl_token:
            access_token = manager._get_fpl_access_token()

        player_data = {}
        if access_token:
            try:
                player_data = (self.sync_authenticated_data('get_manager_data', access_token) or {}).get('player') or {}
            except FPLApiException as e:
                raise self._fpl_user_error(_("Failed to get the FPL manager data"), e) from e

        entry = player_data.get('entry') or manager_id
        if not entry:
            raise UserError(_("Could not determine the FPL manager ID. Please provide it."))
        entry = int(entry)
        manager = self.search([('manager_id', '=', entry)], limit=1) or self.create({'manager_id': entry})
        if token_data:
            manager._store_fpl_tokens(token_data)

        manager._sync_from_api(access_token, player_data)
        _logger.info("Synced FPL manager %s (private data: %s)", entry, bool(access_token))
        return manager

    @api.model
    def cron_sync_manager_data(self):
        """Sync all managers: public data always, private data when the stored token still works"""
        for manager in self.search([]):
            public_only = False
            if manager.has_fpl_token:
                try:
                    # Refresh (and commit the rotated token) outside the savepoint below
                    manager._get_fpl_access_token()
                except UserError as e:
                    # A rejected token is cleared (and reported) by _get_fpl_access_token
                    public_only = True
                    _logger.warning("FPL token refresh failed for manager %s: %s", manager.manager_id, e)
            # No savepoint here: the token rotation commits, which would break it.
            # Everything before this manager is already committed.
            try:
                self.sync_manager_data(manager_id=manager.manager_id, public_only=public_only)
                self.env.cr.commit()
            except Exception:  # noqa: BLE001 - one manager must not block the others
                self.env.cr.rollback()
                _logger.exception("Cron sync failed for manager %s", manager.manager_id)

    def _sync_from_api(self, access_token, player_data):
        """Fetch every endpoint of the manager concurrently, then store the data."""
        self.ensure_one()
        calls = {
            'summary': ('get_entry_summary', (self.manager_id,)),
            'history': ('get_entry_history', (self.manager_id,)),
        }
        if access_token:
            calls['my_team'] = ('get_manager_team', (self.manager_id,))
        results, errors = self._fpl_fetch_many(calls, access_token=access_token)
        if 'summary' in errors:
            raise self._fpl_user_error(_("Failed to sync manager data"), errors['summary']) from errors['summary']
        for key, error in errors.items():
            _logger.warning("FPL manager %s: '%s' could not be fetched: %s", self.manager_id, key, error)

        summary = results.get('summary') or {}
        my_team = results.get('my_team') or {}
        vals = {'last_sync_date': fields.Datetime.now()}
        vals.update(self._prepare_manager_data_vals(player_data))
        vals.update(self._prepare_entry_summary_vals(summary))
        vals.update(self._prepare_manager_team_vals(my_team))
        changed = self._fpl_changed_vals(self, vals)
        if changed:
            self.write(changed)

        leagues = summary.get('leagues') or {}
        self._sync_leagues({'classic': leagues.get('classic') or [], 'h2h': leagues.get('h2h') or []})
        if 'history' in results:
            self._sync_entry_history(results['history'] or {})
        if my_team:
            self._sync_manager_chips(my_team.get('chips') or [])
            self._sync_manager_picks(my_team.get('picks') or [])
        self._sync_league_standings()

    def _prepare_manager_data_vals(self, data):
        """Values from the private /me/ endpoint"""
        if not data:
            return {}
        gender = data.get('gender')
        country = self.env['res.country'].search(
            [('code', '=', REGION_ISO_BY_ID.get(data.get('region')))], limit=1,
        ) if data.get('region') else self.env['res.country']
        return {
            'default_event': data.get('default_event'),
            'dirty': bool(data.get('dirty')),
            'date_of_birth': self._fpl_parse_date(data.get('date_of_birth')),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'full_name': f"{data.get('first_name') or ''} {data.get('last_name') or ''}".strip(),
            'email': data.get('email'),
            'gender': gender if gender in dict(self._fields['gender'].selection) else False,
            'manager_data_id': data.get('id'),
            'region': data.get('region'),
            'country_id': country.id,
            'entry_email': bool(data.get('entry_email')),
            'entry_language': data.get('entry_language'),
            'sso_id': data.get('sso_id'),
        }

    def _prepare_entry_summary_vals(self, data):
        """Values from the public /entry/<id>/ endpoint"""
        if not data:
            return {}
        vals = self._fpl_filter_vals(self._name, data, exclude={
            'id', 'kits', 'leagues', 'joined_time', 'favourite_team', 'last_deadline_bank', 'last_deadline_value',
        })
        favourite_team = self.env['fpl.teams']._get_teams_by_api_id().get(data.get('favourite_team'))
        vals.update({
            'joined_time': self._fpl_parse_datetime(data.get('joined_time')),
            'favourite_team': favourite_team.id if favourite_team else False,
            'last_deadline_bank': self._fpl_tenths(data.get('last_deadline_bank')),
            'last_deadline_value': self._fpl_tenths(data.get('last_deadline_value')),
        })
        return vals

    def _prepare_manager_team_vals(self, data):
        """Values from the private /my-team/<id>/ endpoint"""
        if not data:
            return {}
        transfers = data.get('transfers') or {}
        return {
            'picks_last_updated': self._fpl_parse_datetime(data.get('picks_last_updated')),
            'cost': transfers.get('cost'),
            'status': transfers.get('status'),
            'limit': transfers.get('limit'),
            'made': transfers.get('made'),
            'bank': self._fpl_tenths(transfers.get('bank')),
            'value': self._fpl_tenths(transfers.get('value')),
        }

    def _sync_leagues(self, leagues_by_type):
        """Leagues of the manager and their active phases (overall + current month)."""
        self.ensure_one()
        Leagues = self.env['fpl.leagues']
        phases = {phase.phase_id: phase for phase in self.env['fpl.phases'].search([])}
        existing = {(league.type, league.league_id): league
                    for league in Leagues.search([('manager_id', '=', self.id)])}
        vals_by_key, active_phases_by_key = {}, {}
        for league_type, leagues in leagues_by_type.items():
            for league in leagues:
                key = (league_type, league['id'])
                vals = self._fpl_filter_vals(Leagues._name, league, exclude={'id', 'created', 'active_phases'})
                vals.update({
                    'type': league_type,
                    'league_id': league['id'],
                    'manager_id': self.id,
                    'created': self._fpl_parse_datetime(league.get('created')),
                })
                vals_by_key[key] = vals
                active_phases_by_key[key] = league.get('active_phases') or []

        leagues = self._fpl_upsert(Leagues, existing, vals_by_key, unlink_missing=True)

        ActivePhases = self.env['fpl.league.active.phases']
        existing_phases = {
            (phase.league_id.id, phase.phase_id.id): phase
            for phase in ActivePhases.search([('league_id', 'in', [league.id for league in leagues.values()])])
        }
        phase_vals = {}
        for key, active_phases in active_phases_by_key.items():
            league = leagues[key]
            for active_phase in active_phases:
                phase = phases.get(active_phase.get('phase'))
                if not phase:
                    continue
                phase_vals[(league.id, phase.id)] = {
                    'league_id': league.id,
                    'phase_id': phase.id,
                    'rank': active_phase.get('rank'),
                    'last_rank': active_phase.get('last_rank'),
                    'rank_sort': active_phase.get('rank_sort'),
                    'total': active_phase.get('total'),
                    'rank_count': active_phase.get('rank_count'),
                    'entry_percentile_rank': active_phase.get('entry_percentile_rank'),
                }
        self._fpl_upsert(ActivePhases, existing_phases, phase_vals, unlink_missing=True)

    def _sync_league_standings(self):
        """First page of the standings of every active phase of the classic leagues."""
        self.ensure_one()
        Standings = self.env['fpl.league.standings.results']
        leagues = self.env['fpl.leagues'].search([('manager_id', '=', self.id), ('type', '=', 'classic')])
        calls = {
            (league, active_phase.phase_id): (
                'get_league_standings', (league.league_id, 1, active_phase.phase_id.phase_id),
            )
            for league in leagues
            for active_phase in league.active_phases_ids
            if active_phase.phase_id
        }
        results, errors = self._fpl_fetch_many(calls)
        for (league, phase), error in errors.items():
            _logger.warning("Standings of league %s (%s) could not be fetched: %s", league.name, phase.name, error)

        existing = {
            (row.league_id.id, row.phase_id.id, row.result_id): row
            for row in Standings.search([('league_id', 'in', leagues.ids)])
        }
        vals_by_key = {}
        last_updated = {}
        for (league, phase), data in results.items():
            data = data or {}
            for row in (data.get('standings') or {}).get('results') or []:
                vals_by_key[(league.id, phase.id, row.get('entry'))] = {
                    'league_id': league.id,
                    'phase_id': phase.id,
                    'result_id': row.get('entry'),
                    'entry': row.get('entry'),
                    'entry_name': row.get('entry_name'),
                    'player_name': row.get('player_name'),
                    'club_badge_src': row.get('club_badge_src'),
                    'event_total': row.get('event_total'),
                    'rank': row.get('rank'),
                    'last_rank': row.get('last_rank'),
                    'rank_sort': row.get('rank_sort'),
                    'total': row.get('total'),
                    'has_played': bool(row.get('has_played')),
                }
            if data.get('last_updated_data'):
                last_updated[league] = self._fpl_parse_datetime(data['last_updated_data'])

        self._fpl_upsert(Standings, existing, vals_by_key)
        # Remove the entries that left the first page, and the standings of
        # phases that are not active anymore; but keep the rows of a standing
        # that could not be fetched this time.
        failed = {(league.id, phase.id) for league, phase in errors}
        obsolete = Standings.browse([
            row.id for key, row in existing.items() if key not in vals_by_key and key[:2] not in failed
        ])
        obsolete.unlink()
        for league, date in last_updated.items():
            if league.last_updated_data != date:
                league.last_updated_data = date

    def _sync_entry_history(self, data):
        self.ensure_one()
        History = self.env['fpl.entry.history']
        events = self.env['fpl.events']._get_events_by_api_id()
        # The API only returns the current season: never touch the rows of previous seasons
        existing = {
            history.event_id.id: history
            for history in History.search([
                ('manager_id', '=', self.id), ('event_id', 'in', [event.id for event in events.values()]),
            ])
        }
        vals_by_key = {}
        for history in data.get('current') or []:
            event = events.get(history.get('event'))
            if not event:
                continue
            vals_by_key[event.id] = {
                'manager_id': self.id,
                'event_id': event.id,
                'points': history.get('points'),
                'total_points': history.get('total_points'),
                'rank': history.get('rank'),
                'rank_sort': history.get('rank_sort'),
                'overall_rank': history.get('overall_rank'),
                'bank': self._fpl_tenths(history.get('bank')),
                'value': self._fpl_tenths(history.get('value')),
                'event_transfers': history.get('event_transfers'),
                'event_transfer_cost': history.get('event_transfers_cost'),
                'points_on_bench': history.get('points_on_bench'),
            }
        self._fpl_upsert(History, existing, vals_by_key, unlink_missing=True)

        Past = self.env['fpl.past']
        existing_past = {past.season_name: past for past in Past.search([('manager_id', '=', self.id)])}
        past_vals = {
            past.get('season_name'): {
                'manager_id': self.id,
                'season_name': past.get('season_name'),
                'total_poinst': past.get('total_points'),
                'rank': past.get('rank'),
            }
            for past in data.get('past') or []
        }
        self._fpl_upsert(Past, existing_past, past_vals, unlink_missing=True)

    def _sync_manager_chips(self, chips):
        self.ensure_one()
        ManagerChips = self.env['fpl.manager.chips']
        chips_by_api_id = {chip.chip_id: chip for chip in self.env['fpl.chips'].search([])}
        statuses = dict(ManagerChips._fields['status_for_entry'].selection)
        existing = {chip.chip_id.id: chip for chip in ManagerChips.search([('manager_id', '=', self.id)])}
        vals_by_key = {}
        for chip in chips:
            chip_record = chips_by_api_id.get(str(chip.get('id')))
            if not chip_record:
                continue
            status = chip.get('status_for_entry')
            if status not in statuses:
                _logger.warning("Unknown chip status_for_entry from FPL API: %s", status)
                status = False
            vals_by_key[chip_record.id] = {
                'manager_id': self.id,
                'chip_id': chip_record.id,
                'status_for_entry': status,
                'played_by_entry': chip.get('played_by_entry'),
                'is_pending': bool(chip.get('is_pending')),
            }
        self._fpl_upsert(ManagerChips, existing, vals_by_key, unlink_missing=True)

    def _sync_manager_picks(self, picks):
        """Make the current squad match the API: players sold since the last
        sync are removed."""
        self.ensure_one()
        Picks = self.env['fpl.picks']
        elements = {
            element.element_id: element
            for element in self.env['fpl.elements'].search([('element_id', 'in', [p.get('element') for p in picks])])
        }
        element_types = self.env['fpl.element.types']._get_types_by_api_id()
        existing = {}
        duplicates = Picks
        for pick in Picks.search([('manager_id', '=', self.id)]):
            if pick.element_id.id in existing:
                duplicates |= pick
            else:
                existing[pick.element_id.id] = pick
        duplicates.unlink()

        vals_by_key = {}
        for pick in picks:
            element = elements.get(pick.get('element'))
            if not element:
                _logger.warning("Unknown FPL element %s in picks of manager %s", pick.get('element'), self.manager_id)
                continue
            element_type = element_types.get(str(pick.get('element_type')))
            vals_by_key[element.id] = {
                'manager_id': self.id,
                'element_id': element.id,
                'element_type_id': element_type.id if element_type else element.element_type_id.id,
                'position': pick.get('position'),
                'multiplier': pick.get('multiplier'),
                'is_captain': bool(pick.get('is_captain')),
                'is_vice_captain': bool(pick.get('is_vice_captain')),
                'selling_price': self._fpl_tenths(pick.get('selling_price')),
                'purchase_price': self._fpl_tenths(pick.get('purchase_price')),
            }
        self._fpl_upsert(Picks, existing, vals_by_key, unlink_missing=True)
