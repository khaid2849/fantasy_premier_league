from odoo import models, fields, api

class FPLEventChipPlays(models.Model):
    _name = 'fpl.event.chip.plays'
    _description = 'FPL Event Chip Plays'
    
    event_id = fields.Many2one('fpl.events', string='Event', required=True, ondelete='cascade')
    chip_name = fields.Char(string='Chip Name', required=True)
    num_played = fields.Integer(string='Number Played', default=0)
    
    _sql_constraints = [
        ('unique_event_chip', 'unique(event_id, chip_name)', 'Chip name must be unique per event!'),
    ]