import base64

from odoo import models, fields, api
from odoo.tools.misc import file_path

class FPLTeams(models.Model):
    _name = 'fpl.teams'
    _description = 'FPL Teams'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code', index=True)
    form = fields.Char(string='Form')
    team_id = fields.Integer(string='Team ID')
    loss = fields.Integer(string='Loss')
    played = fields.Integer(string='Played')
    points = fields.Integer(string='Points')
    position = fields.Integer(string='Position')
    short_name = fields.Char(string='Short Name')
    strength = fields.Integer(string='Strength')
    team_division = fields.Char(string='Team Division')
    unavailable = fields.Boolean(string='Unavailable')
    win = fields.Integer(string='Win')
    draw = fields.Integer(string='Draw')
    strength_overall_home = fields.Integer(string='Strength Overall Home')
    strength_overall_away = fields.Integer(string='Strength Overall Away')
    strength_attack_home = fields.Integer(string='Strength Attack Home')
    strength_attack_away = fields.Integer(string='Strength Attack Away')
    strength_defence_home = fields.Integer(string='Strength Defence Home')
    strength_defence_away = fields.Integer(string='Strength Defence Away')
    pulse_id = fields.Integer(string='Pulse ID')
    element_ids = fields.One2many('fpl.elements', 'fpl_team_id', string='Elements')
    photo = fields.Image(string='Photo')
    