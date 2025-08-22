from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from .master_data import REGIONS
from .fpl_api_mixin import FPLApiMixin
from ..services.fpl_api_client import FPLApiException
import logging

_logger = logging.getLogger(__name__)

class FPLManagerTeam(models.Model, FPLApiMixin):
    _name = 'fpl.manager.team'
    _description = 'FPL Manager Team'
    
    manager_id = fields.Char(string=_('Manager ID'))
    #Manager Data
    manager_data_id = fields.Integer(string=_('Manager Data ID'))
    date_of_birth = fields.Date(string=_('Date of Birth'))
    default_event = fields.Integer(string=_('Default Event'))
    dirty = fields.Boolean(string=_('Dirty'))
    first_name = fields.Char(string=_('First Name'))
    last_name = fields.Char(string=_('Last Name'))
    full_name = fields.Char(string=_('Full Name'))
    email = fields.Char(string=_('Email'))
    gender = fields.Selection([('M', _('Male')), ('F', _('Female') )], string=_('Gender'))
    manger_data_id = fields.Integer(string=_('ID'))
    region = fields.Char(string=_('Region'))
    country_id = fields.Many2one('res.country', string=_('Country'))
    entry_email = fields.Char(string=_('Entry Email'))
    entry_language = fields.Char(string=_('Entry Language'))
    sso_id = fields.Char(string=_('SSO ID'))
    #Manager Entry Summary
    joined_time = fields.Datetime(string=_('Joined Time'))
    started_event = fields.Integer(string=_('Started Event'))
    favourite_team = fields.Many2one('fpl.teams', string=_('Favourite Team'))
    player_first_name = fields.Char(string=_('Player First Name'))
    player_last_name = fields.Char(string=_('Player Last Name'))
    player_region_id = fields.Char(string=_('Player Region ID'))
    player_region_name = fields.Char(string=_('Player Region Name'))
    player_region_iso_code_short = fields.Char(string=_('Player Region ISO Code Short'))
    player_region_iso_code_long = fields.Char(string=_('Player Region ISO Code Long'))
    years_active = fields.Integer(string=_('Years Active'))
    summary_overall_points = fields.Integer(string=_('Summary Overall Points'))
    summary_overall_rank = fields.Integer(string=_('Summary Overall Rank'))
    summary_event_points = fields.Integer(string=_('Summary Event Points'))
    summary_event_rank = fields.Integer(string=_('Summary Event Rank'))
    current_event = fields.Integer(string=_('Current Event'))
    name = fields.Char(string=_('Name'))
    name_change_blocked = fields.Boolean(string=_('Name Change Blocked'))
    kits = fields.Char(string=_('Kits'))
    last_deadline_bank = fields.Integer(string=_('Last Deadline Bank'))
    last_deadline_value = fields.Integer(string=_('Last Deadline Value'))
    last_deadline_total_transfers = fields.Integer(string=_('Last Deadline Total Transfers'))
    club_badge_src = fields.Char(string=_('Club Badge Src'))
    league_classic_ids = fields.One2many('fpl.leagues', 'manager_id', string=_('League Classic IDs'), domain=[('type', '=', 'classic')])
    league_h2h_ids = fields.One2many('fpl.leagues', 'manager_id', string=_('League H2H IDs'), domain=[('type', '=', 'h2h')])
    pick_ids = fields.One2many('fpl.picks', 'manager_id', string=_('Element IDs'))
    manager_chip_ids = fields.One2many('fpl.manager.chips', 'manager_id', string=_('Manager Chips'))
    picks_last_updated = fields.Datetime(string=_('Picks Last Updated'))

    #Transfer Info
    cost = fields.Integer(string=_('Cost'))
    status = fields.Char(string=_('Status'))
    limit = fields.Integer(string=_('Transfers Limit'))
    made = fields.Float(string=_('Transfers Made'))
    bank = fields.Float(string=_('In the Bank'))
    value = fields.Float(string=_('Squad Value'))
    
    
    @api.model
    def sync_manager_data(self, cookies, x_api_authorization, manager_id=None):
        """Sync manager data from FPL API using authentication and create/update record"""
        try:
            # manager_data = self.with_context().sync_authenticated_data(
            #     'get_manager_data', 
            #     cookies, 
            #     x_api_authorization
            # )
            
            manager_data = {
                "player": {
                    "date_of_birth": "1999-04-28",
                    "default_event": 2,
                    "dirty": False,
                    "first_name": "Khai",
                    "gender": "M",
                    "id": 66737509,
                    "last_name": "Dang",
                    "region": 234,
                    "email": "dangkhai2849@gmail.com",
                    "entry": 894358,
                    "entry_email": False,
                    "entry_language": None,
                    "sso_id": "5abbd00e-d223-4e81-88ba-fa15847f55a8"
                },
                "watched": []
                }

            entry_summary = {
                "id": 894358,
                "joined_time": "2025-07-22T05:21:47.259864Z",
                "started_event": 1,
                "favourite_team": 7,
                "player_first_name": "Khai",
                "player_last_name": "Dang",
                "player_region_id": 234,
                "player_region_name": "Vietnam",
                "player_region_iso_code_short": "VN",
                "player_region_iso_code_long": "VNM",
                "years_active": 3,
                "summary_overall_points": 50,
                "summary_overall_rank": 5781357,
                "summary_event_points": 50,
                "summary_event_rank": 5781366,
                "current_event": 1,
                "leagues": {
                    "classic": [
                        {
                            "id": 7,
                            "name": "Chelsea",
                            "short_name": "team-7",
                            "created": "2025-07-20T23:14:28.429685Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "s",
                            "scoring": "c",
                            "admin_entry": None,
                            "start_event": 1,
                            "entry_can_leave": False,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 761588,
                            "entry_percentile_rank": 60,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 456824,
                                    "last_rank": 0,
                                    "rank_sort": 459388,
                                    "total": 50,
                                    "league_id": 7,
                                    "rank_count": 761588,
                                    "entry_percentile_rank": 60
                                },
                                {
                                    "phase": 2,
                                    "rank": 456825,
                                    "last_rank": 0,
                                    "rank_sort": 459389,
                                    "total": 50,
                                    "league_id": 7,
                                    "rank_count": 761589,
                                    "entry_percentile_rank": 60
                                }
                            ],
                            "entry_rank": 456824,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 254,
                            "name": "Vietnam",
                            "short_name": "region-234",
                            "created": "2025-07-20T23:14:32.876326Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "s",
                            "scoring": "c",
                            "admin_entry": None,
                            "start_event": 1,
                            "entry_can_leave": False,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 10530,
                            "entry_percentile_rank": 65,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 6433,
                                    "last_rank": 0,
                                    "rank_sort": 6505,
                                    "total": 50,
                                    "league_id": 254,
                                    "rank_count": 10530,
                                    "entry_percentile_rank": 65
                                },
                                {
                                    "phase": 2,
                                    "rank": 6433,
                                    "last_rank": 0,
                                    "rank_sort": 6505,
                                    "total": 50,
                                    "league_id": 254,
                                    "rank_count": 10530,
                                    "entry_percentile_rank": 65
                                }
                            ],
                            "entry_rank": 6433,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 276,
                            "name": "Gameweek 1",
                            "short_name": "event-1",
                            "created": "2025-07-20T23:14:33.264422Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "s",
                            "scoring": "c",
                            "admin_entry": None,
                            "start_event": 1,
                            "entry_can_leave": False,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": False,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 9469100,
                            "entry_percentile_rank": 65,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 5781356,
                                    "last_rank": 0,
                                    "rank_sort": 5809553,
                                    "total": 50,
                                    "league_id": 276,
                                    "rank_count": 9469100,
                                    "entry_percentile_rank": 65
                                },
                                {
                                    "phase": 2,
                                    "rank": 5781348,
                                    "last_rank": 0,
                                    "rank_sort": 5809545,
                                    "total": 50,
                                    "league_id": 276,
                                    "rank_count": 9469082,
                                    "entry_percentile_rank": 65
                                }
                            ],
                            "entry_rank": 5781356,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 314,
                            "name": "Overall",
                            "short_name": "overall",
                            "created": "2025-07-20T23:14:33.933835Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "s",
                            "scoring": "c",
                            "admin_entry": None,
                            "start_event": 1,
                            "entry_can_leave": False,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 9469102,
                            "entry_percentile_rank": 65,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 5781357,
                                    "last_rank": 0,
                                    "rank_sort": 5809554,
                                    "total": 50,
                                    "league_id": 314,
                                    "rank_count": 9469102,
                                    "entry_percentile_rank": 65
                                },
                                {
                                    "phase": 2,
                                    "rank": 5781350,
                                    "last_rank": 0,
                                    "rank_sort": 5809547,
                                    "total": 50,
                                    "league_id": 314,
                                    "rank_count": 9469086,
                                    "entry_percentile_rank": 65
                                }
                            ],
                            "entry_rank": 5781357,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 333,
                            "name": "Second Chance",
                            "short_name": "sc",
                            "created": "2025-07-20T23:14:34.276586Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "s",
                            "scoring": "c",
                            "admin_entry": None,
                            "start_event": 21,
                            "entry_can_leave": False,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": False,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": None,
                            "entry_percentile_rank": None,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 0,
                                    "last_rank": 0,
                                    "rank_sort": 0,
                                    "total": 0,
                                    "league_id": 333,
                                    "rank_count": None,
                                    "entry_percentile_rank": None
                                },
                                {
                                    "phase": 2,
                                    "rank": 0,
                                    "last_rank": 0,
                                    "rank_sort": 0,
                                    "total": 0,
                                    "league_id": 333,
                                    "rank_count": None,
                                    "entry_percentile_rank": None
                                }
                            ],
                            "entry_rank": 0,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 561,
                            "name": "YouTube.com/FPLtips",
                            "short_name": None,
                            "created": "2025-07-21T11:33:10.868406Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "x",
                            "scoring": "c",
                            "admin_entry": 4464,
                            "start_event": 1,
                            "entry_can_leave": True,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 51954,
                            "entry_percentile_rank": 70,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 33916,
                                    "last_rank": 0,
                                    "rank_sort": 34319,
                                    "total": 50,
                                    "league_id": 561,
                                    "rank_count": 51954,
                                    "entry_percentile_rank": 70
                                },
                                {
                                    "phase": 2,
                                    "rank": 33916,
                                    "last_rank": 0,
                                    "rank_sort": 34319,
                                    "total": 50,
                                    "league_id": 561,
                                    "rank_count": 51954,
                                    "entry_percentile_rank": 70
                                }
                            ],
                            "entry_rank": 33916,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 1623,
                            "name": "YouTube.com/FPLFocal",
                            "short_name": None,
                            "created": "2025-07-21T11:36:06.025961Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "x",
                            "scoring": "c",
                            "admin_entry": 200,
                            "start_event": 1,
                            "entry_can_leave": True,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 62506,
                            "entry_percentile_rank": 75,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 44197,
                                    "last_rank": 0,
                                    "rank_sort": 45118,
                                    "total": 50,
                                    "league_id": 1623,
                                    "rank_count": 62506,
                                    "entry_percentile_rank": 75
                                },
                                {
                                    "phase": 2,
                                    "rank": 44196,
                                    "last_rank": 0,
                                    "rank_sort": 45117,
                                    "total": 50,
                                    "league_id": 1623,
                                    "rank_count": 62505,
                                    "entry_percentile_rank": 75
                                }
                            ],
                            "entry_rank": 44197,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 35207,
                            "name": "ShakeThatAston",
                            "short_name": None,
                            "created": "2025-07-21T12:55:52.667144Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "x",
                            "scoring": "c",
                            "admin_entry": 72698,
                            "start_event": 1,
                            "entry_can_leave": True,
                            "entry_can_admin": False,
                            "entry_can_invite": True,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 229,
                            "entry_percentile_rank": 70,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 152,
                                    "last_rank": 0,
                                    "rank_sort": 154,
                                    "total": 50,
                                    "league_id": 35207,
                                    "rank_count": 229,
                                    "entry_percentile_rank": 70
                                },
                                {
                                    "phase": 2,
                                    "rank": 152,
                                    "last_rank": 0,
                                    "rank_sort": 154,
                                    "total": 50,
                                    "league_id": 35207,
                                    "rank_count": 229,
                                    "entry_percentile_rank": 70
                                }
                            ],
                            "entry_rank": 152,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 39776,
                            "name": "Official /r/FantasyPL Classic League",
                            "short_name": None,
                            "created": "2025-07-21T13:07:52.424514Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "x",
                            "scoring": "c",
                            "admin_entry": 217222,
                            "start_event": 1,
                            "entry_can_leave": True,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 35623,
                            "entry_percentile_rank": 70,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 24694,
                                    "last_rank": 0,
                                    "rank_sort": 25138,
                                    "total": 50,
                                    "league_id": 39776,
                                    "rank_count": 35623,
                                    "entry_percentile_rank": 70
                                },
                                {
                                    "phase": 2,
                                    "rank": 24696,
                                    "last_rank": 0,
                                    "rank_sort": 25140,
                                    "total": 50,
                                    "league_id": 39776,
                                    "rank_count": 35625,
                                    "entry_percentile_rank": 70
                                }
                            ],
                            "entry_rank": 24694,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 475909,
                            "name": "League Nhà Quê SS7 - Classic",
                            "short_name": None,
                            "created": "2025-07-28T02:03:01.262268Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "x",
                            "scoring": "c",
                            "admin_entry": 2535381,
                            "start_event": 1,
                            "entry_can_leave": True,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 29,
                            "entry_percentile_rank": 70,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 20,
                                    "last_rank": 0,
                                    "rank_sort": 20,
                                    "total": 50,
                                    "league_id": 475909,
                                    "rank_count": 29,
                                    "entry_percentile_rank": 70
                                },
                                {
                                    "phase": 2,
                                    "rank": 20,
                                    "last_rank": 0,
                                    "rank_sort": 20,
                                    "total": 50,
                                    "league_id": 475909,
                                    "rank_count": 29,
                                    "entry_percentile_rank": 70
                                }
                            ],
                            "entry_rank": 20,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 475912,
                            "name": "League Nhà Quê SS7 - Month",
                            "short_name": None,
                            "created": "2025-07-28T02:03:15.079395Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "x",
                            "scoring": "c",
                            "admin_entry": 2535381,
                            "start_event": 1,
                            "entry_can_leave": True,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 29,
                            "entry_percentile_rank": 70,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 20,
                                    "last_rank": 0,
                                    "rank_sort": 20,
                                    "total": 50,
                                    "league_id": 475912,
                                    "rank_count": 29,
                                    "entry_percentile_rank": 70
                                },
                                {
                                    "phase": 2,
                                    "rank": 20,
                                    "last_rank": 0,
                                    "rank_sort": 20,
                                    "total": 50,
                                    "league_id": 475912,
                                    "rank_count": 29,
                                    "entry_percentile_rank": 70
                                }
                            ],
                            "entry_rank": 20,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 577318,
                            "name": "Chuồng Thỏ",
                            "short_name": None,
                            "created": "2025-07-30T09:14:41.372905Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "x",
                            "scoring": "c",
                            "admin_entry": 2975058,
                            "start_event": 1,
                            "entry_can_leave": True,
                            "entry_can_admin": False,
                            "entry_can_invite": True,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 1068,
                            "entry_percentile_rank": 75,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 755,
                                    "last_rank": 0,
                                    "rank_sort": 778,
                                    "total": 50,
                                    "league_id": 577318,
                                    "rank_count": 1068,
                                    "entry_percentile_rank": 75
                                },
                                {
                                    "phase": 2,
                                    "rank": 755,
                                    "last_rank": 0,
                                    "rank_sort": 778,
                                    "total": 50,
                                    "league_id": 577318,
                                    "rank_count": 1068,
                                    "entry_percentile_rank": 75
                                }
                            ],
                            "entry_rank": 755,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 817012,
                            "name": "Báo Bóng Đá Fantasy",
                            "short_name": None,
                            "created": "2025-08-05T04:34:26.355480Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "x",
                            "scoring": "c",
                            "admin_entry": 3962818,
                            "start_event": 1,
                            "entry_can_leave": True,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 1372,
                            "entry_percentile_rank": 75,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 981,
                                    "last_rank": 0,
                                    "rank_sort": 1005,
                                    "total": 50,
                                    "league_id": 817012,
                                    "rank_count": 1372,
                                    "entry_percentile_rank": 75
                                },
                                {
                                    "phase": 2,
                                    "rank": 981,
                                    "last_rank": 0,
                                    "rank_sort": 1005,
                                    "total": 50,
                                    "league_id": 817012,
                                    "rank_count": 1372,
                                    "entry_percentile_rank": 75
                                }
                            ],
                            "entry_rank": 981,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 856738,
                            "name": "Planning Makes Perfect",
                            "short_name": None,
                            "created": "2025-08-05T19:47:33.835534Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "x",
                            "scoring": "c",
                            "admin_entry": 6586,
                            "start_event": 1,
                            "entry_can_leave": True,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 235,
                            "entry_percentile_rank": None,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 0,
                                    "last_rank": 0,
                                    "rank_sort": 0,
                                    "total": 0,
                                    "league_id": 856738,
                                    "rank_count": 235,
                                    "entry_percentile_rank": None
                                },
                                {
                                    "phase": 2,
                                    "rank": 0,
                                    "last_rank": 0,
                                    "rank_sort": 0,
                                    "total": 0,
                                    "league_id": 856738,
                                    "rank_count": 235,
                                    "entry_percentile_rank": None
                                }
                            ],
                            "entry_rank": 0,
                            "entry_last_rank": 0
                        },
                        {
                            "id": 1445607,
                            "name": "Chelscenes Mini-League",
                            "short_name": None,
                            "created": "2025-08-13T11:17:59.689111Z",
                            "closed": False,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "x",
                            "scoring": "c",
                            "admin_entry": 6146093,
                            "start_event": 1,
                            "entry_can_leave": True,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": True,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": 1370,
                            "entry_percentile_rank": 65,
                            "active_phases": [
                                {
                                    "phase": 1,
                                    "rank": 838,
                                    "last_rank": 0,
                                    "rank_sort": 850,
                                    "total": 50,
                                    "league_id": 1445607,
                                    "rank_count": 1370,
                                    "entry_percentile_rank": 65
                                },
                                {
                                    "phase": 2,
                                    "rank": 838,
                                    "last_rank": 0,
                                    "rank_sort": 850,
                                    "total": 50,
                                    "league_id": 1445607,
                                    "rank_count": 1370,
                                    "entry_percentile_rank": 65
                                }
                            ],
                            "entry_rank": 838,
                            "entry_last_rank": 0
                        }
                    ],
                    "h2h": [
                        {
                            "id": 475922,
                            "name": "League Nhà Quê SS7 - H2H",
                            "short_name": None,
                            "created": "2025-07-28T02:03:34.382008Z",
                            "closed": True,
                            "rank": None,
                            "max_entries": None,
                            "league_type": "x",
                            "scoring": "h",
                            "admin_entry": 2535381,
                            "start_event": 1,
                            "entry_can_leave": False,
                            "entry_can_admin": False,
                            "entry_can_invite": False,
                            "has_cup": False,
                            "cup_league": None,
                            "cup_qualified": None,
                            "rank_count": None,
                            "entry_percentile_rank": None,
                            "active_phases": [],
                            "entry_rank": 15,
                            "entry_last_rank": 0
                        }
                    ],
                    "cup": {
                        "matches": [],
                        "status": {
                            "qualification_event": None,
                            "qualification_numbers": None,
                            "qualification_rank": None,
                            "qualification_state": None
                        },
                        "cup_league": None
                    },
                    "cup_matches": []
                },
                "name": "U know chippy chips?",
                "name_change_blocked": False,
                "entered_events": [
                    1
                ],
                "kit": None,
                "last_deadline_bank": 5,
                "last_deadline_value": 1000,
                "last_deadline_total_transfers": 0,
                "club_badge_src": None
            }

            manager_team_data = {
    "picks": [
        {
            "element": 220,
            "position": 1,
            "multiplier": 1,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 1,
            "selling_price": 50,
            "purchase_price": 50
        },
        {
            "element": 505,
            "position": 2,
            "multiplier": 1,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 2,
            "selling_price": 55,
            "purchase_price": 55
        },
        {
            "element": 568,
            "position": 3,
            "multiplier": 1,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 2,
            "selling_price": 55,
            "purchase_price": 55
        },
        {
            "element": 191,
            "position": 4,
            "multiplier": 1,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 2,
            "selling_price": 40,
            "purchase_price": 40
        },
        {
            "element": 261,
            "position": 5,
            "multiplier": 1,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 2,
            "selling_price": 45,
            "purchase_price": 45
        },
        {
            "element": 235,
            "position": 6,
            "multiplier": 1,
            "is_captain": False,
            "is_vice_captain": True,
            "element_type": 3,
            "selling_price": 105,
            "purchase_price": 105
        },
        {
            "element": 299,
            "position": 7,
            "multiplier": 1,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 3,
            "selling_price": 65,
            "purchase_price": 65
        },
        {
            "element": 381,
            "position": 8,
            "multiplier": 2,
            "is_captain": True,
            "is_vice_captain": False,
            "element_type": 3,
            "selling_price": 145,
            "purchase_price": 145
        },
        {
            "element": 449,
            "position": 9,
            "multiplier": 1,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 3,
            "selling_price": 90,
            "purchase_price": 90
        },
        {
            "element": 283,
            "position": 10,
            "multiplier": 1,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 4,
            "selling_price": 75,
            "purchase_price": 75
        },
        {
            "element": 64,
            "position": 11,
            "multiplier": 1,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 4,
            "selling_price": 90,
            "purchase_price": 90
        },
        {
            "element": 470,
            "position": 12,
            "multiplier": 0,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 1,
            "selling_price": 40,
            "purchase_price": 40
        },
        {
            "element": 242,
            "position": 13,
            "multiplier": 0,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 3,
            "selling_price": 50,
            "purchase_price": 50
        },
        {
            "element": 575,
            "position": 14,
            "multiplier": 0,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 2,
            "selling_price": 45,
            "purchase_price": 45
        },
        {
            "element": 252,
            "position": 15,
            "multiplier": 0,
            "is_captain": False,
            "is_vice_captain": False,
            "element_type": 4,
            "selling_price": 45,
            "purchase_price": 45
        }
    ],
    "picks_last_updated": "2025-08-20T05:19:17.793585Z",
    "chips": [
        {
            "id": 4,
            "status_for_entry": "available",
            "played_by_entry": [],
            "name": "bboost",
            "number": 1,
            "start_event": 1,
            "stop_event": 19,
            "chip_type": "team",
            "is_pending": False
        },
        {
            "id": 5,
            "status_for_entry": "available",
            "played_by_entry": [],
            "name": "3xc",
            "number": 1,
            "start_event": 1,
            "stop_event": 19,
            "chip_type": "team",
            "is_pending": False
        },
        {
            "id": 1,
            "status_for_entry": "available",
            "played_by_entry": [],
            "name": "wildcard",
            "number": 1,
            "start_event": 2,
            "stop_event": 19,
            "chip_type": "transfer",
            "is_pending": False
        },
        {
            "id": 3,
            "status_for_entry": "available",
            "played_by_entry": [],
            "name": "freehit",
            "number": 1,
            "start_event": 2,
            "stop_event": 19,
            "chip_type": "transfer",
            "is_pending": False
        }
    ],
    "transfers": {
        "cost": 4,
        "status": "cost",
        "limit": 1,
        "made": 0,
        "bank": 5,
        "value": 995
    }
}
            if not manager_data:
                raise UserError(_("No manager data received from API"))
            
            api_manager_id = None
            if 'player' in manager_data and isinstance(manager_data['player'], dict):
                api_manager_id = str(manager_data['player'].get('entry'))
            elif 'entry' in manager_data:
                api_manager_id = str(manager_data.get('entry'))
            elif manager_id:
                api_manager_id = str(manager_id)
            
            if not api_manager_id:
                raise UserError(_("Could not extract manager_id from API response"))
            
            manager_team = self.search([('manager_id', '=', api_manager_id)], limit=1)
            if not manager_team:
                manager_team = self.create({'manager_id': api_manager_id})
                _logger.info(f"Created new manager team record for ID: {api_manager_id}")
            else:
                _logger.info(f"Found existing manager team record for ID: {api_manager_id}")
            
            # entry_summary = manager_team.sync_from_fpl_api(
            #     'get_entry_summary', 
            #     api_manager_id
            # )
            
            manager_team._update_from_manager_data(manager_data.get('player', {}))
            manager_team._update_from_entry_summary(entry_summary, manager_team.id)
            manager_team._update_from_manager_team(manager_team_data, manager_team.id)
            
            _logger.info(f"Successfully synced data for manager {api_manager_id}")
            return manager_team
                
        except FPLApiException as e:
            _logger.error(f"Failed to sync manager data: {str(e)}")
            raise UserError(f"Failed to sync manager data: {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error during sync: {str(e)}")
            raise UserError(f"Unexpected error during sync: {str(e)}")
    
    def _update_from_manager_team(self, data, manager_id):
        """Update model fields from manager team API response"""
        if not data:
            return
        update_vals = {
            'picks_last_updated': datetime.fromisoformat(data.get('picks_last_updated').replace('Z', '')),
            "cost": data.get('transfers', {}).get('cost'),
            "status": data.get('transfers', {}).get('status'),
            "limit": data.get('transfers', {}).get('limit'),
            "made": data.get('transfers', {}).get('made'),
            "bank": data.get('transfers', {}).get('bank') / 10,
            "value": data.get('transfers', {}).get('value') / 10,
            'pick_ids': self._update_manager_picks_data(data.get('picks', []), manager_id),
            'manager_chip_ids': self._update_manager_chips_data(data.get('chips', []), manager_id),
        }
        if update_vals:
            self.write(update_vals)

    def _update_manager_picks_data(self, picks, manager_id):
        self.env['fpl.picks'].search([('manager_id', '=', manager_id)]).unlink()
        if not picks:
            return
        picks_vals = []
        for pick in picks:
            element = self.env['fpl.elements'].search([('element_id', '=', pick.get('element'))], limit=1)
            if not element:
                continue
            pick_vals = {
                'element_id': element.id,
                'position': pick.get('position'),
                'multiplier': pick.get('multiplier'),
                'is_captain': pick.get('is_captain'),
                'is_vice_captain': pick.get('is_vice_captain'),
                'element_type_id':self.env['fpl.element.types'].search([('element_type_id', '=', pick.get('element_type'))], limit=1).id,
                'selling_price': pick.get('selling_price') / 10,
                'purchase_price': pick.get('purchase_price') / 10,
            }
            picks_vals.append((0, 0, pick_vals))
        return picks_vals

    def _update_manager_chips_data(self, chips, manager_id):
        self.env['fpl.manager.chips'].search([('manager_id', '=', manager_id)]).unlink()
        if not chips:
            return
        chips_vals = []
        for chip in chips:
            chip_id = self.env['fpl.chips'].search([('chip_id', '=', chip.get('id'))], limit=1)
            if not chip_id:
                continue
            chip_vals = {
                'chip_id': chip_id.id,
                'status_for_entry': chip.get('status_for_entry'),
                'played_by_entry': chip.get('played_by_entry'),
                'is_pending': chip.get('is_pending'),
            }
            chips_vals.append((0, 0, chip_vals))
        return chips_vals
    
    def _update_from_manager_data(self, data):
        """Update model fields from manager data API response"""
        if not data:
            return
        region_code = next((region['iso_code_short'] for region in REGIONS if region['id'] == data.get('region')), None)
        update_vals = {
            'default_event': data.get('default_event'),
            'dirty': data.get('dirty'),
            'date_of_birth': data.get('date_of_birth'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'full_name': f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
            'email': data.get('email'),
            'gender': data.get('gender'),
            'manager_data_id': data.get('id'),
            'region': data.get('region'),
            'country_id': self.env['res.country'].search([('code', '=', region_code)], limit=1).id or False,
            'entry_email': data.get('entry_email'),
            'entry_language': data.get('entry_language'),
        }
                
        if update_vals:
            self.write(update_vals)
    
    def _update_from_entry_summary(self, data, manager_id):
        """Update model fields from entry summary API response"""
        if not data:
            return
        
        league_classic_ids = self._update_manager_leagues_data(data.get('leagues', []).get('classic'), manager_id, 'classic')
        league_h2h_ids = self._update_manager_leagues_data(data.get('leagues', []).get('h2h'), manager_id, 'h2h')
        
        update_vals = {
            'favourite_team': self.env['fpl.teams'].search([('team_id', '=', data.get('favourite_team'))], limit=1).id or False,
            'joined_time': datetime.fromisoformat(data.get('joined_time').replace('Z', '')),
            'started_event': data.get('started_event'),
            'player_first_name': data.get('player_first_name'),
            'player_last_name': data.get('player_last_name'),
            'player_region_id': data.get('player_region_id'),
            'player_region_name': data.get('player_region_name'),
            'years_active': data.get('years_active'),
            'summary_overall_points': data.get('summary_overall_points'),
            'summary_overall_rank': data.get('summary_overall_rank'),
            'summary_event_points': data.get('summary_event_points'),
            'summary_event_rank': data.get('summary_event_rank'),
            'current_event': data.get('current_event'),
            'name': data.get('name'),
            'name_change_blocked': data.get('name_change_blocked'),
            'last_deadline_bank': data.get('last_deadline_bank') / 10,
            'last_deadline_value': data.get('last_deadline_value') / 10,
            'last_deadline_total_transfers': data.get('last_deadline_total_transfers'),
            'league_classic_ids': [(6, 0, league_classic_ids)],
            'league_h2h_ids': [(6, 0, league_h2h_ids)],
        }
        
        if update_vals:
            self.write(update_vals)

    def _update_manager_leagues_data(self, datas, manager_id, type):
        exist_manager_leagues = self.env['fpl.leagues'].search([('manager_id', '=', manager_id), ('type', '=', type)])
        if exist_manager_leagues:
            exist_manager_leagues.active_phases_ids.unlink()
            exist_manager_leagues.unlink()

        league_vals = []
        for league in datas:
            val = {
                'type': type,
                'league_id': league.get('id'),
                'name': league.get('name'),
                'short_name': league.get('short_name'),
                'created': datetime.fromisoformat(league.get('created').replace('Z', '')),
                'closed': league.get('closed'),
                'max_entries': league.get('max_entries'),
                'league_type': league.get('league_type'),
                'scoring': league.get('scoring'),
                'admin_entry': league.get('admin_entry'),
                'start_event': league.get('start_event'),
                'entry_can_leave': league.get('entry_can_leave'),
                'entry_can_admin': league.get('entry_can_admin'),
                'entry_can_invite': league.get('entry_can_invite'),
                'has_cup': league.get('has_cup'),
                'cup_league': league.get('cup_league'),
                'cup_qualified': league.get('cup_qualified'),
                'rank_count': league.get('rank_count'),
                'entry_percentile_rank': league.get('entry_percentile_rank'),
                'entry_rank': league.get('entry_rank'),
                'entry_last_rank': league.get('entry_last_rank'),
                'active_phases_ids': self._get_league_phases_val(league.get('active_phases')),
                'entry_rank': league.get('entry_rank'),
                'entry_last_rank': league.get('entry_last_rank'),
            }
            league_vals.append(val)
        if league_vals:
            league_ids = self.env['fpl.leagues'].create(league_vals)
            return league_ids.ids
                
    
    def _get_league_phases_val(self, phases):
        val = []
        for phase in phases:
            phase_id = self.env['fpl.phases'].search([('phase_id', '=', phase.get('phase'))], limit=1)
            if not phase_id:
                continue
            phase_val = {
                'phase_id': phase_id.id,
                'rank': phase.get('rank'),
                'last_rank': phase.get('last_rank'),
                'rank_sort': phase.get('rank_sort'),
                'total': phase.get('total'),
                'rank_count': phase.get('rank_count'),
                'entry_percentile_rank': phase.get('entry_percentile_rank'),
            }
            val.append((0, 0, phase_val))
        return val