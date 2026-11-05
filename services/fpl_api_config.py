"""FPL API endpoints configuration."""


class FPLApiConfig:
    """Configuration class for FPL API endpoints and settings"""

    BASE_URL = "https://fantasy.premierleague.com/api"

    # OIDC (PingOne) login used by fantasy.premierleague.com
    OIDC_TOKEN_URL = "https://account.premierleague.com/as/token"
    OIDC_CLIENT_ID = "bfcbaf69-aade-4c1b-8f00-c1cb8a193030"

    ENDPOINTS = {
        # Public endpoints (no authentication required)
        'bootstrap_static': '/bootstrap-static/',
        'element_gameweek_live': '/event/{gw_id}/live/',
        'entry_summary': '/entry/{team_id}/',
        'entry_history': '/entry/{team_id}/history/',
        'entry_transfers': '/entry/{team_id}/transfers/',
        'gameweek_picks': '/entry/{team_id}/event/{gw_id}/picks/',
        'fixtures': '/fixtures/',
        'gameweek_fixtures': '/fixtures/?event={gw_id}',
        'element_summary': '/element-summary/{player_id}/',
        'league_standings': '/leagues-classic/{league_id}/standings/?page_standings={page_id}&phase={phase}',
        'head_to_head_standings': '/leagues-h2h/{league_id}/standings/?page_standings={page_id}&phase={phase}',
        'event_status': '/event-status/',
        'dream_team': '/dream-team/{event_id}/',
        'set_piece_notes': '/team/set-piece-notes/',
        'league_cup_status': '/league/{league_id}/cup-status/',
        'most_valuable_teams': '/stats/most-valuable-teams/',
        'best_leagues': '/stats/best-leagues/',

        # Private endpoints (authentication required)
        'manager_team': '/my-team/{team_id}/',
        'manager_team_gameweek': '/my-team/{team_id}/?event={gw_id}',
        'manager_data': '/me/',
        'manager_transfers_current': '/my-team/{team_id}/transfers/',
    }

    AUTHENTICATED_ENDPOINTS = {
        'manager_team',
        'manager_team_gameweek',
        'manager_data',
        'manager_transfers_current',
    }

    @classmethod
    def get_endpoint_url(cls, endpoint_key, **params):
        """Full URL of an endpoint, with its ``{placeholders}`` replaced."""
        if endpoint_key not in cls.ENDPOINTS:
            raise ValueError(f"Unknown endpoint: {endpoint_key}")
        return cls.BASE_URL + cls.ENDPOINTS[endpoint_key].format_map(
            {key: str(value) for key, value in params.items()}
        )

    @classmethod
    def requires_auth(cls, endpoint_key):
        return endpoint_key in cls.AUTHENTICATED_ENDPOINTS
