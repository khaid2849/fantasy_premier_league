from odoo import fields, models


class FplEntryHistory(models.Model):
    _name = 'fpl.entry.history'
    _description = 'FPL Entry History'
    _order = 'event_id'

    manager_id = fields.Many2one('fpl.manager.team', string='Manager Team', required=True, index=True,
                                 ondelete='cascade')
    event_id = fields.Many2one('fpl.events', string='Gameweek', index=True)
    points = fields.Integer(string='Points')
    total_points = fields.Integer(string='Total Points')
    rank = fields.Integer(string='Rank')
    rank_sort = fields.Integer(string='Rank Sort')
    overall_rank = fields.Integer(string='Overall rank')
    bank = fields.Float(string='Bank')
    value = fields.Float(string='Value')
    event_transfers = fields.Integer(string='Current Gameweek transfers')
    event_transfer_cost = fields.Integer(string='Current Gameweek transfer cost')
    points_on_bench = fields.Integer(string='Points on bench')
