from odoo import api, models, fields
from .master_data import MAPPING_SELECTIONS_DATA

class FplElementStats(models.Model):
    _name = 'fpl.element.stats'
    _description = 'FPL Element Stats'

    identifier = fields.Selection(selection=MAPPING_SELECTIONS_DATA['element_stats'], string='Identifier')
    points = fields.Integer(string='Integer')
    value = fields.Integer(string='Value')
    points_modification = fields.Integer(string='Points modification')
    pick_line_id = fields.Many2one('fpl.gameweek.pick.lines', string='Pick')