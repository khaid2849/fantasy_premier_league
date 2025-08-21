from odoo import models, fields, api, _

class FPLPhases(models.Model):
    _name = 'fpl.phases'
    _description = 'FPL Phases'

    phase_id = fields.Integer(string=_('ID'))
    name = fields.Char(string=_('Name'))
    start_event = fields.Integer(string=_('Start Event'))
    stop_event = fields.Integer(string=_('Stop Event'))
    highest_score = fields.Integer(string=_('Highest Score'))
    league_id = fields.Many2one('fpl.leagues', string=_('League'))