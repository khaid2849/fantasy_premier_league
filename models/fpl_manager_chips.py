from odoo import models, fields, api

class FPLManagerChips(models.Model):
    _name = 'fpl.manager.chips'
    _description = 'FPL Manager Chips'

    status_for_entry = fields.Selection([('available', 'Available'), ('played', 'Played'), ('used', 'Used'), ('unavailable', 'Unavailable')], string='Status for Entry')
    played_by_entry = fields.Char(string='Played by Entry')
    chip_id = fields.Many2one('fpl.chips', string='Chip')
    number = fields.Integer(string='Number', related='chip_id.number')
    name = fields.Char(string='Name', related='chip_id.name')
    start_event = fields.Integer(string='Start Event', related='chip_id.start_event')
    stop_event = fields.Integer(string='Stop Event', related='chip_id.stop_event')
    chip_type = fields.Char(string='Chip Type', related='chip_id.chip_type')
    is_pending = fields.Boolean(string='Is Pending')
    fpl_chip_id = fields.Char(string='ID', related='chip_id.chip_id')
    manager_id = fields.Many2one('fpl.manager.team', string='Manager')
    show_name = fields.Selection(related='chip_id.show_name')
    is_bench_boost = fields.Boolean(related='chip_id.is_bench_boost')
    is_wildcard = fields.Boolean(related='chip_id.is_wildcard')
    is_free_hit = fields.Boolean(related='chip_id.is_free_hit')
    is_triple_captain = fields.Boolean(related='chip_id.is_triple_captain') 