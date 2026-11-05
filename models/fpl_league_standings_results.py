from markupsafe import Markup

from odoo import api, fields, models

from .fpl_leagues import rank_form_html

BLANK_BADGE_SRC = '/fantasy_premier_league/static/src/img/blank_image.png'


class FplLeagueStandingsResults(models.Model):
    _name = 'fpl.league.standings.results'
    _description = 'FPL League Standings Results'
    _order = 'rank, id'

    league_id = fields.Many2one('fpl.leagues', string='League', required=True, index=True, ondelete='cascade')
    phase_id = fields.Many2one('fpl.phases', string='Phase', index=True, ondelete='cascade')
    result_id = fields.Integer(string='ID')
    event_total = fields.Integer(string='Event total')
    player_name = fields.Char(string='Player name')
    rank = fields.Integer(string='Rank')
    last_rank = fields.Integer(string='Last rank')
    rank_sort = fields.Integer(string='Rank sort')
    total = fields.Integer(string='Total')
    entry = fields.Integer(string='Entry')
    entry_name = fields.Char(string='Entry Name')
    has_played = fields.Boolean(string='Has played')
    rank_form = fields.Html(string='Rank', compute='_compute_rank_form', sanitize=False)
    club_badge_src = fields.Char(string='Club Badge Src')
    name = fields.Html(string='Team & Manager', compute='_compute_team_and_manager', sanitize=False)

    _sql_constraints = [
        ('league_phase_entry_uniq', 'unique(league_id, phase_id, result_id)',
         'An entry can only appear once per league standing.'),
    ]

    @api.depends('entry_name', 'player_name', 'club_badge_src')
    def _compute_team_and_manager(self):
        for rec in self:
            # Team and manager names are typed by FPL players: always escaped
            rec.name = Markup(
                '<div class="d-flex align-items-center"><div><img src="%s" style="width: 30px; height: 30px;"/>'
                '</div><div><strong>&nbsp;%s</strong><br/><span>&nbsp;%s</span></div></div>'
            ) % (rec.club_badge_src or BLANK_BADGE_SRC, rec.entry_name or '', rec.player_name or '')

    @api.depends('last_rank', 'rank')
    def _compute_rank_form(self):
        for rec in self:
            rec.rank_form = rank_form_html(rec.rank, rec.last_rank)
