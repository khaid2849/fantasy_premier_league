from odoo import models, fields, api, _

class FPLEvents(models.Model):
    _name = 'fpl.events'
    _description = 'FPL Events'

    event_id = fields.Integer(string=_('ID'))
    name = fields.Char(string=_('Name'))
    deadline_time = fields.Datetime(string=_('Deadline Time'))
    release_time = fields.Datetime(string=_('Release Time'))
    average_entry_score = fields.Float(string=_('Average Entry Score'))
    finished = fields.Boolean(string=_('Finished'))
    data_checked = fields.Boolean(string=_('Data Checked'))
    highest_scoring_entry = fields.Integer(string=_('Highest Scoring Entry'))
    deadline_time_epoch = fields.Integer(string=_('Deadline Time Epoch'))
    deadline_time_game_offset = fields.Integer(string=_('Deadline Time Game Offset'))
    highest_score = fields.Integer(string=_('Highest Score'))
    is_previous = fields.Boolean(string=_('Is Previous'))
    is_current = fields.Boolean(string=_('Is Current'))
    is_next = fields.Boolean(string=_('Is Next'))
    cup_leagues_created = fields.Boolean(string=_('Cup Leagues Created'))
    h2h_ko_matches_created = fields.Boolean(string=_('H2H KO Matches Created'))
    can_enter = fields.Boolean(string=_('Can Enter'))
    can_manage = fields.Boolean(string=_('Can Manage'))
    released = fields.Boolean(string=_('Released'))
    ranked_count = fields.Integer(string=_('Ranked Count'))
    most_selected = fields.Integer(string=_('Most Selected'))
    most_transferred_in = fields.Integer(string=_('Most Transferred In'))
    top_element_id = fields.Many2one('fpl.elements', string=_('Top Element ID'))
    transfers_made = fields.Integer(string=_('Transfers Made'))
    most_captained = fields.Integer(string=_('Most Captained'))
    most_vice_captained = fields.Integer(string=_('Most Vice Captained'))
    chip_ids = fields.One2many('fpl.chips', 'event_id', string=_('Chip Plays'))