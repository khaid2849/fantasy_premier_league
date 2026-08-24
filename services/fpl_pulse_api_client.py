"""
Client for the Premier League "pulselive" live data API.

This is a separate, unauthenticated public API family from the official FPL
API (fantasy.premierleague.com/api, see fpl_api_client.py). It is used only
for team standings and team form, which the FPL API no longer keeps
up to date within fpl.teams.
"""

import logging

import requests

from odoo import _

_logger = logging.getLogger(__name__)


class FPLPulseLiveApiException(Exception):
    """Custom exception for pulselive API errors"""
    pass


class FPLPulseLiveApiClient:
    """Client for the pulselive.com Premier League standings/team-form API"""

    BASE_URL = "https://sdp-prem-prod.premier-league-prod.pulselive.com/api"
    COMPETITION_ID = 8  # Premier League

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })

    def _get(self, url):
        try:
            _logger.info(f"Making request to: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f"HTTP request failed for {url}: {str(e)}")
            raise FPLPulseLiveApiException(_("Pulse Live API request failed: %s") % str(e))
        except ValueError as e:
            _logger.error(f"JSON decode error for {url}: {str(e)}")
            raise FPLPulseLiveApiException(_("Invalid JSON response from Pulse Live API"))

    def get_standings(self, season):
        """Get current league table standings for a season (e.g. '2026')"""
        url = f"{self.BASE_URL}/v5/competitions/{self.COMPETITION_ID}/seasons/{season}/standings"
        return self._get(url)

    def get_team_form(self, season):
        """Get recent form + next fixture for every team in a season (e.g. '2026')"""
        url = f"{self.BASE_URL}/v1/competitions/{self.COMPETITION_ID}/seasons/{season}/teamform"
        return self._get(url)
