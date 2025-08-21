from odoo import models, fields, api, _

class FPLChips(models.Model):
    _name = 'fpl.chips'
    _description = 'FPL Chips'

    chip_id = fields.Char(string=_('ID'))
    name = fields.Char(string=_('Name'))
    number = fields.Integer(string=_('Number'))
    start_event = fields.Integer(string=_('Start Event'))
    stop_event = fields.Integer(string=_('Stop Event'))
    chip_type = fields.Char(string=_('Chip Type'))
    event_id = fields.Many2one('fpl.events', string=_('Event ID'))