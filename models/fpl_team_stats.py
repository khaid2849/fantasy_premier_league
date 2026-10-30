from odoo import models, fields, api

class FplTeamAGoalsScored(models.Model):
    _name = 'fpl.team.a.goals.scored'
    _description = 'FPL Away Team Goals Scored'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Goals Scored')
    web_name = fields.Char(related='element_id.web_name')
    

class FplTeamAAssistsScored(models.Model):
    _name = 'fpl.team.a.assists'
    _description = 'FPL Away Team Assists'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Assists')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamAOwnGoals(models.Model):
    _name = 'fpl.team.a.own.goals'
    _description = 'FPL Away Team Own Goals'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Own Goals')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamAPenaltiesSaveds(models.Model):
    _name = 'fpl.team.a.penalties.saved'
    _description = 'FPL Away Team Penalties Saved'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Penalties Saved')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamAPenaltiesMissedScored(models.Model):
    _name = 'fpl.team.a.penalties.missed.scored'
    _description = 'FPL Away Team Penalties Missed Scored'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Penalties Missed')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamAYellowCards(models.Model):
    _name = 'fpl.team.a.yellow.cards'
    _description = 'FPL Away Team Yellow Cards'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Yellow Cards')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamARedCards(models.Model):
    _name = 'fpl.team.a.red.cards'
    _description = 'FPL Away Team Red Cards'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Red Cards')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamAGoalsSaved(models.Model):
    _name = 'fpl.team.a.goals.saved'
    _description = 'FPL Away Team Goals Saved'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Goals Saved')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamABonus(models.Model):
    _name = 'fpl.team.a.bonus'
    _description = 'FPL Away Team Bonus'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Bonus')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamABps(models.Model):
    _name = 'fpl.team.a.bps'
    _description = 'FPL Away Team BPS'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Bonus Points System')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamADefensiveContribution(models.Model):
    _name = 'fpl.team.a.defensive.contribution'
    _description = 'FPL Away Team Defensive Contribution'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Defensive Contribution')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBGoalsScored(models.Model):
    _name = 'fpl.team.h.goals.scored'
    _description = 'FPL Home Team Goals Scored'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Goals Scored')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBAssistsScored(models.Model):
    _name = 'fpl.team.h.assists'
    _description = 'FPL Home Team Assists'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Assists')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBOwnGoals(models.Model):
    _name = 'fpl.team.h.own.goals'
    _description = 'FPL Home Team Own Goals'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Own Goals')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBPenaltiesSaveds(models.Model):
    _name = 'fpl.team.h.penalties.saved'
    _description = 'FPL Home Team Penalties Saved'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Penalties Saved')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBPenaltiesMissedScored(models.Model):
    _name = 'fpl.team.h.penalties.missed.scored'
    _description = 'FPL Home Team Penalties Missed Scored'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Penalties Missed')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBYellowCards(models.Model):
    _name = 'fpl.team.h.yellow.cards'
    _description = 'FPL Home Team Yellow Cards'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Yellow Cards')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBRedCards(models.Model):
    _name = 'fpl.team.h.red.cards'
    _description = 'FPL Home Team Red Cards'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Red Cards')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBGoalsSaved(models.Model):
    _name = 'fpl.team.h.goals.saved'
    _description = 'FPL Home Team Goals Saved'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Goals Saved')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBBonus(models.Model):
    _name = 'fpl.team.h.bonus'
    _description = 'FPL Home Team Bonus'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Bonus')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBBps(models.Model):
    _name = 'fpl.team.h.bps'
    _description = 'FPL Home Team BPS'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Bonus Points System')
    web_name = fields.Char(related='element_id.web_name')

class FplTeamBDefensiveContribution(models.Model):
    _name = 'fpl.team.h.defensive.contribution'
    _description = 'FPL Home Team Defensive Contribution'

    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Stats')
    element_id = fields.Many2one('fpl.elements', string='Player')
    value = fields.Integer(string='Defensive Contribution')
    web_name = fields.Char(related='element_id.web_name')