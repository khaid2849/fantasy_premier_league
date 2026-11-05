from odoo import api, fields, models

CHIP_LABELS = {
    'wildcard': 'Wildcard',
    'freehit': 'Free Hit',
    'bboost': 'Bench Boost',
    '3xc': 'Triple Captain',
    'manager': 'Assistant Manager',
}


class FPLChips(models.Model):
    _name = 'fpl.chips'
    _description = 'FPL Chips'
    _order = 'start_event, id'

    chip_id = fields.Char(string='ID', index=True)
    name = fields.Char(string='Name')
    number = fields.Integer(string='Number')
    start_event = fields.Integer(string='Start Event')
    stop_event = fields.Integer(string='Stop Event')
    chip_type = fields.Char(string='Chip Type')
    event_id = fields.Many2one('fpl.events', string='Event ID')
    # Char (not Selection): FPL introduces new chips from time to time, an
    # unknown value must not break the read of the record.
    show_name = fields.Char(string='Chip', compute='_compute_show_name')
    is_bench_boost = fields.Boolean(compute='_compute_chip_kind', store=True)
    is_wildcard = fields.Boolean(compute='_compute_chip_kind', store=True)
    is_free_hit = fields.Boolean(compute='_compute_chip_kind', store=True)
    is_triple_captain = fields.Boolean(compute='_compute_chip_kind', store=True)

    @api.depends('name')
    def _compute_show_name(self):
        for chip in self:
            chip.show_name = CHIP_LABELS.get(chip.name) or (chip.name or '').replace('_', ' ').title()

    @api.depends('name')
    def _compute_chip_kind(self):
        for chip in self:
            chip.is_bench_boost = chip.name == 'bboost'
            chip.is_wildcard = chip.name == 'wildcard'
            chip.is_free_hit = chip.name == 'freehit'
            chip.is_triple_captain = chip.name == '3xc'
