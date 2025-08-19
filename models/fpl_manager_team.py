from odoo import models, fields, api, _

class FPLManagerTeam(models.Model):
    _name = 'fpl.manager.team'
    _description = 'FPL Manager Team'
    
    manager_id = fields.Char(string=_('Manager ID'))
    #Manager Data
    date_of_birth = fields.Date(string=_('Date of Birth'))
    default_event = fields.Integer(string=_('Default Event'))
    dirty = fields.Boolean(string=_('Dirty'))
    first_name = fields.Char(string=_('First Name'))
    last_name = fields.Char(string=_('Last Name'))
    full_name = fields.Char(string=_('Full Name'))
    email = fields.Char(string=_('Email'))
    gender = fields.Selection([('M', _('Male')), ('F', _('Female') )], string=_('Gender'))
    _id = fields.Char(string=_('ID'))
    region = fields.Char(string=_('Region'))
    entry_email = fields.Char(string=_('Entry Email'))
    entry_language = fields.Char(string=_('Entry Language'))
    sso_id = fields.Char(string=_('SSO ID'))
    
    #Manager Entry Summary
    joined_time = fields.Datetime(string=_('Joined Time'))
    started_event = fields.Integer(string=_('Started Event'))
    favourite_team = fields.Many2one('epl.teams', string=_('Favourite Team'))
    player_first_name = fields.Char(string=_('Player First Name'))
    player_last_name = fields.Char(string=_('Player Last Name'))
    player_region_id = fields.Char(string=_('Player Region ID'))
    player_region_name = fields.Char(string=_('Player Region Name'))
    player_region_iso_code_short = fields.Char(string=_('Player Region ISO Code Short'))
    player_region_iso_code_long = fields.Char(string=_('Player Region ISO Code Long'))
    years_active = fields.Integer(string=_('Years Active'))
    summary_overall_points = fields.Integer(string=_('Summary Overall Points'))
    summary_overall_rank = fields.Integer(string=_('Summary Overall Rank'))
    summary_event_points = fields.Integer(string=_('Summary Event Points'))
    summary_event_rank = fields.Integer(string=_('Summary Event Rank'))
    current_event = fields.Integer(string=_('Current Event'))
    name = fields.Char(string=_('Name'))
    name_change_blocked = fields.Boolean(string=_('Name Change Blocked'))
    kits = fields.Char(string=_('Kits'))
    last_deadline_bank = fields.Integer(string=_('Last Deadline Bank'))
    last_deadline_value = fields.Integer(string=_('Last Deadline Value'))
    last_deadline_total_transfers = fields.Integer(string=_('Last Deadline Total Transfers'))
    club_badge_src = fields.Char(string=_('Club Badge Src'))
    league_ids = fields.One2many('fpl.leagues', 'manager_id', string=_('League IDs'))
    pick_ids = fields.One2many('fpl.picks', 'manager_id', string=_('Element IDs'))
    manager_chips = fields.One2many('fpl.manager.chips', 'manager_id', string=_('Manager Chips'))
    
    #Transfer Info
    cost = fields.Integer(string=_('Cost'))
    status = fields.Char(string=_('Status'))
    limit = fields.Integer(string=_('Transfers Limit'))
    made = fields.Float(string=_('Transfers Made'))
    bank = fields.Float(string=_('In the Bank'))
    value = fields.Float(string=_('Squad Value'))

    def action_verify_team_data(self):
        self.ensure_one()
        action_ref = 'fantasy_premier_league.fpl_manager_team_wizard_form'
        action = self.env['ir.actions.act_window']._for_xml_id(action_ref)

        return action