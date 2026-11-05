from markupsafe import Markup

from odoo import api, fields, models


class FPLPicks(models.Model):
    _name = 'fpl.picks'
    _description = 'FPL Picks'
    _order = 'position, id'

    element_id = fields.Many2one('fpl.elements', string='Player', index=True)
    position = fields.Integer(string='Position')
    multiplier = fields.Integer(string='Multiplier')
    team_id = fields.Many2one('fpl.teams', string='Team', related='element_id.fpl_team_id')
    is_captain = fields.Boolean(string='Is Captain')
    is_vice_captain = fields.Boolean(string='Is Vice Captain')
    element_type_id = fields.Many2one('fpl.element.types', string='Element Type')
    selling_price = fields.Float(string='Selling Price')
    purchase_price = fields.Float(string='Purchase Price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    manager_id = fields.Many2one('fpl.manager.team', string='Manager', required=True, index=True,
                                 ondelete='cascade')
    web_name = fields.Char(string='Web Name', related='element_id.web_name')
    team_display = fields.Html(compute='_compute_team_display', sanitize=False)

    @api.depends('team_id.photo_checksum', 'team_id.short_name')
    def _compute_team_display(self):
        for rec in self:
            rec.team_display = Markup(
                '<img src="%s" style="width: 20px; height: 20px; border-radius: 10px;"/> '
                '<span style="font-size: 12px;">%s</span>'
            ) % (rec.team_id._logo_url(), rec.team_id.short_name or '') if rec.team_id else False
