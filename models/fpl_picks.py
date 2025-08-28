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
    team_display = fields.Html(compute='_compute_team_display')

    @api.depends('team_id')
    def _compute_team_display(self):
        for rec in self:
            rec.team_display = f'<img src="/fantasy_premier_league/static/src/img/teams_logo/{rec.team_id.code}.png" style="width: 20px; height: 20px; border-radius: 10px;"/> <span style="font-size: 12px;">{rec.team_id.short_name}</span>'