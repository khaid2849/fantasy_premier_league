from odoo import models, fields, api, _

class FPLManagerChips(models.Model):
    _name = 'fpl.manager.chips'
    _description = 'FPL Manager Chips'

    status_for_entry = fields.Char(string=_('Status for Entry'))
    played_by_entry = fields.Char(string=_('Played by Entry'))
    chip_id = fields.Many2one('fpl.chips', string=_('Chip'))
    number = fields.Integer(string=_('Number'), related='chip_id.number')
    name = fields.Char(string=_('Name'), related='chip_id.name')
    start_event = fields.Integer(string=_('Start Event'), related='chip_id.start_event')
    stop_event = fields.Integer(string=_('Stop Event'), related='chip_id.stop_event')
    chip_type = fields.Char(string=_('Chip Type'), related='chip_id.chip_type')
    is_pending = fields.Boolean(string=_('Is Pending'))
    _id = fields.Char(string=_('ID'), related='chip_id._id')
    manager_id = fields.Many2one('fpl.manager.team', string=_('Manager'))