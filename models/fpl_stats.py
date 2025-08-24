from odoo import models, fields, api, _

class FplTeamAGoalsScored(models.Model):
    _name = 'fpl.team.a.goals.scored'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Goals Scored'))
    web_name = fields.Char(related='element_id.web_name')
    

class FplTeamAAssistsScored(models.Model):
    _name = 'fpl.team.a.assists'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Assists'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamAOwnGoals(models.Model):
    _name = 'fpl.team.a.own.goals'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Own Goals'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamAPenaltiesSaveds(models.Model):
    _name = 'fpl.team.a.penalties.saved'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Penalties Saved'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamAPenaltiesMissedScored(models.Model):
    _name = 'fpl.team.a.penalties.missed.scored'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Penalties Missed'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamAYellowCards(models.Model):
    _name = 'fpl.team.a.yellow.cards'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Yellow Cards'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamARedCards(models.Model):
    _name = 'fpl.team.a.red.cards'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Red Cards'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamAGoalsSaved(models.Model):
    _name = 'fpl.team.a.goals.saved'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Goals Saved'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamABonus(models.Model):
    _name = 'fpl.team.a.bonus'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Bonus'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamABps(models.Model):
    _name = 'fpl.team.a.bps'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Bonus Points System'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamADefensiveContribution(models.Model):
    _name = 'fpl.team.a.defensive.contribution'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Defensive Contribution'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBGoalsScored(models.Model):
    _name = 'fpl.team.h.goals.scored'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Goals Scored'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBAssistsScored(models.Model):
    _name = 'fpl.team.h.assists'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Assists'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBOwnGoals(models.Model):
    _name = 'fpl.team.h.own.goals'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Own Goals'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBPenaltiesSaveds(models.Model):
    _name = 'fpl.team.h.penalties.saved'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Penalties Saved'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBPenaltiesMissedScored(models.Model):
    _name = 'fpl.team.h.penalties.missed.scored'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Penalties Missed'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBYellowCards(models.Model):
    _name = 'fpl.team.h.yellow.cards'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Yellow Cards'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBRedCards(models.Model):
    _name = 'fpl.team.h.red.cards'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Red Cards'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBGoalsSaved(models.Model):
    _name = 'fpl.team.h.goals.saved'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Goals Saved'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBBonus(models.Model):
    _name = 'fpl.team.h.bonus'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Bonus'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBBps(models.Model):
    _name = 'fpl.team.h.bps'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Bonus Points System'))
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBDefensiveContribution(models.Model):
    _name = 'fpl.team.h.defensive.contribution'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string=_('Stats'))
    element_id = fields.Many2one('fpl.elements', string=_('Player'))
    value = fields.Integer(string=_('Defensive Contribution'))
    web_name = fields.Char(related='element_id.web_name')