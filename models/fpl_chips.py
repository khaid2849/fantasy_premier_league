from odoo import models, fields, api

class FPLChips(models.Model):
    _name = 'fpl.chips'
    _description = 'FPL Chips'

    chip_id = fields.Char(string='ID')
    name = fields.Char(string='Name')
    number = fields.Integer(string='Number')
    start_event = fields.Integer(string='Start Event')
    stop_event = fields.Integer(string='Stop Event')
    chip_type = fields.Char(string='Chip Type')
    event_id = fields.Many2one('fpl.events', string='Event ID')
    show_name = fields.Selection(
        [('wildcard', 'Wildcard'), ('freehit', 'Free Hit'), ('bboost', 'Bench Boost'), ('3xc', 'Triple Captain')],
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