from odoo import models, fields, api, _


class FplGameweekPickLines(models.Model):
    _name = 'fpl.gameweek.pick.lines'
    _description = 'FPL Gameweek Pick Lines'

    gameweek_pick_id = fields.Many2one('fpl.gameweek.picks', string=_('Gameweek Pick'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    position = fields.Integer(string=_('Points'))
    multiplier = fields.Integer(string=_('Multiplier'))
    is_captain = fields.Boolean(string=_('Is Captain'))
    is_vice_captain = fields.Boolean(string=_('Is Vice Captain'))
    element_type_id = fields.Many2one('fpl.element.types', string=_('Element Type'))
    team_id = fields.Many2one('fpl.teams', string=_('Team'))
    team_name = fields.Char(related='team_id.name')
    parent_id = fields.Many2one('fpl.gameweek.pick.lines', string=_('Parent'))
    web_name = fields.Char(related='element_id.web_name')
    plural_name_short= fields.Char(related='element_type_id.plural_name_short')
    child_ids = fields.One2many('fpl.gameweek.pick.lines', 'parent_id', string=_('Children'))
