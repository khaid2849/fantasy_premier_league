from odoo import models, fields, api, _

class FplGameweekPickLinesWizard(models.TransientModel):
    _name = 'fpl.gameweek.pick.lines.wizard'

    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    element_stats_ids = fields.Many2many('fpl.element.stats')
    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Gameweek Fixutre'))
    team_h_photo = fields.Image()
    team_h_score = fields.Integer()
    team_a_photo = fields.Image()
    team_a = fields.Many2one('fpl.teams', string=_('Away team'))
    team_h = fields.Many2one('fpl.teams', string=_('Home team'))
    team_a_score = fields.Integer()
    kickoff_time = fields.Datetime()
    started = fields.Boolean()
    finished = fields.Boolean()