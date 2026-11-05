from odoo import api, fields, models


class FPLEvents(models.Model):
    _name = 'fpl.events'
    _description = 'FPL Events'
    _order = 'season desc, event_id'

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
    is_current = fields.Boolean(string='Is Current', index=True)
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
    is_current_season = fields.Boolean(compute='_compute_is_current_season', search='_search_is_current_season')

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

    @api.depends('season')
    def _compute_is_current_season(self):
        current_season = self._get_current_season()
        for rec in self:
            rec.is_current_season = bool(current_season) and rec.season == current_season

    def _search_is_current_season(self, operator, value):
        if operator not in ('=', '!='):
            raise NotImplementedError("Unsupported search on 'is current season'.")
        positive = (operator == '=') == bool(value)
        return [('season', '=' if positive else '!=', self._get_current_season())]

    def _compute_fold(self):
        open_events = self.browse()
        for season in set(self.mapped('season')):
            # Nearest unfinished gameweek (live or next); the last one once the season is over
            open_events |= self.search([('season', '=', season), ('finished', '=', False)], order='event_id', limit=1) \
                or self.search([('season', '=', season)], order='event_id desc', limit=1)
        for rec in self:
            rec.fold = rec not in open_events

    @api.model
    def _get_current_event(self):
        """The live gameweek; off-season (or before GW1) the latest known one."""
        return self.search([('is_current', '=', True)], order='deadline_time desc', limit=1) \
            or self.search([], order='deadline_time desc', limit=1)

    @api.model
    def _get_current_season(self):
        """Current season label, e.g. '2026/2027' (False when nothing is synced yet)."""
        return self._get_current_event().season or False

    @api.model
    def _get_events_by_api_id(self, season=None):
        """``{FPL event id: record}`` of a season (the current one by default).

        FPL re-uses the ids 1..38 every season, so lookups must be scoped.
        """
        season = season or self._get_current_season()
        return {event.event_id: event for event in self.search([('season', '=', season)])}
