from odoo import models, fields, api

class FplLeagueStandingsResults(models.Model):
    _name = 'fpl.league.standings.results'
    _description = 'FPL League Standings Results'

    league_id = fields.Many2one('fpl.leagues', string='League')
    result_id = fields.Integer(string='ID')
    event_total = fields.Integer(string='Event total')
    player_name = fields.Char(string='Player name')
    rank = fields.Integer(string='Rank')
    last_rank = fields.Integer(string='Last rank')
    rank_sort = fields.Integer(string='Rank sort')
    total = fields.Integer(string='141')
    entry = fields.Integer(string='Entry')
    entry_name = fields.Char(string='Entry Name')
    has_played = fields.Boolean(string='Has played')
    phase_id = fields.Many2one('fpl.phases', string='Phase')
    rank_form = fields.Html(string='Rank', compute='_compute_rank_form')
    club_badge_src = fields.Char(string='Club Badge Src')
    name = fields.Html(string='Team & Manager', compute='_compute_team_and_manager')

    @api.depends('entry_name', 'player_name')
    def _compute_team_and_manager(self):
        for rec in self:
            if rec.club_badge_src:
                club_badge_src = rec.club_badge_src
            else:
                club_badge_src = '/fantasy_premier_league/static/src/img/blank_image.png'
            rec.name = f'<div class="d-flex align-items-center"><div><img src={club_badge_src} style="width: 30px; height: 30px;"/></div><div><strong>&nbsp;{rec.entry_name}</strong><br/><span>&nbsp;{rec.player_name}</span></div></div>'

    @api.depends('last_rank', 'rank')
    def _compute_rank_form(self):
        for rec in self:
            if rec.rank > rec.last_rank:
                rec.rank_form = f'<p><i class="fa fa-arrow-circle-down" style="color: #E60023"></i> {format(rec.rank, ",")}</p>'
            elif rec.rank < rec.last_rank:
                rec.rank_form = f'<p><i class="fa fa-arrow-circle-up" style="color: #34a853"></i> {format(rec.rank, ",")}</p>'
            elif rec.rank == rec.last_rank:
                rec.rank_form = f'<p><i class="fa fa-circle" style="color: #87668a"></i> {format(rec.rank, ",")}</p>'
