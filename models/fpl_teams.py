import base64

from odoo import models, fields, api, _
from odoo.tools.misc import file_path

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
    draw = fields.Integer(string=_('Draw'))
    strength_overall_home = fields.Integer(string=_('Strength Overall Home'))
    strength_overall_away = fields.Integer(string=_('Strength Overall Away'))
    strength_attack_home = fields.Integer(string=_('Strength Attack Home'))
    strength_attack_away = fields.Integer(string=_('Strength Attack Away'))
    strength_defence_home = fields.Integer(string=_('Strength Defence Home'))
    strength_defence_away = fields.Integer(string=_('Strength Defence Away'))
    pulse_id = fields.Integer(string=_('Pulse ID'))
    photo = fields.Image(string=_('Photo'))

    # @api.depends('code')
    # def _compute_team_photo(self):
    #     for rec in self:
    #         team_photo_file = file_path('fantasy_premier_league', 'static/src/img/{code}.svg'.format(code=rec.code))
    #         rec.photo = base64.b64encode(open(team_photo_file, 'rb').read()) if team_photo_file else False