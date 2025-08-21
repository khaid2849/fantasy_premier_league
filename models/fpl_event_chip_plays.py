from odoo import models, fields, api, _

class FPLEventChipPlays(models.Model):
    _name = 'fpl.event.chip.plays'
    _description = 'FPL Event Chip Plays'
    
    event_id = fields.Many2one('fpl.events', string=_('Event'), required=True, ondelete='cascade')
    chip_name = fields.Char(string=_('Chip Name'), required=True)
    num_played = fields.Integer(string=_('Number Played'), default=0)
    
    _sql_constraints = [
        ('unique_event_chip', 'unique(event_id, chip_name)', 'Chip name must be unique per event!'),
    ]