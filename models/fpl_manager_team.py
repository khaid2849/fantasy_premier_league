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
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = 'FPL Manager Team'
    
    manager_id = fields.Char(string=_('Manager ID'))
    cookies = fields.Char(string=_('Cookies'))
    x_api_authorization = fields.Char(string=_('X-api-authorization'))
    #Manager Data
    manager_data_id = fields.Integer(string=_('Manager Data ID'))
    date_of_birth = fields.Date(string=_('Date of Birth'), tracking=True)
    default_event = fields.Integer(string=_('Default Event'), tracking=True)
    dirty = fields.Boolean(string=_('Dirty'), tracking=True)
    first_name = fields.Char(string=_('First Name'), tracking=True)
    last_name = fields.Char(string=_('Last Name'), tracking=True)
    full_name = fields.Char(string=_('Full Name'), tracking=True)
    email = fields.Char(string=_('Email'), tracking=True)
    gender = fields.Selection([('M', _('Male')), ('F', _('Female') )], string=_('Gender'), tracking=True)
    manger_data_id = fields.Integer(string=_('ID'))
    region = fields.Char(string=_('Region'), tracking=True)
    country_id = fields.Many2one('res.country', string=_('Country'), tracking=True)
    entry_email = fields.Char(string=_('Entry Email'), tracking=True)
    entry_language = fields.Char(string=_('Entry Language'), tracking=True)
    sso_id = fields.Char(string=_('SSO ID'), tracking=True)
    #Manager Entry Summary
    joined_time = fields.Datetime(string=_('Joined Time'), tracking=True)
    started_event = fields.Integer(string=_('Started Event'), tracking=True)
    favourite_team = fields.Many2one('fpl.teams', string=_('Favourite Team'), tracking=True)
    player_first_name = fields.Char(string=_('Player First Name'), tracking=True)
    player_last_name = fields.Char(string=_('Player Last Name'), tracking=True)
    player_region_id = fields.Char(string=_('Player Region ID'), tracking=True)
    player_region_name = fields.Char(string=_('Player Region Name'), tracking=True)
    player_region_iso_code_short = fields.Char(string=_('Player Region ISO Code Short'), tracking=True)
    player_region_iso_code_long = fields.Char(string=_('Player Region ISO Code Long'), tracking=True)
    years_active = fields.Integer(string=_('Years Active'), tracking=True)
    summary_overall_points = fields.Integer(string=_('Summary Overall Points'), tracking=True)
    summary_overall_rank = fields.Integer(string=_('Summary Overall Rank'), tracking=True)
    summary_event_points = fields.Integer(string=_('Current Gameweek points'), tracking=True)
    summary_event_rank = fields.Integer(string=_('Current Gameweek Rank'), tracking=True)
    current_event = fields.Integer(string=_('Current Gameweek'), tracking=True)
    name = fields.Char(string=_('Name'), tracking=True)
    name_change_blocked = fields.Boolean(string=_('Name Change Blocked'), tracking=True)
    kits = fields.Char(string=_('Kits'), tracking=True)
    last_deadline_bank = fields.Integer(string=_('Last Deadline Bank'), tracking=True)
    last_deadline_value = fields.Integer(string=_('Last Deadline Value'), tracking=True)
    last_deadline_total_transfers = fields.Integer(string=_('Last Deadline Total Transfers'), tracking=True)
    club_badge_src = fields.Char(string=_('Club Badge Src'), tracking=True)
    league_classic_ids = fields.One2many('fpl.leagues', 'manager_id', string=_('League Classic IDs'), domain=[('type', '=', 'classic')])
    league_h2h_ids = fields.One2many('fpl.leagues', 'manager_id', string=_('League H2H IDs'), domain=[('type', '=', 'h2h')])
    pick_ids = fields.One2many('fpl.picks', 'manager_id', string=_('Element IDs'))
    manager_chip_ids = fields.One2many('fpl.manager.chips', 'manager_id', string=_('Manager Chips'))
    picks_last_updated = fields.Datetime(string=_('Picks Last Updated'), tracking=True)

    #Transfer Info
    cost = fields.Integer(string=_('Cost'), tracking=True)
    status = fields.Char(string=_('Status'), tracking=True)
    limit = fields.Integer(string=_('Transfers Limit'), tracking=True)
    made = fields.Float(string=_('Transfers Made'), tracking=True)
    bank = fields.Float(string=_('In the Bank'), tracking=True)
    value = fields.Float(string=_('Squad Value'), tracking=True)
    status_for_entry = fields.Selection([('available', _('Available')), ('used', _('Used'))], string=_('Status for Entry'))
    
    used_bench_boost = fields.Boolean(compute='_computed_used_chips')
    used_wildcard = fields.Boolean(compute='_computed_used_chips')
    used_free_hit = fields.Boolean(compute='_computed_used_chips')
    used_triple_captain = fields.Boolean(compute='_computed_used_chips')

    #Entry History
    entry_history_ids = fields.One2many('fpl.entry.history', 'manager_id', string=_('Entry History'))
    entry_past_ids = fields.One2many('fpl.past', 'manager_id', string=_('Entry Past'))

    @api.depends('manager_chip_ids')
    def _computed_used_chips(self):
        for rec in self:
            if rec.manager_chip_ids:
                rec.used_bench_boost = False if any(chip.is_bench_boost and chip.status_for_entry == 'available' for chip in rec.manager_chip_ids) else True
                rec.used_wildcard = False if any(chip.is_wildcard and chip.status_for_entry == 'available' for chip in rec.manager_chip_ids) else True
                rec.used_free_hit = False if any(chip.is_free_hit and chip.status_for_entry == 'available' for chip in rec.manager_chip_ids) else True
                rec.used_triple_captain = False if any(chip.is_triple_captain and chip.status_for_entry == 'available' for chip in rec.manager_chip_ids) else True


    def action_open_entry_history(self):
        action = self.env['ir.actions.actions']._for_xml_id('fantasy_premier_league.fpl_manager_team_history_wizard_action')
        action.update({
                'context': {
                    'default_entry_history_ids': self.entry_history_ids.ids,
                    'default_entry_past_ids': self.entry_past_ids.ids,
                },
            }
        )
        return action

    def action_verify_manager_data(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('fantasy_premier_league.fpl_manager_team_wizard_action')
        action.update({
                'context': {
                    'default_manager_id':  self.manager_id, 
                    'default_cookies':  self.cookies, 
                    'default_x_api_authorization':  self.x_api_authorization,
                    'is_readonly': True,    
                },
        })
        return action
    
    @api.model
    def sync_manager_data(self, cookies, x_api_authorization, manager_id=None):
        """Sync manager data from FPL API using authentication and create/update record"""
        try:
            manager_data = self.with_context().sync_authenticated_data(
                'get_manager_data', 
                cookies, 
                x_api_authorization
            )
            
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
                manager_team = self.create({
                    'manager_id': api_manager_id,
                    'cookies': cookies,
                    'x_api_authorization': x_api_authorization,
                    }
                )
                _logger.info(f"Created new manager team record for ID: {api_manager_id}")
            else:
                manager_team.write({
                    'cookies': cookies,
                    'x_api_authorization': x_api_authorization,
                })
                _logger.info(f"Found existing manager team record for ID: {api_manager_id}")
            
            entry_summary = manager_team.sync_from_fpl_api(
                'get_entry_summary', 
                api_manager_id,
            )

            manager_team_data = manager_team.sync_authenticated_data(
                'get_manager_team',
                cookies, 
                x_api_authorization,
                api_manager_id
            )
            
            entry_history_data = manager_team.sync_from_fpl_api(
                'get_entry_history',
                api_manager_id,
            )
            manager_team._update_from_manager_data(manager_data.get('player', {}))
            manager_team._update_from_entry_summary(entry_summary, manager_team.id)
            manager_team._update_from_manager_team(manager_team_data, manager_team.id)
            manager_team._update_from_entry_histroy(entry_history_data, manager_id)
            
            leauge_ids = self.env['fpl.leagues'].search([('manager_id', '=', manager_team.id)])
            if leauge_ids:
                league_phase_mapping = {leauge: leauge.active_phases_ids for leauge in leauge_ids if leauge.active_phases_ids}
                if league_phase_mapping:
                    self._update_league_standings(league_phase_mapping)

            _logger.info(f"Successfully synced data for manager {api_manager_id}")
            return manager_team
                
        except FPLApiException as e:
            _logger.error(f"Failed to sync manager data: {str(e)}")
            raise UserError(f"Failed to sync manager data: {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error during sync: {str(e)}")
            raise UserError(f"Unexpected error during sync: {str(e)}")

    def _update_from_entry_histroy(self, data, manager_id):
        existing_history = {h.event_id.event_id: h for h in self.env['fpl.entry.history'].search([('manager_id', '=', manager_id)])}
        existing_past = {p.season_name: p for p in self.env['fpl.past'].search([('manager_id', '=', manager_id)])}
        
        event_ids = [history.get('event') for history in data.get('current', [])]
        events_dict = {e.event_id: e for e in self.env['fpl.events'].search([('event_id', 'in', event_ids)])}
        
        history_to_create = []
        history_to_update = []
        current_history_events = set()
        
        for history in data.get('current', []):
            event_id = history.get('event')
            current_history_events.add(event_id)
            event_record = events_dict.get(event_id)
            
            if not event_record:
                continue
                
            val = {
                'event_id': event_record.id,
                'points': history.get('points'),
                'total_points': history.get('total_points'),
                'rank': history.get('rank'),
                'rank_sort': history.get('rank_sort'),
                'overall_rank': history.get('overall_rank'),
                'bank': history.get('bank'),
                'value': history.get('value'),
                'event_transfers': history.get('event_transfers'),
                'event_transfer_cost': history.get('event_transfer_cost'),
                'points_on_bench': history.get('points_on_bench'),
                'manager_id': manager_id,
            }
            
            existing_record = existing_history.get(event_id)
            if existing_record:
                needs_update = False
                for key, new_val in val.items():
                    if key != 'manager_id' and hasattr(existing_record, key) and getattr(existing_record, key) != new_val:
                        needs_update = True
                        break
                if needs_update:
                    history_to_update.append((existing_record, val))
            else:
                history_to_create.append(val)

        past_to_create = []
        past_to_update = []
        current_past_seasons = set()
        
        for past in data.get('past', []):
            season_name = past.get('season_name')
            current_past_seasons.add(season_name)
            
            val = {
                'season_name': season_name,
                'total_poinst': past.get('total_points'),
                'rank': past.get('rank'),
                'manager_id': manager_id,
            }
            
            existing_record = existing_past.get(season_name)
            if existing_record:
                needs_update = False
                for key, new_val in val.items():
                    if key != 'manager_id' and hasattr(existing_record, key) and getattr(existing_record, key) != new_val:
                        needs_update = True
                        break
                if needs_update:
                    past_to_update.append((existing_record, val))
            else:
                past_to_create.append(val)
        
        obsolete_history = [rec for event_id, rec in existing_history.items() if event_id not in current_history_events]
        obsolete_past = [rec for season, rec in existing_past.items() if season not in current_past_seasons]
        
        if obsolete_history:
            for rec in obsolete_history:
                rec.unlink()
        if obsolete_past:
            for rec in obsolete_past:
                rec.unlink()
        
        created_history = self.env['fpl.entry.history'].create(history_to_create) if history_to_create else self.env['fpl.entry.history']
        created_past = self.env['fpl.past'].create(past_to_create) if past_to_create else self.env['fpl.past']
        
        for record, vals in history_to_update:
            record.write(vals)
        for record, vals in past_to_update:
            record.write(vals)
        
        if history_to_create or past_to_create:
            all_history = list(existing_history.values()) + list(created_history)
            all_past = list(existing_past.values()) + list(created_past)
            
            self.write({
                'entry_history_ids': [(6, 0, [h.id for h in all_history])],
                'entry_past_ids': [(6, 0, [p.id for p in all_past])]
            })

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
        if not picks:
            existing_picks = self.env['fpl.picks'].search([('manager_id', '=', manager_id)])
            if existing_picks:
                existing_picks.unlink()
            return []
        
        existing_picks = {(p.element_id.element_id, p.position): p for p in self.env['fpl.picks'].search([('manager_id', '=', manager_id)])}
        
        element_ids = [pick.get('element') for pick in picks]
        element_type_ids = [pick.get('element_type') for pick in picks]
        
        elements_dict = {e.element_id: e for e in self.env['fpl.elements'].search([('element_id', 'in', element_ids)])}
        element_types_dict = {et.element_type_id: et for et in self.env['fpl.element.types'].search([('element_type_id', 'in', [str(et_id) for et_id in element_type_ids])])}
        
        picks_to_create = []
        picks_to_update = []
        current_picks = set()
        
        for pick in picks:
            element_id = pick.get('element')
            position = pick.get('position')
            current_picks.add((element_id, position))
            
            element = elements_dict.get(element_id)
            element_type = element_types_dict.get(str(pick.get('element_type')))
            
            if not element or not element_type:
                continue
                
            pick_vals = {
                'element_id': element.id,
                'position': position,
                'multiplier': pick.get('multiplier'),
                'is_captain': pick.get('is_captain'),
                'is_vice_captain': pick.get('is_vice_captain'),
                'element_type_id': element_type.id,
                'selling_price': pick.get('selling_price') / 10,
                'purchase_price': pick.get('purchase_price') / 10,
                'manager_id': manager_id,
            }
            
            existing_pick = existing_picks.get((element_id, position))
            if existing_pick:
                needs_update = False
                for key, new_val in pick_vals.items():
                    if key != 'manager_id' and hasattr(existing_pick, key) and getattr(existing_pick, key) != new_val:
                        needs_update = True
                        break
                if needs_update:
                    picks_to_update.append((existing_pick, pick_vals))
            else:
                picks_to_create.append(pick_vals)
        
        obsolete_picks = [pick for key, pick in existing_picks.items() if key not in current_picks]
        if obsolete_picks:
            for pick in obsolete_picks:
                pick.unlink()
        
        for pick, vals in picks_to_update:
            pick.write(vals)
        
        if picks_to_create:
            created_picks = self.env['fpl.picks'].create(picks_to_create)
            return [(0, 0, {'id': pick.id}) for pick in created_picks]
        else:
            return []

    def _update_manager_chips_data(self, chips, manager_id):
        if not chips:
            existing_chips = self.env['fpl.manager.chips'].search([('manager_id', '=', manager_id)])
            if existing_chips:
                existing_chips.unlink()
            return []
        
        existing_chips = {c.chip_id.chip_id: c for c in self.env['fpl.manager.chips'].search([('manager_id', '=', manager_id)])}
        
        chip_ids = [str(chip.get('id')) for chip in chips]
        chips_dict = {c.chip_id: c for c in self.env['fpl.chips'].search([('chip_id', 'in', chip_ids)])}
        
        chips_to_create = []
        chips_to_update = []
        current_chips = set()
        
        for chip in chips:
            chip_api_id = str(chip.get('id'))
            current_chips.add(chip_api_id)
            
            chip_record = chips_dict.get(chip_api_id)
            if not chip_record:
                continue
                
            chip_vals = {
                'chip_id': chip_record.id,
                'status_for_entry': chip.get('status_for_entry'),
                'played_by_entry': chip.get('played_by_entry'),
                'is_pending': chip.get('is_pending'),
                'manager_id': manager_id,
            }
            
            existing_chip = existing_chips.get(chip_api_id)
            if existing_chip:
                needs_update = False
                for key, new_val in chip_vals.items():
                    if key != 'manager_id' and hasattr(existing_chip, key) and getattr(existing_chip, key) != new_val:
                        needs_update = True
                        break
                if needs_update:
                    chips_to_update.append((existing_chip, chip_vals))
            else:
                chips_to_create.append(chip_vals)
        
        obsolete_chips = [chip for chip_id, chip in existing_chips.items() if chip_id not in current_chips]
        if obsolete_chips:
            for chip in obsolete_chips:
                chip.unlink()
        
        for chip, vals in chips_to_update:
            chip.write(vals)
        
        if chips_to_create:
            created_chips = self.env['fpl.manager.chips'].create(chips_to_create)
            return [(0, 0, {'id': chip.id}) for chip in created_chips]
        else:
            return []
    
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
        if not datas:
            existing_leagues = self.env['fpl.leagues'].search([('manager_id', '=', manager_id), ('type', '=', type)])
            if existing_leagues:
                existing_leagues.active_phases_ids.unlink()
                existing_leagues.unlink()
            return []
        
        existing_leagues = {l.league_id: l for l in self.env['fpl.leagues'].search([('manager_id', '=', manager_id), ('type', '=', type)])}
        
        leagues_to_create = []
        leagues_to_update = []
        current_leagues = set()
        
        for league in datas:
            league_api_id = league.get('id')
            current_leagues.add(league_api_id)
            
            val = {
                'type': type,
                'league_id': league_api_id,
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
                'manager_id': manager_id,
            }
            
            existing_league = existing_leagues.get(league_api_id)
            if existing_league:
                needs_update = False
                for key, new_val in val.items():
                    if key != 'manager_id' and hasattr(existing_league, key) and getattr(existing_league, key) != new_val:
                        needs_update = True
                        break
                
                if needs_update:
                    leagues_to_update.append((existing_league, val, league.get('active_phases')))
                else:
                    leagues_to_update.append((existing_league, {}, league.get('active_phases')))
            else:
                val['active_phases_ids'] = self._get_league_phases_val(league.get('active_phases'))
                leagues_to_create.append(val)
        
        obsolete_leagues = [league for league_id, league in existing_leagues.items() if league_id not in current_leagues]
        if obsolete_leagues:
            for league in obsolete_leagues:
                league.active_phases_ids.unlink()
                league.unlink()
        
        updated_league_ids = []
        for league, vals, active_phases in leagues_to_update:
            if vals:
                league.write(vals)
            
            if active_phases is not None:
                league.active_phases_ids.unlink()
                new_phases = self._get_league_phases_val(active_phases)
                if new_phases:
                    phase_records = self.env['fpl.league.active.phases'].create([vals for _, _, vals in new_phases])
                    league.write({'active_phases_ids': [(6, 0, phase_records.ids)]})
            
            updated_league_ids.append(league.id)
        
        if leagues_to_create:
            created_leagues = self.env['fpl.leagues'].create(leagues_to_create)
            return updated_league_ids + created_leagues.ids
        else:
            return updated_league_ids
                
    def _update_league_standings(self, league_phases):
        try:
            for leauge, active_phases in league_phases.items():
                for phase in active_phases:
                    existing_standings = {s.result_id: s for s in self.env['fpl.league.standings.results'].search([('league_id', '=', leauge.id), ('phase_id', '=', phase.id)])}
                    
                    leauge_standing_datas = self.sync_from_fpl_api('get_league_standings', league_id=leauge.league_id, phase=phase.phase_id.phase_id)
                    standings = leauge_standing_datas.get('standings', {})
                    results = standings.get('results', [])
                    
                    standings_to_create = []
                    standings_to_update = []
                    current_result_ids = set()
                    
                    for rs in results:
                        result_id = rs.get('id')
                        current_result_ids.add(result_id)
                        
                        standing_vals = rs.copy()
                        standing_vals.update({
                            'result_id': result_id,
                            'league_id': leauge.id,
                            'phase_id': phase.phase_id.id,
                        })
                        standing_vals.pop('id')
                        
                        existing_standing = existing_standings.get(result_id)
                        if existing_standing:
                            needs_update = False
                            for key, new_val in standing_vals.items():
                                if hasattr(existing_standing, key) and getattr(existing_standing, key) != new_val:
                                    needs_update = True
                                    break
                            if needs_update:
                                standings_to_update.append((existing_standing, standing_vals))
                        else:
                            standings_to_create.append(standing_vals)
                    
                    obsolete_standings = [s for result_id, s in existing_standings.items() if result_id not in current_result_ids]
                    if obsolete_standings:
                        for s in obsolete_standings:
                            s.unlink()
                    
                    for standing, vals in standings_to_update:
                        standing.write(vals)
                    
                    if standings_to_create:
                        self.env['fpl.league.standings.results'].create(standings_to_create)
                    
                    if leauge_standing_datas.get('last_updated_data'):
                        leauge.write({'last_updated_data': datetime.fromisoformat(leauge_standing_datas.get('last_updated_data').replace('Z', ''))})

       
        except FPLApiException as e:
                _logger.error(f"Failed to sync league standings data: {str(e)}")
                raise UserError(f"Failed to sync league standings data: {str(e)}")
        except Exception as e:
                _logger.error(f"Unexpected error during sync: {str(e)}")
                raise UserError(f"Unexpected error during sync: {str(e)}")



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