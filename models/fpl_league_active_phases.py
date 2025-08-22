from odoo import models, fields, api, _

class FPLLeagueActivePhases(models.Model):
    _name = 'fpl.league.active.phases'
    _description = 'FPL League Active Phases'

    phase_id = fields.Many2one('fpl.phases', string=_('Phase'))
    rank = fields.Integer(string=_('Rank'))
    last_rank = fields.Integer(string=_('Last Rank'))
    rank_sort = fields.Integer(string=_('Rank Sort'))
    total = fields.Integer(string=_('Total'))
    league_id = fields.Many2one('fpl.leagues', string=_('League ID'))
    rank_count = fields.Integer(string=_('Rank Count'))
    entry_percentile_rank = fields.Integer(string=_('Entry Percentile Rank'))