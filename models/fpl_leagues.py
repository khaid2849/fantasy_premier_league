from odoo import models, fields, api, _

class FPLLeagues(models.Model):
    _name = 'fpl.leagues'
    _description = 'FPL Leagues'

    type = fields.Selection([('classic', _('Classic')), ('h2h', _('H2H'))], string=_('League Type'))
    manager_id = fields.Many2one('fpl.manager.team', string=_('Manager ID'))
    league_id = fields.Integer(string=_('League ID'))
    name = fields.Char(string=_('Name'))
    short_name = fields.Char(string=_('Short Name'))
    created = fields.Datetime(string=_('Created'))
    closed = fields.Boolean(string=_('Closed'))
    max_entries = fields.Integer(string=_('Max Entries'))
    league_type = fields.Char(string=_('League Type'))
    scoring = fields.Char(string=_('Scoring'))
    admin_entry = fields.Integer(string=_('Admin Entry'))
    start_event = fields.Integer(string=_('Start Event'))
    entry_can_leave = fields.Boolean(string=_('Entry Can Leave'))
    entry_can_admin = fields.Boolean(string=_('Entry Can Admin'))
    entry_can_invite = fields.Boolean(string=_('Entry Can Invite'))
    has_cup = fields.Boolean(string=_('Has Cup'))
    rank_count = fields.Integer(string=_('Rank Count'))
    entry_percentile_rank = fields.Integer(string=_('Entry Percentile Rank'))
    entry_rank = fields.Integer(string=_('Entry Rank'))
    entry_last_rank = fields.Integer(string=_('Entry Last Rank'))
    phase_ids = fields.One2many('fpl.phases', 'league_id', string=_('Phases'))