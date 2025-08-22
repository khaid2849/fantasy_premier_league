from odoo import models, fields, api, _

class FPLPicks(models.Model):
    _name = 'fpl.picks'
    _description = 'FPL Picks'

    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    position = fields.Char(string=_('Position'))
    multiplier = fields.Integer(string=_('Multiplier'))
    team_id = fields.Many2one('fpl.teams', string=_('Team'), related='element_id.fpl_team_id')
    is_captain = fields.Boolean(string=_('Is Captain'))
    is_vice_captain = fields.Boolean(string=_('Is Vice Captain'))
    element_type_id = fields.Many2one('fpl.element.types', string=_('Element Type'))
    selling_price = fields.Float(string=_('Selling Price'))
    purchase_price = fields.Float(string=_('Purchase Price'))
    currency_id = fields.Many2one('res.currency', string='Currency')
    manager_id = fields.Many2one('fpl.manager.team', string=_('Manager'))
    web_name = fields.Char(string=_('Web Name'), related='element_id.web_name')