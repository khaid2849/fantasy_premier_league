"""
FPL API Client for making HTTP requests to Fantasy Premier League API
"""

import requests
import json
import logging
from odoo import _
from .fpl_api_config import FPLApiConfig

_logger = logging.getLogger(__name__)

class FPLApiException(Exception):
    """Custom exception for FPL API errors"""
    pass

class FPLApiClient:
    """Main API client for interacting with FPL endpoints"""
    
    def __init__(self, cookies=None, x_api_authorization=None):
        """
        Initialize the FPL API client
        
        Args:
            cookies (str): Authentication cookies for private endpoints
            x_api_authorization (str): X-API-Authorization header for private endpoints
        """
        self.cookies = cookies
        self.x_api_authorization = x_api_authorization
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
        
        # Add authentication headers if provided
        if self.cookies:
            self.session.headers.update({'Cookie': self.cookies})
        if self.x_api_authorization:
            self.session.headers.update({'X-API-Authorization': self.x_api_authorization})
    
    def _make_request(self, endpoint_key, **params):
        """Make HTTP request to FPL API"""
        try:
            url = FPLApiConfig.get_endpoint_url(endpoint_key, **params)
            
            # Check if endpoint requires authentication
            if FPLApiConfig.requires_auth(endpoint_key):
                if not self.cookies and not self.x_api_authorization:
                    raise FPLApiException(_("Authentication required for endpoint: %s") % endpoint_key)
            
            _logger.info(f"Making request to: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"HTTP request failed for {endpoint_key}: {str(e)}")
            raise FPLApiException(_("API request failed: %s") % str(e))
        except json.JSONDecodeError as e:
            _logger.error(f"JSON decode error for {endpoint_key}: {str(e)}")
            raise FPLApiException(_("Invalid JSON response from API"))
        except Exception as e:
            _logger.error(f"Unexpected error for {endpoint_key}: {str(e)}")
            raise FPLApiException(_("Unexpected API error: %s") % str(e))

    # Public API Methods (no authentication required)
    
    def get_bootstrap_static(self):
        """Get bootstrap static data (players, teams, events, etc.)"""
        return self._make_request('bootstrap_static')
    
    def get_element_gameweek_live(self, gw_id):
        """Get live gameweek data for all players"""
        return self._make_request('element_gameweek_live', gw_id=gw_id)
    
    def get_entry_summary(self, team_id):
        """Get entry summary for a team"""
        return self._make_request('entry_summary', team_id=team_id)
    
    def get_entry_history(self, team_id):
        """Get entry history for a team"""
        return self._make_request('entry_history', team_id=team_id)
    
    def get_entry_transfers(self, team_id):
        """Get transfer history for a team"""
        return self._make_request('entry_transfers', team_id=team_id)
    
    def get_gameweek_picks(self, team_id, gw_id):
        """Get team picks for a specific gameweek"""
        return self._make_request('gameweek_picks', team_id=team_id, gw_id=gw_id)
    
    def get_gameweek_fixtures(self, gw_id=None):
        """Get fixtures for a gameweek"""
        if gw_id:
            return self._make_request('gameweek_fixtures', gw_id=gw_id)
        return self._make_request('gameweek_fixtures')
    
    def get_element_summary(self, player_id):
        """Get detailed player summary"""
        return self._make_request('element_summary', player_id=player_id)
    
    def get_league_standings(self, league_id, page_id=1, phase=1):
        """Get league standings"""
        return self._make_request('league_standings', 
                                league_id=league_id, page_id=page_id, phase=phase)
    
    def get_head_to_head_standings(self, league_id, page_id=1, phase=1):
        """Get head-to-head league standings"""
        return self._make_request('head_to_head_standings', 
                                league_id=league_id, page_id=page_id, phase=phase)
    
    def get_event_status(self):
        """Get current event status"""
        return self._make_request('event_status')
    
    def get_dream_team(self, event_id):
        """Get dream team for an event"""
        return self._make_request('dream_team', event_id=event_id)
    
    def get_set_piece_notes(self):
        """Get set piece taker notes"""
        return self._make_request('set_piece_notes')
    
    def get_league_cup_status(self, league_id):
        """Get league cup status"""
        return self._make_request('league_cup_status', league_id=league_id)
    
    def get_most_valuable_teams(self):
        """Get most valuable teams"""
        return self._make_request('most_valuable_teams')
    
    def get_best_leagues(self):
        """Get best leagues"""
        return self._make_request('best_leagues')

    # Private API Methods (authentication required)
    
    def get_manager_team(self, team_id):
        """Get manager's current team (requires authentication)"""
        return self._make_request('manager_team', team_id=team_id)
    
    def get_manager_team_gameweek(self, team_id, gw_id):
        """Get manager's team for specific gameweek (requires authentication)"""
        return self._make_request('manager_team_gameweek', team_id=team_id, gw_id=gw_id)
    
    def get_manager_data(self):
        """Get manager's personal data (requires authentication)"""
        return self._make_request('manager_data')
    
    def get_manager_transfers_current(self, team_id):
        """Get manager's current gameweek transfers (requires authentication)"""
        return self._make_request('manager_transfers_current', team_id=team_id)

class FPLDataService:
    """High-level service for common FPL data operations"""
    
    def __init__(self, api_client):
        """
        Initialize with an FPL API client
        
        Args:
            api_client (FPLApiClient): Configured API client instance
        """
        self.api_client = api_client
    
    def sync_bootstrap_data(self):
        """
        Synchronize bootstrap data (teams, players, events)
        Returns structured data ready for Odoo model updates
        """
        try:
            data = self.api_client.get_bootstrap_static()
            
            return {
                'teams': data.get('teams', []),
                'elements': data.get('elements', []),
                'events': data.get('events', []),
                'element_types': data.get('element_types', []),
                'phases': data.get('phases', []),
                'game_settings': data.get('game_settings', {}),
                'total_players': data.get('total_players', 0)
            }
        except FPLApiException as e:
            _logger.error(f"Failed to sync bootstrap data: {str(e)}")
            raise
    
    def sync_manager_team_data(self, manager_id, cookies, x_api_authorization):
        """
        Synchronize manager team data including current team and history
        
        Args:
            manager_id (str): FPL manager ID
            cookies (str): Authentication cookies
            x_api_authorization (str): Authorization header
        """
        try:
            # Create authenticated client
            auth_client = FPLApiClient(cookies=cookies, x_api_authorization=x_api_authorization)
            
            # Get manager data
            manager_data = auth_client.get_manager_data()
            current_team = auth_client.get_manager_team(manager_id)
            team_history = auth_client.get_entry_history(manager_id)
            
            return {
                'manager_data': manager_data,
                'current_team': current_team,
                'team_history': team_history
            }
        except FPLApiException as e:
            _logger.error(f"Failed to sync manager team data: {str(e)}")
            raise
    
    def get_current_gameweek(self):
        """Get current gameweek information"""
        try:
            bootstrap_data = self.api_client.get_bootstrap_static()
            events = bootstrap_data.get('events', [])
            
            for event in events:
                if event.get('is_current', False):
                    return event
            
            return None
        except FPLApiException as e:
            _logger.error(f"Failed to get current gameweek: {str(e)}")
            raise