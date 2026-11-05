"""Client for the Premier League "pulselive" live data API.

This is a separate, unauthenticated public API family from the official FPL
API (fantasy.premierleague.com/api, see fpl_api_client.py). It is used only
for team standings and team form, which the FPL API no longer keeps
up to date within fpl.teams.
"""

from .fpl_api_client import FPLApiException, http_get_json


class FPLPulseLiveApiException(FPLApiException):
    """Pulse Live API error (sub-class, so callers may catch either)."""


class FPLPulseLiveApiClient:
    """Client for the pulselive.com Premier League standings/team-form API"""

    BASE_URL = "https://sdp-prem-prod.premier-league-prod.pulselive.com/api"
    COMPETITION_ID = 8  # Premier League

    def _get(self, url):
        return http_get_json(url, error_cls=FPLPulseLiveApiException)

    def get_standings(self, season):
        """Current league table for a season (e.g. '2026')"""
        return self._get(f"{self.BASE_URL}/v5/competitions/{self.COMPETITION_ID}/seasons/{season}/standings")

    def get_team_form(self, season):
        """Recent form + next fixture of every team for a season (e.g. '2026')"""
        return self._get(f"{self.BASE_URL}/v1/competitions/{self.COMPETITION_ID}/seasons/{season}/teamform")
