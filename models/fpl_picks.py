from odoo import models, fields, api

class FPLPicks(models.Model):
    _name = 'fpl.picks'
    _description = 'FPL Picks'

    element_id = fields.Many2one('fpl.elements', string='Player')
    position = fields.Char(string='Position')
    multiplier = fields.Integer(string='Multiplier')
    team_id = fields.Many2one('fpl.teams', string='Team', related='element_id.fpl_team_id')
    is_captain = fields.Boolean(string='Is Captain')
    is_vice_captain = fields.Boolean(string='Is Vice Captain')
    element_type_id = fields.Many2one('fpl.element.types', string='Element Type')
    selling_price = fields.Float(string='Selling Price')
    purchase_price = fields.Float(string='Purchase Price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    manager_id = fields.Many2one('fpl.manager.team', string='Manager')
    web_name = fields.Char(string='Web Name', related='element_id.web_name')
    team_display = fields.Html(compute='_compute_team_display')

    @api.depends('team_id')
    def _compute_team_display(self):
        for rec in self:
            rec.team_display = f'<img src="/fantasy_premier_league/static/src/img/teams_logo/{rec.team_id.code}.svg" style="width: 20px; height: 20px; border-radius: 10px;"/> <span style="font-size: 12px;">{rec.team_id.short_name}</span>'