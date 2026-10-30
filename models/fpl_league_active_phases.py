from odoo import models, fields, api

class FPLLeagueActivePhases(models.Model):
    _name = 'fpl.league.active.phases'
    _description = 'FPL League Active Phases'

    phase_id = fields.Many2one('fpl.phases', string='Phase')
    rank = fields.Integer(string='Rank')
    last_rank = fields.Integer(string='Last Rank')
    rank_sort = fields.Integer(string='Rank Sort')
    total = fields.Integer(string='Total')
    league_id = fields.Many2one('fpl.leagues', string='League ID')
    rank_count = fields.Integer(string='Rank Count')
    entry_percentile_rank = fields.Integer(string='Entry Percentile Rank')