"""HTTP client for the official Fantasy Premier League API.

Design notes:

* One ``requests.Session`` per thread (connection pooling / keep-alive),
  instead of a brand new session for every single call. The FPL API is hit
  hundreds of times per cron run, so re-using TCP/TLS connections matters.
* Transient failures (429 / 5xx / connection resets) are retried with an
  exponential back-off by urllib3, so one hiccup does not abort a whole sync.
* :func:`fetch_many` runs independent GET requests concurrently. It only does
  network I/O - it never touches the ORM - so it is safe to call from inside
  an Odoo transaction: the results are processed afterwards in the caller's
  thread.
* Messages raised here are plain English: the models catch
  :class:`FPLApiException` and re-raise a translated ``UserError``.
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .fpl_api_config import FPLApiConfig

_logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

_thread_local = threading.local()


class FPLApiException(Exception):
    """Raised for any FPL API failure (HTTP error, timeout, invalid JSON...)."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


def get_session():
    """Return the HTTP session of the current thread (created on first use)."""
    session = getattr(_thread_local, 'session', None)
    if session is None:
        session = requests.Session()
        retry = Retry(
            total=3,
            connect=3,
            read=2,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({'GET'}),
            respect_retry_after_header=True,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=4, pool_maxsize=16)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        session.headers.update(DEFAULT_HEADERS)
        _thread_local.session = session
    return session


def http_get_json(url, headers=None, timeout=DEFAULT_TIMEOUT, error_cls=FPLApiException):
    """GET ``url`` and return the decoded JSON body.

    :raises error_cls: on network error, non-2xx status or invalid JSON
    """
    try:
        response = get_session().get(url, headers=headers, timeout=timeout)
    except requests.exceptions.RequestException as e:
        _logger.warning("HTTP request failed for %s: %s", url, e)
        raise error_cls(f"Request to {url} failed: {e}") from e
    if not response.ok:
        _logger.warning("HTTP %s for %s", response.status_code, url)
        raise error_cls(f"HTTP {response.status_code} for {url}", status_code=response.status_code)
    try:
        return response.json()
    except ValueError as e:
        _logger.warning("Invalid JSON returned by %s", url)
        raise error_cls(f"Invalid JSON returned by {url}") from e


def http_get_bytes(url, timeout=DEFAULT_TIMEOUT):
    """GET ``url`` and return the raw body, or None when it does not exist.

    The Premier League image CDN (S3) answers 403, not 404, for a missing file.

    :raises FPLApiException: on network error or other non-2xx status
    """
    try:
        response = get_session().get(url, timeout=timeout)
    except requests.exceptions.RequestException as e:
        raise FPLApiException(f"Request to {url} failed: {e}") from e
    if response.status_code in (403, 404):
        return None
    if not response.ok:
        raise FPLApiException(f"HTTP {response.status_code} for {url}", status_code=response.status_code)
    return response.content


def fetch_many(jobs, max_workers=8):
    """Run independent callables concurrently and collect their results.

    :param dict jobs: ``{key: callable}``; each callable performs HTTP only
    :return: ``(results, errors)`` - two dicts keyed like ``jobs``
    """
    results, errors = {}, {}
    if not jobs:
        return results, errors
    if len(jobs) == 1 or max_workers <= 1:
        for key, job in jobs.items():
            try:
                results[key] = job()
            except Exception as e:  # noqa: BLE001 - reported to the caller
                errors[key] = e
        return results, errors

    with ThreadPoolExecutor(max_workers=min(max_workers, len(jobs)), thread_name_prefix='fpl_http') as executor:
        futures = {key: executor.submit(job) for key, job in jobs.items()}
        for key, future in futures.items():
            try:
                results[key] = future.result()
            except Exception as e:  # noqa: BLE001 - reported to the caller
                errors[key] = e
    return results, errors


class FPLApiClient:
    """Thin wrapper around the FPL REST endpoints listed in :class:`FPLApiConfig`."""

    def __init__(self, x_api_authorization=None):
        """
        :param str x_api_authorization: ``Bearer <token>`` for the private endpoints
        """
        self.x_api_authorization = x_api_authorization

    def _make_request(self, endpoint_key, **params):
        if FPLApiConfig.requires_auth(endpoint_key) and not self.x_api_authorization:
            raise FPLApiException(f"Authentication required for endpoint: {endpoint_key}")
        url = FPLApiConfig.get_endpoint_url(endpoint_key, **params)
        headers = {'X-API-Authorization': self.x_api_authorization} if self.x_api_authorization else None
        _logger.debug("FPL API request: %s", url)
        return http_get_json(url, headers=headers)

    @staticmethod
    def _token_request(data, what):
        try:
            response = requests.post(FPLApiConfig.OIDC_TOKEN_URL, data=data, timeout=DEFAULT_TIMEOUT)
        except requests.exceptions.RequestException as e:
            _logger.error("FPL %s request failed: %s", what, e)
            raise FPLApiException(f"{what} request failed: {e}") from e
        if response.status_code != 200:
            _logger.error("FPL %s rejected (%s): %s", what, response.status_code, response.text[:200])
            raise FPLApiException(
                f"FPL {what} rejected: invalid, expired or revoked (HTTP {response.status_code})",
                status_code=response.status_code,
            )
        try:
            token_data = response.json()
        except ValueError as e:
            raise FPLApiException("Invalid JSON in FPL token response") from e
        if not token_data.get('access_token'):
            raise FPLApiException("No access token in FPL token response")
        return token_data

    @staticmethod
    def exchange_authorization_code(code, code_verifier, redirect_uri, client_id=None):
        """Redeem an OIDC authorization code (PKCE) for a new token chain.

        :return: token response with ``access_token``, ``expires_in`` and ``refresh_token``
        """
        return FPLApiClient._token_request({
            'grant_type': 'authorization_code',
            'code': code,
            'code_verifier': code_verifier,
            'redirect_uri': redirect_uri,
            'client_id': client_id or FPLApiConfig.OIDC_CLIENT_ID,
        }, 'authorization code exchange')

    @staticmethod
    def refresh_access_token(refresh_token, client_id=None):
        """Exchange an OIDC refresh token for a new access token.

        :return: token response with ``access_token``, ``expires_in`` and the
            rotated ``refresh_token``
        """
        return FPLApiClient._token_request({
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id or FPLApiConfig.OIDC_CLIENT_ID,
        }, 'token refresh')

    # Public endpoints (no authentication required)

    def get_bootstrap_static(self):
        """Players, teams, events, phases, chips..."""
        return self._make_request('bootstrap_static')

    def get_element_gameweek_live(self, gw_id):
        """Live stats + points breakdown of every player for a gameweek."""
        return self._make_request('element_gameweek_live', gw_id=gw_id)

    def get_entry_summary(self, team_id):
        return self._make_request('entry_summary', team_id=team_id)

    def get_entry_history(self, team_id):
        return self._make_request('entry_history', team_id=team_id)

    def get_entry_transfers(self, team_id):
        return self._make_request('entry_transfers', team_id=team_id)

    def get_gameweek_picks(self, team_id, gw_id):
        return self._make_request('gameweek_picks', team_id=team_id, gw_id=gw_id)

    def get_gameweek_fixtures(self, gw_id=None):
        """Fixtures of one gameweek, or of the whole season when ``gw_id`` is empty."""
        if gw_id:
            return self._make_request('gameweek_fixtures', gw_id=gw_id)
        return self._make_request('fixtures')

    def get_element_summary(self, player_id):
        return self._make_request('element_summary', player_id=player_id)

    def get_league_standings(self, league_id, page_id=1, phase=1):
        return self._make_request('league_standings', league_id=league_id, page_id=page_id, phase=phase)

    def get_head_to_head_standings(self, league_id, page_id=1, phase=1):
        return self._make_request('head_to_head_standings', league_id=league_id, page_id=page_id, phase=phase)

    def get_event_status(self):
        return self._make_request('event_status')

    def get_dream_team(self, event_id):
        return self._make_request('dream_team', event_id=event_id)

    def get_set_piece_notes(self):
        return self._make_request('set_piece_notes')

    def get_league_cup_status(self, league_id):
        return self._make_request('league_cup_status', league_id=league_id)

    def get_most_valuable_teams(self):
        return self._make_request('most_valuable_teams')

    def get_best_leagues(self):
        return self._make_request('best_leagues')

    # Private endpoints (authentication required)

    def get_manager_team(self, team_id):
        return self._make_request('manager_team', team_id=team_id)

    def get_manager_team_gameweek(self, team_id, gw_id):
        return self._make_request('manager_team_gameweek', team_id=team_id, gw_id=gw_id)

    def get_manager_data(self):
        return self._make_request('manager_data')

    def get_manager_transfers_current(self, team_id):
        return self._make_request('manager_transfers_current', team_id=team_id)
