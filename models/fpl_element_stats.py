from odoo import api, models, fields, _
from .master_data import MAPPING_SELECTIONS_DATA

class FplElementStats(models.Model):
    _name = 'fpl.element.stats'

    identifier = fields.Selection(selection=MAPPING_SELECTIONS_DATA['element_stats'], string=_('Identifier'))
    points = fields.Integer(string=_('Integer'))
    value = fields.Integer(string=_('Value'))
    points_modification = fields.Integer(string=_('Points modification'))
    pick_line_id = fields.Many2one('fpl.gameweek.pick.lines', string=_('Pick'))