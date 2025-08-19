from odoo import models, fields, api, _

class FPLTeams(models.Model):
    _name = 'fpl.teams'
    _description = 'FPL Teams'

    name = fields.Char(string=_('Name'))
    code = fields.Char(string=_('Code'))
    form = fields.Char(string=_('Form'))
    team_id = fields.Integer(string=_('Team ID'))
    loss = fields.Integer(string=_('Loss'))
    played = fields.Integer(string=_('Played'))
    points = fields.Integer(string=_('Points'))
    position = fields.Integer(string=_('Position'))
    short_name = fields.Char(string=_('Short Name'))
    strength = fields.Integer(string=_('Strength'))
    team_division = fields.Char(string=_('Team Division'))
    unavailable = fields.Boolean(string=_('Unavailable'))
    win = fields.Integer(string=_('Win'))
    strength_overall_home = fields.Integer(string=_('Strength Overall Home'))
    strength_overall_away = fields.Integer(string=_('Strength Overall Away'))
    strength_attack_home = fields.Integer(string=_('Strength Attack Home'))
    strength_attack_away = fields.Integer(string=_('Strength Attack Away'))
    strength_defence_home = fields.Integer(string=_('Strength Defence Home'))
    strength_defence_away = fields.Integer(string=_('Strength Defence Away'))
    pulse_id = fields.Integer(string=_('Pulse ID'))