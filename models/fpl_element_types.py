from odoo import models, fields, api, _

class FPLElementTypes(models.Model):
    _name = 'fpl.element.types'
    _description = 'FPL Element Types'

    element_type_id = fields.Char(string=_('Element Type ID'))
    plural_name = fields.Char(string=_('Plural Name'))
    plural_name_short = fields.Char(string=_('Plural Name Short'))
    singular_name = fields.Char(string=_('Singular Name'))
    singular_name_short = fields.Char(string=_('Singular Name Short'))
    squad_select = fields.Integer(string=_('Squad Select'))
    squad_min_select = fields.Integer(string=_('Squad Min Select'))
    squad_max_select = fields.Integer(string=_('Squad Max Select'))
    squad_min_play = fields.Integer(string=_('Squad Min Play'))
    squad_max_play = fields.Integer(string=_('Squad Max Play'))
    ui_shirt_specific = fields.Boolean(string=_('UI Shirt Specific'))
    element_count = fields.Integer(string=_('Element Count'))
    display_name = fields.Char(string=_('Display Name'), compute='_compute_display_name')
    
    @api.depends('singular_name_short')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.singular_name_short