from odoo import models, fields, api, _

class FplPast(models.Model):
    _name = 'fpl.past'

    season_name = fields.Char(string=_('Season name'))
    total_poinst = fields.Integer(string=_('Total points'))
    rank = fields.Integer(string=_('Rank'))
    manager_id = fields.Many2one('fpl.manager.team', string=_('Manager Team'))