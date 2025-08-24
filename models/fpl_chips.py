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
    show_name = fields.Selection(
        [('wildcard', _('Wildcard')), ('freehit', _('Free Hit')), ('bboost', _('Bench Boost')), ('3xc', _('Triple Captain'))],
        compute='_compute_show_name'
    )
    is_bench_boost = fields.Boolean(default=False)
    is_wildcard = fields.Boolean(default=False)
    is_free_hit = fields.Boolean(default=False)
    is_triple_captain = fields.Boolean(default=False) 

    @api.depends('name')
    def _compute_show_name(self):
        for chip in self:
            chip.show_name = chip.name