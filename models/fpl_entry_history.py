from odoo import models, fields, api

class FplEntryHistory(models.Model):
    _name = 'fpl.entry.history'
    _description = 'FPL Entry History'

    manager_id = fields.Many2one('fpl.manager.team', string='Manager Team')
    event_id = fields.Many2one('fpl.events', string='Gameweek')
    points = fields.Integer(string='Points')
    total_points = fields.Integer(string='Total Points')
    rank = fields.Integer(string='Rank')
    rank_sort = fields.Integer(string='Rank Sort')
    overall_rank = fields.Integer(string='Overall rank')
    bank = fields.Float(string='Bank')
    value = fields.Integer(string='Value')
    event_transfers = fields.Integer(string='Current Gameweek transfers')
    event_transfer_cost = fields.Integer(string='Current Gameweek transfer cost')
    points_on_bench = fields.Integer(string='Points on bench')