from odoo import models, fields, api

class FplGameweekPickLinesWizard(models.TransientModel):
    _name = 'fpl.gameweek.pick.lines.wizard'
    _description = 'FPL Gameweek Pick Lines Wizard'

    element_id = fields.Many2one('fpl.elements', string='Player')
    element_stats_ids = fields.Many2many('fpl.element.stats')
    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Gameweek Fixutre')
    team_h_photo = fields.Image()
    team_h_score = fields.Integer()
    team_a_photo = fields.Image()
    team_a = fields.Many2one('fpl.teams', string='Away team')
    team_h = fields.Many2one('fpl.teams', string='Home team')
    team_a_score = fields.Integer()
    kickoff_time = fields.Datetime()
    started = fields.Boolean()
    finished = fields.Boolean()