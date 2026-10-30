from odoo import models, fields, api

class FPLElementTypes(models.Model):
    _name = 'fpl.element.types'
    _description = 'FPL Element Types'

    element_type_id = fields.Char(string='Element Type ID')
    plural_name = fields.Char(string='Plural Name')
    plural_name_short = fields.Char(string='Plural Name Short')
    singular_name = fields.Char(string='Singular Name')
    singular_name_short = fields.Char(string='Singular Name Short')
    squad_select = fields.Integer(string='Squad Select')
    squad_min_select = fields.Integer(string='Squad Min Select')
    squad_max_select = fields.Integer(string='Squad Max Select')
    squad_min_play = fields.Integer(string='Squad Min Play')
    squad_max_play = fields.Integer(string='Squad Max Play')
    ui_shirt_specific = fields.Boolean(string='UI Shirt Specific')
    element_count = fields.Integer(string='Element Count')
    display_name = fields.Char(string='Display Name', compute='_compute_display_name')
    
    @api.depends('singular_name_short')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.singular_name_short