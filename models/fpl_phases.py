from odoo import fields, models

OVERALL_PHASE_ID = 1


class FPLPhases(models.Model):
    _name = 'fpl.phases'
    _description = 'FPL Phases'
    _order = 'phase_id'

    phase_id = fields.Integer(string='ID', index=True)
    name = fields.Char(string='Name')
    start_event = fields.Integer(string='Start Event')
    stop_event = fields.Integer(string='Stop Event')
    highest_score = fields.Integer(string='Highest Score')
    league_id = fields.Many2one('fpl.leagues', string='League')
