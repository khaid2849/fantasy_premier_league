import logging
from datetime import timedelta

from markupsafe import Markup

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Players refreshed per cron batch; the cron re-runs itself until every
# player is done (see ir.cron progress API), committing between batches.
SUMMARY_BATCH_SIZE = 100
# A player summary is considered fresh for that long
SUMMARY_MAX_AGE = timedelta(hours=5)


class FPLElements(models.Model):
    _name = 'fpl.elements'
    _inherit = ['fpl.api.mixin']
    _description = 'FPL Elements'
    _order = 'total_points desc, id'

    active = fields.Boolean(default=True,
                            help="Players that left the Premier League are archived by the bootstrap sync.")
    element_id = fields.Integer(string='Element ID', index=True)
    fpl_team_id = fields.Many2one('fpl.teams', string='FPL Team', index=True)
    team_id = fields.Integer(string='Team ID', related='fpl_team_id.team_id')
    team_code = fields.Char(string='Team Code', related='fpl_team_id.code')
    can_transact = fields.Boolean(string='Can Transact')
    can_select = fields.Boolean(string='Can Select')
    chance_of_playing_next_round = fields.Char(string='Chance of Playing Next Round')
    chance_of_playing_this_round = fields.Char(string='Chance of Playing This Round')
    # Stable player identifier across seasons ('element_id' is re-assigned every season)
    code = fields.Char(string='Code', index=True)
    cost_change_event = fields.Float(string='Cost Change Event')
    cost_change_event_fall = fields.Float(string='Cost Change Event Fall')
    cost_change_start = fields.Float(string='Cost Change Start')
    cost_change_start_fall = fields.Float(string='Cost Change Start Fall')
    dreamteam_count = fields.Integer(string='Dreamteam Count')
    element_type_id = fields.Many2one('fpl.element.types', string='Element Type', index=True)
    plural_name = fields.Char(string='Plural Name', related='element_type_id.plural_name')
    ep_next = fields.Char(string='EP Next')
    ep_this = fields.Char(string='EP This')
    event_points = fields.Float(string='Event Points')
    first_name = fields.Char(string='First Name')
    form = fields.Char(string='Form')
    in_dreamteam = fields.Boolean(string='In Dreamteam')
    news = fields.Char(string='News')
    news_added = fields.Char(string='News Added')
    now_cost = fields.Float(string='Now Cost')
    photo = fields.Binary(string='Photo')
    photo_checksum = fields.Char(string='Photo Source Checksum', readonly=True, copy=False)
    images_checked_at = fields.Datetime(string='Photo Checked At', readonly=True, copy=False)
    points_per_game = fields.Float(string='Points Per Game')
    removed = fields.Boolean(string='Removed')
    second_name = fields.Char(string='Second Name')
    selected_by_percent = fields.Char(string='Selected By Percent')
    special = fields.Boolean(string='Special')
    squad_number = fields.Char(string='Squad Number')
    status = fields.Selection(
        [
            ('a', 'Available'),
            ('u', 'Unavailable'),
            ('s', 'Suspended'),
            ('d', 'Doubtful'),
            ('i', 'Injured'),
            ('n', 'Not Available')
        ], string='Status')
    total_points = fields.Float(string='Total Points')
    transfers_in = fields.Float(string='Transfers In')
    transfers_in_event = fields.Float(string='Transfers In Event')
    transfers_out = fields.Float(string='Transfers Out')
    transfers_out_event = fields.Float(string='Transfers Out Event')
    value_form = fields.Char(string='Value Form')
    value_season = fields.Char(string='Value Season')
    web_name = fields.Char(string='Web Name')
    country_id = fields.Many2one('res.country', string='Country')
    region = fields.Char(string='Region')
    team_join_date = fields.Date(string='Team Join Date')
    birth_date = fields.Date(string='Birth Date')
    has_temporary_code = fields.Boolean(string='Has Temporary Code')
    opta_code = fields.Char(string='Opta Code')
    minutes = fields.Integer(string='Minutes')
    goals_scored = fields.Integer(string='Goals Scored')
    assists = fields.Integer(string='Assists')
    clean_sheets = fields.Integer(string='Clean Sheets')
    goals_conceded = fields.Integer(string='Goals Conceded')
    own_goals = fields.Integer(string='Own Goals')
    penalties_saved = fields.Integer(string='Penalties Saved')
    penalties_missed = fields.Integer(string='Penalties Missed')
    yellow_cards = fields.Integer(string='Yellow Cards')
    red_cards = fields.Integer(string='Red Cards')
    saves = fields.Integer(string='Saves')
    bonus = fields.Integer(string='Bonus')
    bps = fields.Integer(string='BPS')
    influence = fields.Char(string='Influence')
    creativity = fields.Char(string='Creativity')
    threat = fields.Char(string='Threat')
    ict_index = fields.Char(string='ICT Index')
    clearances_blocks_interceptions = fields.Integer(string='Clearances Blocks Interceptions')
    recoveries = fields.Integer(string='Recoveries')
    tackles = fields.Integer(string='Tackles')
    defensive_contribution = fields.Float(string='Defensive Contribution')
    starts = fields.Integer(string='Starts')
    expected_goals = fields.Char(string='Expected Goals')
    expected_assists = fields.Char(string='Expected Assists')
    expected_goal_involvements = fields.Char(string='Expected Goal Involvements')
    expected_goals_conceded = fields.Char(string='Expected Goals Conceded')
    influence_rank = fields.Integer(string='Influence Rank')
    influence_rank_type = fields.Integer(string='Influence Rank Type')
    creativity_rank = fields.Integer(string='Creativity Rank')
    creativity_rank_type = fields.Integer(string='Creativity Rank Type')
    threat_rank = fields.Integer(string='Threat Rank')
    threat_rank_type = fields.Integer(string='Threat Rank Type')
    ict_index_rank = fields.Integer(string='ICT Index Rank')
    ict_index_rank_type = fields.Integer(string='ICT Index Rank Type')
    corners_and_indirect_freekicks_order = fields.Char(string='Corners and Indirect Freekicks Order')
    corners_and_indirect_freekicks_text = fields.Char(string='Corners and Indirect Freekicks Text')
    direct_freekicks_order = fields.Char(string='Direct Freekicks Order')
    direct_freekicks_text = fields.Char(string='Direct Freekicks Text')
    penalties_order = fields.Char(string='Penalties Order')
    penalties_text = fields.Char(string='Penalties Text')
    expected_goals_per_90 = fields.Float(string='Expected Goals Per 90')
    saves_per_90 = fields.Float(string='Saves Per 90')
    expected_assists_per_90 = fields.Float(string='Expected Assists Per 90')
    expected_goal_involvements_per_90 = fields.Float(string='Expected Goal Involvements Per 90')
    expected_goals_conceded_per_90 = fields.Float(string='Expected Goals Conceded Per 90')
    goals_conceded_per_90 = fields.Float(string='Goals Conceded Per 90')
    now_cost_rank = fields.Integer(string='Now Cost Rank')
    now_cost_rank_type = fields.Integer(string='Now Cost Rank Type')
    form_rank = fields.Integer(string='Form Rank')
    form_rank_type = fields.Integer(string='Form Rank Type')
    points_per_game_rank = fields.Integer(string='Points Per Game Rank')
    points_per_game_rank_type = fields.Integer(string='Points Per Game Rank Type')
    selected_rank = fields.Integer(string='Selected Rank')
    selected_rank_type = fields.Integer(string='Selected Rank Type')
    starts_per_90 = fields.Float(string='Starts Per 90')
    clean_sheets_per_90 = fields.Float(string='Clean Sheets Per 90')
    defensive_contribution_per_90 = fields.Float(string='Defensive Contribution Per 90')
    currency_id = fields.Many2one('res.currency', string='Currency')
    display_player_with_photo = fields.Html(compute='_compute_display_player_with_photo', sanitize=False)
    history_ids = fields.One2many('fpl.element.summary.history', 'element_id', string='History IDs')
    history_past_ids = fields.One2many('fpl.element.summary.history.past', 'element_id', string='History Past IDs')
    fixture_ids = fields.One2many(
        'fpl.element.summary.fixture', 'element_id', string='Upcoming Fixtures',
        domain=[('finished', '=', False)],
    )
    summary_name_form = fields.Html(compute='_compute_summary_name_form', sanitize=False)
    summary_synced_at = fields.Datetime(string='Summary Synced At', readonly=True, copy=False)

    @api.depends('first_name', 'second_name', 'web_name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = ' '.join(filter(None, [rec.first_name, rec.second_name])) or rec.web_name or ''

    @api.depends('web_name', 'fpl_team_id.name', 'element_type_id.singular_name_short')
    def _compute_summary_name_form(self):
        for rec in self:
            rec.summary_name_form = Markup(
                '<b>%s</b><br/><span style="color: #af99b1; font-size: 11px">%s %s</span>'
            ) % (rec.web_name or '', rec.fpl_team_id.name or '', rec.element_type_id.singular_name_short or '')

    @api.depends('summary_name_form')
    def _compute_display_player_with_photo(self):
        for rec in self:
            # Served (and HTTP-cached) by /web/image: no file-system lookup per row
            photo_src = f'/web/image/fpl.elements/{rec.id}/photo/80x80' if rec.id else ''
            rec.display_player_with_photo = Markup(
                '<div class="d-flex align-items-center gap-2">'
                '<img src="%s" style="width: 40px; height: 40px; object-fit: contain;"/>'
                '<div>%s</div></div>'
            ) % (photo_src, rec.summary_name_form)

    # ------------------------------------------------------------------
    # Element summary sync (history / past seasons / upcoming fixtures)
    # ------------------------------------------------------------------

    @api.model
    def cron_get_data_element_summary(self, batch_size=SUMMARY_BATCH_SIZE):
        """Refresh the per-player summaries, a batch of players per call.

        The players with the oldest summary go first; ``_notify_progress``
        makes ir.cron call this method again right away (committing between
        calls) until every player is fresh, so a failure only loses the
        current batch and the job never holds one huge transaction.
        """
        stale_domain = [
            ('removed', '=', False),
            '|', ('summary_synced_at', '=', False),
            ('summary_synced_at', '<', fields.Datetime.now() - SUMMARY_MAX_AGE),
        ]
        elements = self.search(stale_domain, order='summary_synced_at asc nulls first, id', limit=batch_size)
        if elements:
            elements._sync_element_summaries()
        remaining = self.search_count(stale_domain)
        self.env['ir.cron']._notify_progress(done=len(elements), remaining=remaining)
        _logger.info("Element summary sync: %s players done, %s remaining", len(elements), remaining)
        return remaining

    def _sync_element_summaries(self):
        """Fetch the summaries of ``self`` concurrently, then store them with a
        single upsert per model.

        Upserting player by player is much slower: every unlink invalidates
        the ORM cache, so the next player re-fetches all the prefetched rows.
        """
        results, errors = self._fpl_fetch_many({
            element.id: ('get_element_summary', (element.element_id,)) for element in self
        })
        for element_id, error in errors.items():
            _logger.warning("Element summary of %s failed: %s", self.browse(element_id).web_name, error)

        synced = self.browse(list(results))
        if synced:
            context = synced._get_summary_sync_context()
            history_vals, past_vals, upcoming_vals = {}, {}, {}
            for element in synced:
                summary = results[element.id] or {}
                history_vals.update(element._prepare_history_vals(summary.get('history') or [], context))
                past_vals.update(element._prepare_history_past_vals(summary.get('history_past') or []))
                upcoming_vals.update(element._prepare_upcoming_fixture_vals(summary.get('fixtures') or [], context))
            self._fpl_upsert('fpl.element.summary.history', context['history'], history_vals)
            self._fpl_upsert('fpl.element.summary.history.past', context['past'], past_vals)
            # The API only lists the fixtures not played yet: the rows of the
            # fixtures played since the last sync are deleted.
            self._fpl_upsert('fpl.element.summary.fixture', context['upcoming'], upcoming_vals, unlink_missing=True)
        # Failed players are retried at the next run, not in a loop
        self.write({'summary_synced_at': fields.Datetime.now()})

    def _get_summary_sync_context(self):
        """Everything the summary sync of ``self`` needs, loaded with a few queries."""
        season = self.env['fpl.events']._get_current_season()

        def existing_rows(model):
            return {
                (rec.element_id.id, rec._get_summary_key()): rec
                for rec in self.env[model].search([('element_id', 'in', self.ids)])
            }

        return {
            'fixtures': self.env['fpl.gameweek.fixtures']._get_fixtures_by_api_id(season),
            'events': self.env['fpl.events']._get_events_by_api_id(season),
            'teams': self.env['fpl.teams']._get_teams_by_api_id(),
            'history': existing_rows('fpl.element.summary.history'),
            'past': existing_rows('fpl.element.summary.history.past'),
            'upcoming': existing_rows('fpl.element.summary.fixture'),
        }

    def _prepare_history_vals(self, history, context):
        """Matches played this season: ``{(element id, fixture id): vals}``"""
        self.ensure_one()
        History = self.env['fpl.element.summary.history']
        no_team = self.env['fpl.teams']
        vals_by_key = {}
        for item in history:
            fixture = context['fixtures'].get(item.get('fixture'))
            if not fixture:
                continue
            vals = self._fpl_filter_vals(History._name, item, exclude={'value', 'kickoff_time', 'opponent_team'})
            vals.update({
                'element_id': self.id,
                'fixture_id': fixture.id,
                'opponent_team': context['teams'].get(item.get('opponent_team'), no_team).id,
                'kickoff_time': self._fpl_parse_datetime(item.get('kickoff_time')),
                'is_modified': bool(item.get('modified')),
                'value': self._fpl_tenths(item.get('value')),
            })
            vals_by_key[(self.id, fixture.id)] = vals
        return vals_by_key

    def _prepare_history_past_vals(self, history_past):
        """Previous seasons: ``{(element id, season name): vals}``"""
        self.ensure_one()
        Past = self.env['fpl.element.summary.history.past']
        vals_by_key = {}
        for past in history_past:
            vals = self._fpl_filter_vals(Past._name, past, exclude={'start_cost', 'end_cost'})
            vals.update({
                'element_id': self.id,
                'start_cost': self._fpl_tenths(past.get('start_cost')),
                'end_cost': self._fpl_tenths(past.get('end_cost')),
            })
            vals_by_key[(self.id, past.get('season_name'))] = vals
        return vals_by_key

    def _prepare_upcoming_fixture_vals(self, fixtures, context):
        """Fixtures not played yet: ``{(element id, fixture id): vals}``"""
        self.ensure_one()
        no_team = self.env['fpl.teams']
        vals_by_key = {}
        for item in fixtures:
            fixture = context['fixtures'].get(item.get('id'))
            if not fixture:
                continue
            event = context['events'].get(item.get('event'))
            vals_by_key[(self.id, fixture.id)] = {
                'element_id': self.id,
                'fixture_id': fixture.id,
                'code': item.get('code'),
                'team_h': context['teams'].get(item.get('team_h'), no_team).id,
                'team_a': context['teams'].get(item.get('team_a'), no_team).id,
                'team_h_score': item.get('team_h_score'),
                'team_a_score': item.get('team_a_score'),
                'event_id': event.id if event else False,
                'event_name': item.get('event_name') or (event.name if event else False),
                'finished': bool(item.get('finished')),
                'minutes': item.get('minutes'),
                'provisional_start_time': bool(item.get('provisional_start_time')),
                'kickoff_time': self._fpl_parse_datetime(item.get('kickoff_time')),
                'is_home': bool(item.get('is_home')),
                'difficulty': item.get('difficulty'),
            }
        return vals_by_key
