from odoo import models, fields, api, _

class FPLPicks(models.Model):
    _name = 'fpl.picks'
    _description = 'FPL Picks'

    element_id = fields.Many2one('epl.players', string=_('Player'))
    position = fields.Char(string=_('Position'))
    team = fields.Many2one('epl.teams', string=_('Team'))
    is_captain = fields.Boolean(string=_('Is Captain'))
    is_vice_captain = fields.Boolean(string=_('Is Vice Captain'))
    element_type = fields.Many2one('fpl.element.types', string=_('Element Type'))
    selling_price = fields.Float(string=_('Selling Price'))
    purchase_price = fields.Float(string=_('Purchase Price'))
    manager_id = fields.Many2one('fpl.manager.team', string=_('Manager'))