from odoo import models, fields, api

class FPLEvents(models.Model):
    _name = 'fpl.events'
    _description = 'FPL Events'

    event_id = fields.Integer(string='ID', index=True)
    name = fields.Char(string='Name')
    deadline_time = fields.Datetime(string='Deadline Time')
    season = fields.Char(string='Season', compute='_compute_season', store=True, index=True)
    release_time = fields.Datetime(string='Release Time')
    average_entry_score = fields.Float(string='Average Entry Score')
    finished = fields.Boolean(string='Finished')
    data_checked = fields.Boolean(string='Data Checked')
    # Kanban folding (_fold_name): only the nearest unfinished gameweek is unfolded
    fold = fields.Boolean(string='Folded in Kanban', compute='_compute_fold')
    highest_scoring_entry = fields.Integer(string='Highest Scoring Entry')
    deadline_time_epoch = fields.Integer(string='Deadline Time Epoch')
    deadline_time_game_offset = fields.Integer(string='Deadline Time Game Offset')
    highest_score = fields.Integer(string='Highest Score')
    is_previous = fields.Boolean(string='Is Previous')
    is_current = fields.Boolean(string='Is Current')
    is_next = fields.Boolean(string='Is Next')
    cup_leagues_created = fields.Boolean(string='Cup Leagues Created')
    h2h_ko_matches_created = fields.Boolean(string='H2H KO Matches Created')
    can_enter = fields.Boolean(string='Can Enter')
    can_manage = fields.Boolean(string='Can Manage')
    released = fields.Boolean(string='Released')
    ranked_count = fields.Integer(string='Ranked Count')
    most_selected = fields.Integer(string='Most Selected')
    most_transferred_in = fields.Integer(string='Most Transferred In')
    top_element_id = fields.Many2one('fpl.elements', string='Top Element ID')
    transfers_made = fields.Integer(string='Transfers Made')
    most_captained = fields.Integer(string='Most Captained')
    most_vice_captained = fields.Integer(string='Most Vice Captained')
    chip_ids = fields.One2many('fpl.chips', 'event_id', string='Chip Plays')
    event_chip_plays_ids = fields.One2many('fpl.event.chip.plays', 'event_id', string='Event Chip Plays')

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

    def _compute_fold(self):
        open_events = self.browse()
        for season in set(self.mapped('season')):
            # Nearest unfinished gameweek (live or next); the last one once the season is over
            open_events |= self.search([('season', '=', season), ('finished', '=', False)], order='event_id', limit=1) \
                or self.search([('season', '=', season)], order='event_id desc', limit=1)
        for rec in self:
            rec.fold = rec not in open_events
