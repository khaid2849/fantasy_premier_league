import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .fpl_api_mixin import FPLApiMixin
from ..services.fpl_api_client import FPLApiException
from datetime import datetime

_logger = logging.getLogger(__name__)

class FplGameweekFixures(models.Model, FPLApiMixin):
    _name = 'fpl.gameweek.fixtures'

    gameweek = fields.Integer(string=_('Gameweek'))
    code = fields.Char(string=_('Code'))
    event_id = fields.Many2one('fpl.events', string=_('Gameweek'))
    finished = fields.Boolean(string=_('Finished'))
    finished_provisional = fields.Boolean(string=_('Finished provisional'))
    gw_fixture_id = fields.Integer(string=_('Gameweek ID'))
    kickoff_time = fields.Datetime(string=_('Kickoff Time'))
    minutes = fields.Integer(string=_('Minutes'))
    provisional_start_time = fields.Boolean(string=_('Provisional start time'))
    started = fields.Boolean(string=_('Started'))
    team_a = fields.Many2one('fpl.teams', string=_('Away team'))
    team_h = fields.Many2one('fpl.teams', string=_('Home team'))
    team_a_code = fields.Char()
    team_h_code = fields.Char()
    team_a_photo = fields.Image(realted='team_a.photo')
    team_h_photo = fields.Image(realted='team_h.photo')
    team_a_score = fields.Integer(string=_('Away Team Score'))
    team_h_score = fields.Integer(string=_('Home Team Score'))
    team_a_difficulty = fields.Integer(string=_('Away Team Difficulty'))
    team_h_difficulty = fields.Integer(string=_('Home Team Difficulty'))
    pulse_id = fields.Integer(string=_('Pulse id'))

    team_a_goals_scored_ids = fields.One2many('fpl.team.a.goals.scored', 'gw_fixture_id', sting=_('Away Team Goals Scored'))
    team_a_assists_ids = fields.One2many('fpl.team.a.assists', 'gw_fixture_id', sting=_('Away Team Assists'))
    team_a_own_goals_ids = fields.One2many('fpl.team.a.own.goals', 'gw_fixture_id', sting=_('Away Team Own Goals'))
    team_a_penalties_saved_ids = fields.One2many('fpl.team.a.penalties.saved', 'gw_fixture_id', sting=_('Away Team Penalties Saved'))
    team_a_penalties_missed_ids = fields.One2many('fpl.team.a.penalties.missed.scored', 'gw_fixture_id', sting=_('Away Team Penalties Missed'))
    team_a_yellow_cards_ids = fields.One2many('fpl.team.a.yellow.cards', 'gw_fixture_id', sting=_('Away Team Yellow Cards'))
    team_a_red_cards_ids = fields.One2many('fpl.team.a.red.cards', 'gw_fixture_id', sting=_('Away Team Red Cards'))
    team_a_saves_ids = fields.One2many('fpl.team.a.goals.saved', 'gw_fixture_id', sting=_('Away Team Saves'))
    team_a_bonus_ids = fields.One2many('fpl.team.a.bonus', 'gw_fixture_id', sting=_('Away Team Bonus'))
    team_a_bps_ids = fields.One2many('fpl.team.a.bps', 'gw_fixture_id', sting=_('Away Team Bonus Points System'))
    team_a_defensive_contribution_ids = fields.One2many('fpl.team.a.defensive.contribution', 'gw_fixture_id', sting=_('Away Team Defensive Contribution'))

    team_h_goals_scored_ids = fields.One2many('fpl.team.h.goals.scored', 'gw_fixture_id', sting=_('Home Team Goals Scored'))
    team_h_assists_ids = fields.One2many('fpl.team.h.assists', 'gw_fixture_id', sting=_('Home Team Assists'))
    team_h_own_goals_ids = fields.One2many('fpl.team.h.own.goals', 'gw_fixture_id', sting=_('Home Team Own Goals'))
    team_h_penalties_saved_ids = fields.One2many('fpl.team.h.penalties.saved', 'gw_fixture_id', sting=_('Home Team Penalties Saved'))
    team_h_penalties_missed_ids = fields.One2many('fpl.team.h.penalties.missed.scored', 'gw_fixture_id', sting=_('Home Team Penalties Missed'))
    team_h_yellow_cards_ids = fields.One2many('fpl.team.h.yellow.cards', 'gw_fixture_id', sting=_('Home Team Yellow Cards'))
    team_h_red_cards_ids = fields.One2many('fpl.team.h.red.cards', 'gw_fixture_id', sting=_('Home Team Red Cards'))
    team_h_saves_ids = fields.One2many('fpl.team.h.goals.saved', 'gw_fixture_id', sting=_('Home Team Saves'))
    team_h_bonus_ids = fields.One2many('fpl.team.h.bonus', 'gw_fixture_id', sting=_('Home Team Bonus'))
    team_h_bps_ids = fields.One2many('fpl.team.h.bps', 'gw_fixture_id', sting=_('Home Team Bonus Points System'))
    team_h_defensive_contribution_ids = fields.One2many('fpl.team.h.defensive.contribution', 'gw_fixture_id', sting=_('Home Team Defensive Contribution'))

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'GW {rec.gameweek}: {rec.team_h.name} vs {rec.team_a.name}'

    def action_open_players_statistics(self):
        action = self.env['ir.actions.actions']._for_xml_id('fantasy_premier_league.fpl_stats_wizard_action')
        action.update({
                'context': {
                    'default_team_h_goals_scored_ids': self.team_h_goals_scored_ids.ids,
                    'default_team_h_assists_ids': self.team_h_assists_ids.ids,
                    'default_team_a_goals_scored_ids': self.team_a_goals_scored_ids.ids,
                    'default_team_a_assists_ids': self.team_a_assists_ids.ids,
                    'default_team_h_yellow_cards_ids': self.team_h_yellow_cards_ids.ids,
                    'default_team_h_red_cards_ids': self.team_h_red_cards_ids.ids,
                    'default_team_a_yellow_cards_ids': self.team_a_yellow_cards_ids.ids,
                    'default_team_a_red_cards_ids': self.team_a_red_cards_ids.ids,
                    'default_team_h_saves_ids': self.team_h_saves_ids.ids,
                    'default_team_a_penalties_saved_ids': self.team_a_penalties_saved_ids.ids,
                    'default_team_a_saves_ids': self.team_a_saves_ids.ids,
                    'default_team_h_penalties_saved_ids': self.team_h_penalties_saved_ids.ids,
                    'default_team_h_bonus_ids': self.team_h_bonus_ids.ids,
                    'default_team_h_bps_ids': self.team_h_bps_ids.ids,
                    'default_team_a_bonus_ids': self.team_a_bonus_ids.ids,
                    'default_team_a_bps_ids': self.team_a_bps_ids.ids,
                },
            }
        )
        return action

    def cron_get_data_gameweek_fixutres(self):
        try:
            for gameweek in range(1, 39):
                gameweek_fixtures = self.sync_from_fpl_api('get_gameweek_fixtures', gameweek)
                
                gw_start = min(gameweek_fixtures, key=lambda item: item['kickoff_time']).get('kickoff_time')
                gw_end =  max(gameweek_fixtures, key=lambda item: item['kickoff_time']).get('kickoff_time')

                if not datetime.fromisoformat(gw_start.replace('Z', ''))  < datetime.now() < datetime.fromisoformat(gw_end.replace('Z', '')):
                    continue

                for fixture_data in gameweek_fixtures:
                    fixture_id = fixture_data.get('id')
                    exist_fixture = self.search([('gw_fixture_id', '=', fixture_id)])
                    
                    if exist_fixture and exist_fixture.finished:
                        continue
                    
                    old_data = self._get_fixture_snapshot(exist_fixture) if exist_fixture else {}
                    
                    fixture_vals = self._update_gameweek_val(fixture_data)
                    fixture_vals.update({'gameweek': gameweek})
                    
                    if exist_fixture:
                        exist_fixture.write(fixture_vals)
                    else:
                        new_fixture = self.create(fixture_vals)
                        exist_fixture = new_fixture
                    
                    if fixture_data.get('stats'):
                        old_stats = self._get_stats_snapshot(exist_fixture.id) if old_data else {}
                        self._process_fixture_stats(fixture_data.get('stats'), exist_fixture.id)
                        
                        if exist_fixture.started and not exist_fixture.finished:
                            self._check_and_notify_live_updates(exist_fixture, old_data, old_stats)
                        
        except FPLApiException as e:
            _logger.error(f"FPL API error during gameweek fixtures sync: {str(e)}")
            raise UserError(f"FPL API error during gameweek fixtures sync: {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error during sync: {str(e)}")
            raise UserError(f"Unexpected error during sync: {str(e)}")
    
    def _update_gameweek_val(self, data):
        event_id = self.env['fpl.events'].search([('event_id', '=', data.get('event'))], limit=1)
        team_h_id = self.env['fpl.teams'].search([('team_id', '=', data.get('team_h'))], limit=1)
        team_a_id = self.env['fpl.teams'].search([('team_id', '=', data.get('team_a'))], limit=1)
        
        val = {
            'code': data.get('code'),
            'event_id': event_id.id if event_id else False,
            'finished': data.get('finished'),
            'finished_provisional': data.get('finished_provisional'),
            'gw_fixture_id': data.get('id'),
            'kickoff_time': datetime.fromisoformat(data.get('kickoff_time').replace('Z', '')),
            'minutes': data.get('minutes'),
            'provisional_start_time': data.get('provisional_start_time'),
            'started': data.get('started'),
            'team_a': team_a_id.id if team_a_id else False,
            'team_a_score': data.get('team_a_score'),
            'team_a_code': team_a_id.code,
            'team_h': team_h_id.id if team_h_id else False,
            'team_h_code': team_h_id.code,
            'team_h_score': data.get('team_h_score'),
            'team_h_difficulty': data.get('team_h_difficulty'),
            'team_a_difficulty': data.get('team_a_difficulty'),
            'pulse_id': data.get('pulse_id'),
        }
        return val
    
    def _process_fixture_stats(self, stats_data, fixture_id):
        """Process stats data for a fixture"""
        stat_model_mapping = {
            'goals_scored': {
                'away': 'fpl.team.a.goals.scored',
                'home': 'fpl.team.h.goals.scored'
            },
            'assists': {
                'away': 'fpl.team.a.assists', 
                'home': 'fpl.team.h.assists'
            },
            'own_goals': {
                'away': 'fpl.team.a.own.goals',
                'home': 'fpl.team.h.own.goals'
            },
            'penalties_saved': {
                'away': 'fpl.team.a.penalties.saved',
                'home': 'fpl.team.h.penalties.saved'
            },
            'penalties_missed': {
                'away': 'fpl.team.a.penalties.missed.scored',
                'home': 'fpl.team.h.penalties.missed.scored'
            },
            'yellow_cards': {
                'away': 'fpl.team.a.yellow.cards',
                'home': 'fpl.team.h.yellow.cards'
            },
            'red_cards': {
                'away': 'fpl.team.a.red.cards',
                'home': 'fpl.team.h.red.cards'
            },
            'saves': {
                'away': 'fpl.team.a.goals.saved',
                'home': 'fpl.team.h.goals.saved'
            },
            'bonus': {
                'away': 'fpl.team.a.bonus',
                'home': 'fpl.team.h.bonus'
            },
            'bps': {
                'away': 'fpl.team.a.bps',
                'home': 'fpl.team.h.bps'
            },
            'defensive_contribution': {
                'away': 'fpl.team.a.defensive.contribution',
                'home': 'fpl.team.h.defensive.contribution'
            }
        }
        
        for stat_group in stats_data:
            identifier = stat_group.get('identifier')
            if identifier not in stat_model_mapping:
                continue
            

            for team_type in ['a', 'h']:
                team_key = 'away' if team_type == 'a' else 'home'
                model_name = stat_model_mapping[identifier][team_key]
                self.env[model_name].search([('gw_fixture_id', '=', fixture_id)]).unlink()
                
                team_stats = stat_group.get(team_type, [])
                for player_stat in team_stats:
                    element_id = player_stat.get('element')
                    value = player_stat.get('value')
                    
                    player_record = self.env['fpl.elements'].search([('element_id', '=', element_id)], limit=1)
                    
                    self.env[model_name].create({
                        'gw_fixture_id': fixture_id,
                        'element_id': player_record.id if player_record else False,
                        'value': value
                    })

    def _get_fixture_snapshot(self, fixture):
        """Get snapshot of fixture data for change detection"""
        if not fixture:
            return {}
        return {
            'team_h_score': fixture.team_h_score,
            'team_a_score': fixture.team_a_score,
            'minutes': fixture.minutes,
        }

    def _get_stats_snapshot(self, fixture_id):
        """Get snapshot of stats data for change detection"""
        stats_snapshot = {
            'red_cards': {
                'home': len(self.env['fpl.team.h.red.cards'].search([('gw_fixture_id', '=', fixture_id)])),
                'away': len(self.env['fpl.team.a.red.cards'].search([('gw_fixture_id', '=', fixture_id)])),
            },
            'own_goals': {
                'home': len(self.env['fpl.team.h.own.goals'].search([('gw_fixture_id', '=', fixture_id)])),
                'away': len(self.env['fpl.team.a.own.goals'].search([('gw_fixture_id', '=', fixture_id)])),
            },
            'penalties_saved': {
                'home': len(self.env['fpl.team.h.penalties.saved'].search([('gw_fixture_id', '=', fixture_id)])),
                'away': len(self.env['fpl.team.a.penalties.saved'].search([('gw_fixture_id', '=', fixture_id)])),
            },
            'penalties_missed': {
                'home': len(self.env['fpl.team.h.penalties.missed.scored'].search([('gw_fixture_id', '=', fixture_id)])),
                'away': len(self.env['fpl.team.a.penalties.missed.scored'].search([('gw_fixture_id', '=', fixture_id)])),
            },
        }
        return stats_snapshot

    def _check_and_notify_live_updates(self, fixture, old_data, old_stats):
        notifications = []
        
        if old_data:
            if old_data.get('team_h_score', 0) != fixture.team_h_score:
                if fixture.team_h_score > old_data.get('team_h_score', 0):
                    notifications.append(f"⚽ GOAL! {fixture.team_h.name} scored! {fixture.team_h.name} {fixture.team_h_score} - {fixture.team_a_score} {fixture.team_a.name}")
            
            if old_data.get('team_a_score', 0) != fixture.team_a_score:
                if fixture.team_a_score > old_data.get('team_a_score', 0):
                    notifications.append(f"⚽ GOAL! {fixture.team_a.name} scored! {fixture.team_h.name} {fixture.team_h_score} - {fixture.team_a_score} {fixture.team_a.name}")
        
        if old_stats:
            current_stats = self._get_stats_snapshot(fixture.id)
            
            if current_stats['red_cards']['home'] > old_stats.get('red_cards', {}).get('home', 0):
                notifications.append(f"🟥 RED CARD! {fixture.team_h.name} player sent off!")
            if current_stats['red_cards']['away'] > old_stats.get('red_cards', {}).get('away', 0):
                notifications.append(f"🟥 RED CARD! {fixture.team_a.name} player sent off!")
            
            if current_stats['own_goals']['home'] > old_stats.get('own_goals', {}).get('home', 0):
                notifications.append(f"⚽ OWN GOAL! {fixture.team_h.name} scored an own goal!")
            if current_stats['own_goals']['away'] > old_stats.get('own_goals', {}).get('away', 0):
                notifications.append(f"⚽ OWN GOAL! {fixture.team_a.name} scored an own goal!")
            
            if current_stats['penalties_saved']['home'] > old_stats.get('penalties_saved', {}).get('home', 0):
                notifications.append(f"🥅 PENALTY SAVED! {fixture.team_h.name} goalkeeper made a penalty save!")
            if current_stats['penalties_saved']['away'] > old_stats.get('penalties_saved', {}).get('away', 0):
                notifications.append(f"🥅 PENALTY SAVED! {fixture.team_a.name} goalkeeper made a penalty save!")
            
            if current_stats['penalties_missed']['home'] > old_stats.get('penalties_missed', {}).get('home', 0):
                notifications.append(f"❌ PENALTY MISSED! {fixture.team_h.name} player missed a penalty!")
            if current_stats['penalties_missed']['away'] > old_stats.get('penalties_missed', {}).get('away', 0):
                notifications.append(f"❌ PENALTY MISSED! {fixture.team_a.name} player missed a penalty!")
        
        if notifications:
            self._send_live_notifications(fixture, notifications)

    def _send_live_notifications(self, fixture, notifications):
        """Send live match notifications to all users using message_post"""
        try:
            users = self.env['res.users'].search([])
            
            match_info = f"GW{fixture.gameweek}: {fixture.team_h.name} vs {fixture.team_a.name} ({fixture.minutes}')"
            
            for notification in notifications:
                message_body = f"<p><strong>🔴 LIVE MATCH UPDATE</strong></p>"
                message_body += f"<p><strong>{match_info}</strong></p>"
                message_body += f"<p>{notification}</p>"
                
                for user in users:
                    if user.partner_id:
                        user.partner_id.message_post(
                            body=message_body,
                            subject=f"FPL Live Update: {fixture.team_h.name} vs {fixture.team_a.name}",
                            message_type='notification',
                            subtype_xmlid='mail.mt_comment'
                        )
                
                _logger.info(f"Live notification sent: {notification}")
                
        except Exception as e:
            _logger.error(f"Error sending live notifications: {str(e)}")