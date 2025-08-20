from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .fpl_api_mixin import FPLApiMixin
from ..services.fpl_api_client import FPLApiException
import logging

_logger = logging.getLogger(__name__)

class FPLManagerTeam(models.Model, FPLApiMixin):
    _name = 'fpl.manager.team'
    _description = 'FPL Manager Team'
    
    manager_id = fields.Char(string=_('Manager ID'))
    #Manager Data
    date_of_birth = fields.Date(string=_('Date of Birth'))
    default_event = fields.Integer(string=_('Default Event'))
    dirty = fields.Boolean(string=_('Dirty'))
    first_name = fields.Char(string=_('First Name'))
    last_name = fields.Char(string=_('Last Name'))
    full_name = fields.Char(string=_('Full Name'))
    email = fields.Char(string=_('Email'))
    gender = fields.Selection([('M', _('Male')), ('F', _('Female') )], string=_('Gender'))
    _id = fields.Char(string=_('ID'))
    region = fields.Char(string=_('Region'))
    entry_email = fields.Char(string=_('Entry Email'))
    entry_language = fields.Char(string=_('Entry Language'))
    sso_id = fields.Char(string=_('SSO ID'))
    
    #Manager Entry Summary
    joined_time = fields.Datetime(string=_('Joined Time'))
    started_event = fields.Integer(string=_('Started Event'))
    favourite_team = fields.Many2one('epl.teams', string=_('Favourite Team'))
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
    league_ids = fields.One2many('fpl.leagues', 'manager_id', string=_('League IDs'))
    pick_ids = fields.One2many('fpl.picks', 'manager_id', string=_('Element IDs'))
    manager_chips = fields.One2many('fpl.manager.chips', 'manager_id', string=_('Manager Chips'))
    
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
            # Get manager personal data first to extract manager_id
            manager_data = self.with_context().sync_authenticated_data(
                'get_manager_data', 
                cookies, 
                x_api_authorization
            )
            
            if not manager_data:
                raise UserError(_("No manager data received from API"))
            
            # Extract manager_id from API response
            api_manager_id = None
            if 'player' in manager_data and isinstance(manager_data['player'], dict):
                api_manager_id = str(manager_data['player'].get('entry'))
            elif 'entry' in manager_data:
                api_manager_id = str(manager_data.get('entry'))
            elif manager_id:
                api_manager_id = str(manager_id)
            
            if not api_manager_id:
                raise UserError(_("Could not extract manager_id from API response"))
            
            # Find or create manager team record
            manager_team = self.search([('manager_id', '=', api_manager_id)], limit=1)
            if not manager_team:
                manager_team = self.create({'manager_id': api_manager_id})
                _logger.info(f"Created new manager team record for ID: {api_manager_id}")
            else:
                _logger.info(f"Found existing manager team record for ID: {api_manager_id}")
            
            # Get manager entry summary
            entry_summary = manager_team.sync_from_fpl_api(
                'get_entry_summary', 
                api_manager_id
            )
            
            # Update model fields with API data
            manager_team._update_from_manager_data(manager_data)
            manager_team._update_from_entry_summary(entry_summary)
            
            _logger.info(f"Successfully synced data for manager {api_manager_id}")
            return manager_team
                
        except FPLApiException as e:
            _logger.error(f"Failed to sync manager data: {str(e)}")
            raise UserError(f"Failed to sync manager data: {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error during sync: {str(e)}")
            raise UserError(f"Unexpected error during sync: {str(e)}")
    
    def _update_from_manager_data(self, data):
        """Update model fields from manager data API response"""
        if not data:
            return
            
        update_vals = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'full_name': f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
            'email': data.get('email'),
            'gender': data.get('gender'),
            '_id': str(data.get('id', '')),
            'region': data.get('region'),
            'entry_email': data.get('entry_email'),
            'entry_language': data.get('entry_language'),
        }
        
        # Remove None values
        update_vals = {k: v for k, v in update_vals.items() if v is not None}
        
        if update_vals:
            self.write(update_vals)
    
    def _update_from_entry_summary(self, data):
        """Update model fields from entry summary API response"""
        if not data:
            return
            
        update_vals = {
            'joined_time': data.get('joined_time'),
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
            'last_deadline_bank': data.get('last_deadline_bank'),
            'last_deadline_value': data.get('last_deadline_value'),
            'last_deadline_total_transfers': data.get('last_deadline_total_transfers'),
        }
        
        # Remove None values
        update_vals = {k: v for k, v in update_vals.items() if v is not None}
        
        if update_vals:
            self.write(update_vals)
    
    # @api.model
    # def sync_bootstrap_data(self):
    #     """Sync basic FPL data (teams, players, events)"""
    #     try:
    #         data_service = self.get_data_service()
    #         bootstrap_data = data_service.sync_bootstrap_data()
    #
    #         # Process teams
    #         self._process_teams_data(bootstrap_data.get('teams', []))
    #
    #         # Process players
    #         self._process_elements_data(bootstrap_data.get('elements', []))
    #
    #         # Process events (gameweeks)
    #         self._process_events_data(bootstrap_data.get('events', []))
    #
    #         _logger.info("Successfully synced bootstrap data")
    #         return True
    #
    #     except Exception as e:
    #         _logger.error(f"Failed to sync bootstrap data: {str(e)}")
    #         raise UserError(f"Failed to sync bootstrap data: {str(e)}")