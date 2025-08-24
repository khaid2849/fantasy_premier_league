from odoo import models, fields, api, _

class FplEntryHistory(models.Model):
    _name = 'fpl.entry.history'

    manager_id = fields.Many2one('fpl.manager.team', string=_('Manager Team'))
    event_id = fields.Many2one('fpl.events', string=_('Gameweek'))
    points = fields.Integer(string=_('Points'))
    total_points = fields.Integer(string=_('Total Points'))
    rank = fields.Integer(string=_('Rank'))
    rank_sort = fields.Integer(string=_('Rank Sort'))
    overall_rank = fields.Integer(string=_('Overall rank'))
    bank = fields.Float(string=_('Bank'))
    value = fields.Integer(string=_('Value'))
    event_transfers = fields.Integer(string=_('Current Gameweek transfers'))
    event_transfer_cost = fields.Integer(string=_('Current Gameweek transfer cost'))
    points_on_bench = fields.Integer(string=_('Points on bench'))