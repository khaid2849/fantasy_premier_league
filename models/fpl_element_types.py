from odoo import api, fields, models


class FPLElementTypes(models.Model):
    _name = 'fpl.element.types'
    _description = 'FPL Element Types'
    _rec_name = 'singular_name_short'
    _order = 'element_type_id'

    element_type_id = fields.Char(string='Element Type ID', index=True)
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

    @api.model
    def _get_types_by_api_id(self):
        """``{FPL element type id (str): record}``"""
        return {rec.element_type_id: rec for rec in self.search([])}
