from odoo import fields, models


class FplPast(models.Model):
    _name = 'fpl.past'
    _description = 'FPL Past'
    _order = 'season_name desc'

    season_name = fields.Char(string='Season name')
    total_poinst = fields.Integer(string='Total points')
    rank = fields.Integer(string='Rank')
    manager_id = fields.Many2one('fpl.manager.team', string='Manager Team', required=True, index=True,
                                 ondelete='cascade')
