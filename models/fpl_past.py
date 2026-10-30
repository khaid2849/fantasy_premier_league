from odoo import models, fields, api

class FplPast(models.Model):
    _name = 'fpl.past'
    _description = 'FPL Past'

    season_name = fields.Char(string='Season name')
    total_poinst = fields.Integer(string='Total points')
    rank = fields.Integer(string='Rank')
    manager_id = fields.Many2one('fpl.manager.team', string='Manager Team')