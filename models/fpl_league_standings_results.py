from odoo import models, fields, api, _

class FplLeagueStandingsResults(models.Model):
    _name = 'fpl.league.standings.results'

    league_id = fields.Many2one('fpl.leagues', string=_('League'))
    result_id = fields.Integer(string=_('ID'))
    event_total = fields.Integer(string=_('Event total'))
    player_name = fields.Char(string=_('Player name'))
    rank = fields.Integer(string=_('Rank'))
    last_rank = fields.Integer(string=_('Last rank'))
    rank_sort = fields.Integer(string=_('Rank sort'))
    total = fields.Integer(string=_('141'))
    entry = fields.Integer(string=_('Entry'))
    entry_name = fields.Char(string=_('Entry Name'))
    has_played = fields.Boolean(string=_('Has played'))
    phase_id = fields.Many2one('fpl.phases', string=_('Phase'))
    rank_form = fields.Html(string=_('Rank'), compute='_compute_rank_form')
    name = fields.Html(string=_('Team & Manager'), compute='_compute_team_and_manager')

    @api.depends('entry_name', 'player_name')
    def _compute_team_and_manager(self):
        for rec in self:
            rec.name = f'<strong>{rec.entry_name}</strong><br/><span>{rec.player_name}</span>'

    @api.depends('last_rank', 'rank')
    def _compute_rank_form(self):
        for rec in self:
            if rec.rank > rec.last_rank:
                rec.rank_form = f'<p><i class="fa fa-arrow-circle-down" style="color: #E60023"></i> {format(rec.rank, ",")}</p>'
            elif rec.rank < rec.last_rank:
                rec.rank_form = f'<p><i class="fa fa-arrow-circle-up" style="color: #34a853"></i> {format(rec.rank, ",")}</p>'
            elif rec.rank == rec.last_rank:
                rec.rank_form = f'<p><i class="fa fa-circle" style="color: #87668a"></i> {format(rec.rank, ",")}</p>'
