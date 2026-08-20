from odoo import models, fields, api, _

class FPLEvents(models.Model):
    _name = 'fpl.events'
    _description = 'FPL Events'

    event_id = fields.Integer(string=_('ID'), index=True)
    name = fields.Char(string=_('Name'))
    deadline_time = fields.Datetime(string=_('Deadline Time'))
    season = fields.Char(string=_('Season'), compute='_compute_season', store=True, index=True)
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
    event_chip_plays_ids = fields.One2many('fpl.event.chip.plays', 'event_id', string=_('Event Chip Plays'))

    _sql_constraints = [
        ('event_id_season_uniq', 'unique(event_id, season)',
         'An event with this ID already exists for this season.'),
    ]

    @api.depends('deadline_time')
    def _compute_season(self):
        for rec in self:
            rec.season = self._season_from_date(rec.deadline_time)

    @api.model
    def _season_from_date(self, date_value):
        """English football season runs Aug-May, so a deadline in Jul-Dec
        belongs to the season starting that year, and a deadline in Jan-Jun
        belongs to the season that started the previous year.
        """
        if not date_value:
            return False
        year = date_value.year
        if date_value.month >= 7:
            return f"{year}/{year + 1}"
        return f"{year - 1}/{year}"