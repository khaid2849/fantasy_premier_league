from odoo import models, fields, api

class FPLPhases(models.Model):
    _name = 'fpl.phases'
    _description = 'FPL Phases'

    phase_id = fields.Integer(string='ID')
    name = fields.Char(string='Name')
    start_event = fields.Integer(string='Start Event')
    stop_event = fields.Integer(string='Stop Event')
    highest_score = fields.Integer(string='Highest Score')
    league_id = fields.Many2one('fpl.leagues', string='League')