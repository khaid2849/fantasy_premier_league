from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .fpl_api_mixin import FPLApiMixin
from ..services.fpl_api_client import FPLApiException
import logging

_logger = logging.getLogger(__name__)

class FplGameweekPickLines(models.Model, FPLApiMixin):
    _name = 'fpl.gameweek.pick.lines'
    _description = 'FPL Gameweek Pick Lines'

    gameweek_pick_id = fields.Many2one('fpl.gameweek.picks', string=_('Gameweek Pick'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    position = fields.Integer(string=_('Points'))
    multiplier = fields.Integer(string=_('Multiplier'))
    is_captain = fields.Boolean(string=_('Is Captain'))
    is_vice_captain = fields.Boolean(string=_('Is Vice Captain'))
    element_type_id = fields.Many2one('fpl.element.types', string=_('Element Type'))
    team_id = fields.Many2one('fpl.teams', string=_('Team'))
    team_code = fields.Char()
    team_name = fields.Char()
    total_points = fields.Integer(string=_('Total points'))
    web_name = fields.Char()
    plural_name_short= fields.Char(related='element_type_id.plural_name_short')
    element_stats_ids = fields.One2many('fpl.element.stats', 'pick_line_id', string=_('Stats'))
    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Gameweek Fixutre'))


    @api.model
    def sync_gameweek_picks(self, manager_team, gw):
        try:
            if not gw.get('finished') and not gw.get('is_current') and not gw.get('is_previous') and not gw.get('is_next'):
                return
            exist_pick = self.env['fpl.gameweek.picks'].search([('manager_id', '=', manager_team.get('id')), ('event_id', '=', gw.get('id'))])

            gw_picks = self.sync_from_fpl_api('get_gameweek_picks', team_id=manager_team.get('manager_id'), gw_id=gw.get('event_id'))
            element_datas = self.sync_from_fpl_api('get_element_gameweek_live', gw_id=gw.get('event_id'))

            entry_history = gw_picks.get('entry_history')
            gw_pick_lines = gw_picks.get('picks')
            gw_pick_val = {
                'event_id': gw.get('id'),
                'manager_id': manager_team.get('id'),
                'points': entry_history.get('points'),
                'total_points': entry_history.get('total_points'),
                'rank': entry_history.get('rank'),
                'rank_sort': entry_history.get('rank_sort'),
                'overall_rank': entry_history.get('overall_rank'),
                'percentile_rank': entry_history.get('percentile_rank'),
                'bank': entry_history.get('bank') / 10,
                'value': entry_history.get('value') / 10,
                'event_transfers': entry_history.get('event_transfers'),
                'event_transfers_cost': entry_history.get('event_transfers_cost') / 10,
                'points_on_bench': entry_history.get('points_on_bench'),
            }

            if exist_pick:
                exist_pick.update(gw_pick_val)
            else:
                create_gw_pick = self.env['fpl.gameweek.picks'].create(gw_pick_val)
                exist_pick = create_gw_pick

            self._get_gw_picks_lines(gw_pick_lines, exist_pick, element_datas.get('elements'))

        except FPLApiException as e:
            _logger.error(f"Failed to sync gameweek picks data: {str(e)}")
            
            raise UserError(f"Failed to sync gameweek picks data: {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error during sync: {str(e)}")
            raise UserError(f"Unexpected error during sync: {str(e)}")
    
    def _get_gw_picks_lines(self, picks, gw_pick, element_datas):
        for pick in picks:
            element_id = self.env['fpl.elements'].search([('element_id', '=', pick.get('element'))])
            val = {
                'gameweek_pick_id': gw_pick.id,
                'element_id': element_id.id,
                'element_type_id': self.env['fpl.element.types'].search([('element_type_id', '=', pick.get('element_type'))]).id,
                'team_id': element_id.fpl_team_id.id,
                'team_code': element_id.fpl_team_id.code,
                'team_name': element_id.fpl_team_id.name,
                'web_name': element_id.web_name,
                'position': pick.get('position'),
                'multiplier': pick.get('multiplier'),
                'is_captain': pick.get('is_captain'),
                'is_vice_captain': pick.get('is_vice_captain'),
                'gameweek_pick_id': gw_pick.id,
            }
            pick_line = self.env['fpl.gameweek.pick.lines'].search([('gameweek_pick_id', '=', gw_pick.id), ('element_id', '=', element_id.id)], limit=1)
            if pick_line:
                pick_line.update(val)
            else:
                pick_line = self.env['fpl.gameweek.pick.lines'].create(val)

            self._get_element_stat_lines(pick_line, element_datas)

    def _get_element_stat_lines(self, pick_line, element_datas):
        try:
            self.env['fpl.element.stats'].search([('pick_line_id', '=', pick_line.id), ('pick_line_id.element_id', '=', pick_line.element_id.id)]).unlink()
            for el in element_datas:
                if el.get('id') == pick_line.element_id.element_id:
                    stat_vals = el.get('explain')[0].get('stats')
                    fixture = self.env['fpl.gameweek.fixtures'].search([('gw_fixture_id', '=', el.get('explain')[0].get('fixture'))])
                    
                    for st in stat_vals:
                        st.update({'pick_line_id': pick_line.id,})

                    self.env['fpl.element.stats'].create(stat_vals)
                    pick_line.update({'gw_fixture_id': fixture.id, 'total_points': el.get('stats').get('total_points')})
                    
        except FPLApiException as e:
            _logger.error(f"Failed to sync gameweek element stats data: {str(e)}")
            raise UserError(f"Failed to sync gameweek element stats data: {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error during sync: {str(e)}")
            raise UserError(f"Unexpected error during sync: {str(e)}")

    @api.model
    def get_pick_formations(self, picks):
        lineup_gkp = []
        lineup_def = []
        lineup_mid = []
        lineup_fwd = []

        sub_elements = []

        lineups_element_mapping = {
            'GKP': lineup_gkp,
            'DEF': lineup_def,
            'MID': lineup_mid,
            'FWD': lineup_fwd,
        }

        for pick in picks:
            if hasattr(pick, 'position'):
                # This is a recordset object
                position = pick.position
                pick_id = pick.id
                plural_name_short = pick.element_type_id.plural_name_short
            else:
                # This is dictionary data from JavaScript
                position = pick['position']
                pick_id = pick['id']
                plural_name_short = pick['element_type_id']['plural_name_short']
            
            if position in [12, 13, 14, 15]:
                sub_elements.append(pick_id)
            
            for pos, elements in lineups_element_mapping.items():
                if position == 1 and plural_name_short == pos:
                    elements.append(pick_id)
                
                elif position in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11] and plural_name_short == pos:
                    elements.append(pick_id)

        return {
            'lineup_gkp': lineup_gkp,
            'lineup_def': lineup_def,
            'lineup_mid': lineup_mid,
            'lineup_fwd': lineup_fwd,
            'sub_elements': sub_elements,
        }
    
    @api.model
    def action_open_player_stats(self, pick_line_id):
        element_stats_ids = self.env['fpl.element.stats'].search([('pick_line_id', '=', pick_line_id)])
        pick_line = self.browse(pick_line_id)
        action = self.env['ir.actions.actions']._for_xml_id('fantasy_premier_league.fpl_gameweek_pick_lines_wizard_action')
        action.update({
                'context': {
                    'default_element_stats_ids': element_stats_ids.ids,
                    'default_gw_fixture_id': pick_line.gw_fixture_id.id,
                    'default_element_id': pick_line.element_id.id,
                    'default_team_h_photo': pick_line.gw_fixture_id.team_h_photo,
                    'default_team_h': pick_line.gw_fixture_id.team_h.id,
                    'default_team_h_score': pick_line.gw_fixture_id.team_h_score,
                    'default_team_a_photo': pick_line.gw_fixture_id.team_a_photo,
                    'default_team_a': pick_line.gw_fixture_id.team_a.id,
                    'default_team_a_score': pick_line.gw_fixture_id.team_a_score,
                    'default_kickoff_time': pick_line.gw_fixture_id.kickoff_time,
                    'default_started': pick_line.gw_fixture_id.started,
                    'default_finished': pick_line.gw_fixture_id.finished,
                },
            }
        )
        return action
