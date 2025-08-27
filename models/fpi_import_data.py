import base64
import logging
import os
import requests

from odoo import models, api
from odoo.exceptions import UserError
from odoo.tools.misc import file_path
from .fpl_api_mixin import FPLApiMixin
from .master_data import REGIONS
from datetime import datetime

_logger = logging.getLogger(__name__)

class FplImportData(models.Model, FPLApiMixin):
    _name = 'fpl.import.data'

    def cron_get_data_boostrap_static(self):
        try:
            bootstrap_static_datas = self.sync_from_fpl_api('get_bootstrap_static')
            
            _logger.info("Starting bootstrap static data sync")
            
            # Sync chips data
            chips_data = bootstrap_static_datas.get('chips', [])
            self._sync_chips_data(chips_data)
            
            # Sync events data
            events_data = bootstrap_static_datas.get('events', [])
            self._sync_events_data(events_data)
            
            # Sync phases data
            phases_data = bootstrap_static_datas.get('phases', [])
            self._sync_phases_data(phases_data)
            
            # Sync teams data
            teams_data = bootstrap_static_datas.get('teams', [])
            self._sync_teams_data(teams_data)
            
            # Sync element types data
            element_types_data = bootstrap_static_datas.get('element_types', [])
            self._sync_element_types_data(element_types_data)
            
            # Sync elements data
            elements_data = bootstrap_static_datas.get('elements', [])
            self._sync_elements_data(elements_data)
            
            _logger.info("Bootstrap static data sync completed successfully")
            
        except Exception as e:
            _logger.error(f"Unexpected error during sync: {str(e)}")
            raise UserError(f"Unexpected error during sync: {str(e)}")
    
    def _sync_chips_data(self, chips_data):
        """Sync chips data from API"""
        chips_model = self.env['fpl.chips']
        for chip_data in chips_data:
            existing_chip = chips_model.search([('chip_id', '=', str(chip_data.get('id')))], limit=1)
            vals = {
                    'chip_id': str(chip_data.get('id')),
                    'name': chip_data.get('name'),
                    'number': chip_data.get('number'),
                    'start_event': chip_data.get('start_event'),
                    'stop_event': chip_data.get('stop_event'),
                    'chip_type': chip_data.get('chip_type'),
                    'is_bench_boost': True if chip_data.get('name') == 'bboost' else False,
                    'is_wildcard': True if chip_data.get('name') == 'wildcard' else False,
                    'is_free_hit': True if chip_data.get('name') == 'freehit' else False,
                    'is_triple_captain': True if chip_data.get('name') == '3xc' else False,
                }
            if existing_chip:
                existing_chip.write(vals)
            else:
                chips_model.create(vals)
        _logger.info(f"Synced {len(chips_data)} chips")
    
    def _prase_datetime_values(self, time_val):
        time_val = datetime.fromisoformat(time_val.replace('Z', ''))
        return time_val
                

    def _sync_events_data(self, events_data):
        """Sync events data from API"""
        events_model = self.env['fpl.events']
        for event_data in events_data:
            existing_event = events_model.search([('event_id', '=', event_data.get('id'))], limit=1)
            
            vals = {
                'event_id': event_data.get('id'),
                'name': event_data.get('name'),
                'deadline_time': self._prase_datetime_values(event_data.get('deadline_time')) if event_data.get('deadline_time') else False,
                'release_time': self._prase_datetime_values(event_data.get('release_time')) if event_data.get('release_time') else False,
                'average_entry_score': event_data.get('average_entry_score'),
                'finished': event_data.get('finished', False),
                'data_checked': event_data.get('data_checked', False),
                'highest_scoring_entry': event_data.get('highest_scoring_entry'),
                'deadline_time_epoch': event_data.get('deadline_time_epoch'),
                'deadline_time_game_offset': event_data.get('deadline_time_game_offset'),
                'highest_score': event_data.get('highest_score'),
                'is_previous': event_data.get('is_previous', False),
                'is_current': event_data.get('is_current', False),
                'is_next': event_data.get('is_next', False),
                'cup_leagues_created': event_data.get('cup_leagues_created', False),
                'h2h_ko_matches_created': event_data.get('h2h_ko_matches_created', False),
                'can_enter': event_data.get('can_enter', False),
                'can_manage': event_data.get('can_manage', False),
                'released': event_data.get('released', False),
                'ranked_count': event_data.get('ranked_count'),
                'most_selected': event_data.get('most_selected'),
                'most_transferred_in': event_data.get('most_transferred_in'),
                'transfers_made': event_data.get('transfers_made'),
                'most_captained': event_data.get('most_captained'),
                'most_vice_captained': event_data.get('most_vice_captained'),
            }
            if existing_event:
                existing_event.write(vals)
                event_record = existing_event
            else:
                event_record = events_model.create(vals)
            
            # Handle chip_plays for this event
            chip_plays_data = event_data.get('chip_plays', [])
            if chip_plays_data:
                self._sync_event_chip_plays(event_record, chip_plays_data)
        
        _logger.info(f"Synced {len(events_data)} events")
    
    def _sync_event_chip_plays(self, event_record, chip_plays_data):
        """Sync chip plays data for an event"""
        chip_plays_model = self.env['fpl.event.chip.plays']
        
        existing_chip_plays = chip_plays_model.search([('event_id', '=', event_record.id)])
        existing_chip_plays.unlink()
        
        for chip_play_data in chip_plays_data:
            vals = {
                'event_id': event_record.id,
                'chip_name': chip_play_data.get('chip_name'),
                'num_played': chip_play_data.get('num_played', 0),
            }
            chip_plays_model.create(vals)
    
    def _sync_phases_data(self, phases_data):
        """Sync phases data from API"""
        phases_model = self.env['fpl.phases']
        for phase_data in phases_data:
            existing_phase = phases_model.search([('phase_id', '=', phase_data.get('id'))], limit=1)
            vals = {
                'phase_id': phase_data.get('id'),
                'name': phase_data.get('name'),
                'start_event': phase_data.get('start_event'),
                'stop_event': phase_data.get('stop_event'),
                'highest_score': phase_data.get('highest_score'),
            }
            if existing_phase:
                existing_phase.write(vals)
            else:
                phases_model.create(vals)
        _logger.info(f"Synced {len(phases_data)} phases")
    
    def _get_photo_png(self, code, path):            
        try:
            team_photo_file = file_path(f'{path}/{code}.png')
            if not team_photo_file:
                _logger.warning(f"Photo file not found for code: {code} in path: {path}")
                return False
                
            if not os.path.exists(team_photo_file):
                return False
            
            with open(team_photo_file, 'rb') as file:
                png_content = file.read()
                
            photo_base64 = base64.b64encode(png_content)
            
            return photo_base64
            
        except Exception as e:
            _logger.error(f"Error loading photo for code {code}: {str(e)} in path: {file_path}")
            return False
    
    def _sync_teams_data(self, teams_data):
        """Sync teams data from API"""
        teams_model = self.env['fpl.teams']
        for team_data in teams_data:
            existing_team = teams_model.search([('team_id', '=', team_data.get('id'))], limit=1)
            photo = self._get_photo_png(code=team_data.get('code'), path='fantasy_premier_league/static/src/img/teams_logo')
            vals = {
                'team_id': team_data.get('id'),
                'name': team_data.get('name'),
                'code': team_data.get('code'),
                'form': team_data.get('form'),
                'loss': team_data.get('loss'),
                'played': team_data.get('played'),
                'points': team_data.get('points'),
                'position': team_data.get('position'),
                'short_name': team_data.get('short_name'),
                'strength': team_data.get('strength'),
                'team_division': team_data.get('team_division'),
                'unavailable': team_data.get('unavailable', False),
                'win': team_data.get('win'),
                'draw': team_data.get('draw'),
                'strength_overall_home': team_data.get('strength_overall_home'),
                'strength_overall_away': team_data.get('strength_overall_away'),
                'strength_attack_home': team_data.get('strength_attack_home'),
                'strength_attack_away': team_data.get('strength_attack_away'),
                'strength_defence_home': team_data.get('strength_defence_home'),
                'strength_defence_away': team_data.get('strength_defence_away'),
                'pulse_id': team_data.get('pulse_id'),
                'photo': photo,
            }
            if existing_team:
                existing_team.write(vals)
            else:
                teams_model.create(vals)
        _logger.info(f"Synced {len(teams_data)} teams")
    
    def _sync_element_types_data(self, element_types_data):
        """Sync element types data from API"""
        element_types_model = self.env['fpl.element.types']
        for element_type_data in element_types_data:
            existing_element_type = element_types_model.search([('element_type_id', '=', str(element_type_data.get('id')))], limit=1)
            vals = {
                'element_type_id': str(element_type_data.get('id')),
                'plural_name': element_type_data.get('plural_name'),
                'plural_name_short': element_type_data.get('plural_name_short'),
                'singular_name': element_type_data.get('singular_name'),
                'singular_name_short': element_type_data.get('singular_name_short'),
                'squad_select': element_type_data.get('squad_select'),
                'squad_min_select': element_type_data.get('squad_min_select'),
                'squad_max_select': element_type_data.get('squad_max_select'),
                'squad_min_play': element_type_data.get('squad_min_play'),
                'squad_max_play': element_type_data.get('squad_max_play'),
                'ui_shirt_specific': element_type_data.get('ui_shirt_specific', False),
                'element_count': element_type_data.get('element_count'),
            }
            if existing_element_type:
                existing_element_type.write(vals)
            else:
                element_types_model.create(vals)
        _logger.info(f"Synced {len(element_types_data)} element types")
    
    def _sync_elements_data(self, elements_data):
        """Sync elements data from API"""
        elements_model = self.env['fpl.elements']
        teams_model = self.env['fpl.teams']
        element_types_model = self.env['fpl.element.types']
        
        for element_data in elements_data:
            existing_element = elements_model.search([('element_id', '=', element_data.get('id'))], limit=1)
            
            team_id = None
            if element_data.get('team'):
                team = teams_model.search([('team_id', '=', element_data.get('team'))], limit=1)
                team_id = team.id if team else None
            
            element_type_id = None
            if element_data.get('element_type'):
                element_type = element_types_model.search([('element_type_id', '=', str(element_data.get('element_type')))], limit=1)
                element_type_id = element_type.id if element_type else None
            
            team_join_date = None
            birth_date = None
            if element_data.get('team_join_date'):
                try:
                    team_join_date = datetime.strptime(element_data.get('team_join_date'), '%Y-%m-%d').date()
                except:
                    pass
            if element_data.get('birth_date'):
                try:
                    birth_date = datetime.strptime(element_data.get('birth_date'), '%Y-%m-%d').date()
                except:
                    pass
            
            region_code = next((region['iso_code_short'] for region in REGIONS if region['id'] == element_data.get('region')), None)
            photo = self._get_photo_png(code=element_data.get('opta_code'), path='fantasy_premier_league/static/src/img/players_avatar')
            vals = {
                'element_id': element_data.get('id'),
                'fpl_team_id': team_id,
                'element_type_id': element_type_id,
                'can_transact': element_data.get('can_transact', False),
                'can_select': element_data.get('can_select', False),
                'chance_of_playing_next_round': element_data.get('chance_of_playing_next_round'),
                'chance_of_playing_this_round': element_data.get('chance_of_playing_this_round'),
                'code': element_data.get('code'),
                'cost_change_event': element_data.get('cost_change_event'),
                'cost_change_event_fall': element_data.get('cost_change_event_fall'),
                'cost_change_start': element_data.get('cost_change_start'),
                'cost_change_start_fall': element_data.get('cost_change_start_fall'),
                'dreamteam_count': element_data.get('dreamteam_count'),
                'ep_next': element_data.get('ep_next'),
                'ep_this': element_data.get('ep_this'),
                'event_points': element_data.get('event_points'),
                'first_name': element_data.get('first_name'),
                'form': element_data.get('form'),
                'in_dreamteam': element_data.get('in_dreamteam', False),
                'news': element_data.get('news'),
                'news_added': element_data.get('news_added'),
                'now_cost': element_data.get('now_cost') / 10 if element_data.get('now_cost') else 0,
                'points_per_game': element_data.get('points_per_game'),
                'removed': element_data.get('removed', False),
                'second_name': element_data.get('second_name'),
                'selected_by_percent': element_data.get('selected_by_percent'),
                'special': element_data.get('special', False),
                'squad_number': element_data.get('squad_number'),
                'status': element_data.get('status'),
                'total_points': element_data.get('total_points'),
                'transfers_in': element_data.get('transfers_in'),
                'transfers_in_event': element_data.get('transfers_in_event'),
                'transfers_out': element_data.get('transfers_out'),
                'transfers_out_event': element_data.get('transfers_out_event'),
                'value_form': element_data.get('value_form'),
                'value_season': element_data.get('value_season'),
                'web_name': element_data.get('web_name'),
                'region': element_data.get('region'),
                'country_id': self.env['res.country'].search([('code', '=', region_code)], limit=1).id or False,
                'team_join_date': team_join_date,
                'birth_date': birth_date,
                'has_temporary_code': element_data.get('has_temporary_code', False),
                'opta_code': element_data.get('opta_code'),
                'minutes': element_data.get('minutes'),
                'goals_scored': element_data.get('goals_scored'),
                'assists': element_data.get('assists'),
                'clean_sheets': element_data.get('clean_sheets'),
                'goals_conceded': element_data.get('goals_conceded'),
                'own_goals': element_data.get('own_goals'),
                'penalties_saved': element_data.get('penalties_saved'),
                'penalties_missed': element_data.get('penalties_missed'),
                'yellow_cards': element_data.get('yellow_cards'),
                'red_cards': element_data.get('red_cards'),
                'saves': element_data.get('saves'),
                'bonus': element_data.get('bonus'),
                'bps': element_data.get('bps'),
                'influence': element_data.get('influence'),
                'creativity': element_data.get('creativity'),
                'threat': element_data.get('threat'),
                'ict_index': element_data.get('ict_index'),
                'clearances_blocks_interceptions': element_data.get('clearances_blocks_interceptions'),
                'recoveries': element_data.get('recoveries'),
                'tackles': element_data.get('tackles'),
                'defensive_contribution': element_data.get('defensive_contribution'),
                'starts': element_data.get('starts'),
                'expected_goals': element_data.get('expected_goals'),
                'expected_assists': element_data.get('expected_assists'),
                'expected_goal_involvements': element_data.get('expected_goal_involvements'),
                'expected_goals_conceded': element_data.get('expected_goals_conceded'),
                'influence_rank': element_data.get('influence_rank'),
                'influence_rank_type': element_data.get('influence_rank_type'),
                'creativity_rank': element_data.get('creativity_rank'),
                'creativity_rank_type': element_data.get('creativity_rank_type'),
                'threat_rank': element_data.get('threat_rank'),
                'threat_rank_type': element_data.get('threat_rank_type'),
                'ict_index_rank': element_data.get('ict_index_rank'),
                'ict_index_rank_type': element_data.get('ict_index_rank_type'),
                'corners_and_indirect_freekicks_order': element_data.get('corners_and_indirect_freekicks_order'),
                'corners_and_indirect_freekicks_text': element_data.get('corners_and_indirect_freekicks_text'),
                'direct_freekicks_order': element_data.get('direct_freekicks_order'),
                'direct_freekicks_text': element_data.get('direct_freekicks_text'),
                'penalties_order': element_data.get('penalties_order'),
                'penalties_text': element_data.get('penalties_text'),
                'expected_goals_per_90': element_data.get('expected_goals_per_90'),
                'saves_per_90': element_data.get('saves_per_90'),
                'expected_assists_per_90': element_data.get('expected_assists_per_90'),
                'expected_goal_involvements_per_90': element_data.get('expected_goal_involvements_per_90'),
                'expected_goals_conceded_per_90': element_data.get('expected_goals_conceded_per_90'),
                'goals_conceded_per_90': element_data.get('goals_conceded_per_90'),
                'now_cost_rank': element_data.get('now_cost_rank'),
                'now_cost_rank_type': element_data.get('now_cost_rank_type'),
                'form_rank': element_data.get('form_rank'),
                'form_rank_type': element_data.get('form_rank_type'),
                'points_per_game_rank': element_data.get('points_per_game_rank'),
                'points_per_game_rank_type': element_data.get('points_per_game_rank_type'),
                'selected_rank': element_data.get('selected_rank'),
                'selected_rank_type': element_data.get('selected_rank_type'),
                'starts_per_90': element_data.get('starts_per_90'),
                'clean_sheets_per_90': element_data.get('clean_sheets_per_90'),
                'defensive_contribution_per_90': element_data.get('defensive_contribution_per_90'),
                'photo': photo,
            }
            if existing_element:
                existing_element.write(vals)
            else:
                elements_model.create(vals)
        _logger.info(f"Synced {len(elements_data)} elements")

    
    def download_player_avatar(self):
        player_codes = self.env['fpl.elements'].search([('opta_code', '!=', False)])
        
        # Ensure the players_avatar directory exists
        base_path = file_path('fantasy_premier_league/static/src/img/players_avatar')
        if not os.path.exists(base_path):
            os.makedirs(base_path, exist_ok=True)
            _logger.info(f"Created directory: {base_path}")
        
        for player in player_codes:
            code = player.opta_code.replace('p', '')
            url_image = f'https://resources.premierleague.com/premierleague25/photos/players/110x140/{code}.png'
            
            save_in_path = os.path.join(base_path, f'{player.opta_code}.png')
            
            if not os.path.exists(save_in_path):
                try:
                    download_image = requests.get(url_image, timeout=10)
                    if download_image.status_code == 200:
                        with open(save_in_path, 'wb') as file:
                            file.write(download_image.content)
                        _logger.info(f"Downloaded avatar for player {player.opta_code}")
                    else:
                        _logger.warning(f"Failed to download avatar for player {player.opta_code} - Status code: {download_image.status_code}")
                except Exception as e:
                    _logger.error(f"Error downloading avatar for player {player.opta_code}: {str(e)}")
            else:
                _logger.info(f"Avatar already exists for player {player.opta_code}")