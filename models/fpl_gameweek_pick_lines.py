from odoo import _, api, fields, models


class FplGameweekPickLines(models.Model):
    _name = 'fpl.gameweek.pick.lines'
    _inherit = ['fpl.api.mixin']
    _description = 'FPL Gameweek Pick Lines'
    _order = 'gameweek_pick_id, position'

    gameweek_pick_id = fields.Many2one('fpl.gameweek.picks', string='Gameweek Pick', required=True, index=True,
                                       ondelete='cascade')
    element_id = fields.Many2one('fpl.elements', string='Player', index=True)
    position = fields.Integer(string='Position')
    multiplier = fields.Integer(string='Multiplier')
    is_captain = fields.Boolean(string='Is Captain')
    is_vice_captain = fields.Boolean(string='Is Vice Captain')
    element_type_id = fields.Many2one('fpl.element.types', string='Element Type')
    # Snapshot of the club at the time of the gameweek (players may move later on)
    team_id = fields.Many2one('fpl.teams', string='Team')
    team_code = fields.Char()
    team_name = fields.Char()
    web_name = fields.Char()
    raw_points = fields.Integer(string='Points', help="Points scored by the player, before the captain multiplier.")
    total_points = fields.Integer(string='Total points', help="Points counted for the manager (captain multiplier "
                                                              "applied; raw points for the bench).")
    plural_name_short = fields.Char(related='element_type_id.plural_name_short')
    element_stats_ids = fields.One2many('fpl.element.stats', 'pick_line_id', string='Stats')
    gw_fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Gameweek Fixture')

    # Fixture header of the player stats popup
    team_h = fields.Many2one(related='gw_fixture_id.team_h', string='Home team')
    team_a = fields.Many2one(related='gw_fixture_id.team_a', string='Away team')
    team_h_photo = fields.Image(related='gw_fixture_id.team_h.photo')
    team_a_photo = fields.Image(related='gw_fixture_id.team_a.photo')
    team_h_score = fields.Integer(related='gw_fixture_id.team_h_score')
    team_a_score = fields.Integer(related='gw_fixture_id.team_a_score')
    kickoff_time = fields.Datetime(related='gw_fixture_id.kickoff_time')
    started = fields.Boolean(related='gw_fixture_id.started')
    finished = fields.Boolean(related='gw_fixture_id.finished')

    _sql_constraints = [
        ('pick_element_uniq', 'unique(gameweek_pick_id, element_id)', 'A player can only be picked once.'),
    ]

    @api.model
    def _sync_pick_lines(self, gameweek_pick, picks, live_elements, event):
        """Replace the lines of ``gameweek_pick`` with ``picks`` and their
        points breakdown taken from the gameweek live data."""
        elements = {
            element.element_id: element
            for element in self.env['fpl.elements'].search([
                ('element_id', 'in', [pick.get('element') for pick in picks]),
            ])
        }
        element_types = self.env['fpl.element.types']._get_types_by_api_id()
        fixtures = self.env['fpl.gameweek.fixtures']._get_fixtures_by_api_id(event.season)
        existing = {line.element_id.id: line for line in gameweek_pick.pick_lines}

        vals_by_key, explains = {}, {}
        for pick in picks:
            element = elements.get(pick.get('element'))
            if not element:
                continue
            live = live_elements.get(pick.get('element')) or {}
            explain = live.get('explain') or []
            raw_points = (live.get('stats') or {}).get('total_points') or 0
            multiplier = pick.get('multiplier') or 0
            first_fixture = fixtures.get(explain[0].get('fixture')) if explain else None
            element_type = element_types.get(str(pick.get('element_type')))
            vals_by_key[element.id] = {
                'gameweek_pick_id': gameweek_pick.id,
                'element_id': element.id,
                'element_type_id': element_type.id if element_type else element.element_type_id.id,
                'team_id': element.fpl_team_id.id,
                'team_code': element.fpl_team_id.code,
                'team_name': element.fpl_team_id.name,
                'web_name': element.web_name,
                'position': pick.get('position'),
                'multiplier': multiplier,
                'is_captain': bool(pick.get('is_captain')),
                'is_vice_captain': bool(pick.get('is_vice_captain')),
                'raw_points': raw_points,
                'total_points': raw_points * multiplier if multiplier else raw_points,
                'gw_fixture_id': first_fixture.id if first_fixture else False,
            }
            explains[element.id] = explain

        lines = self._fpl_upsert(self, existing, vals_by_key, unlink_missing=True)
        self.env['fpl.element.stats']._sync_points_breakdown(
            {lines[key]: explains[key] for key in lines}, fixtures,
        )

    @api.model
    def action_open_player_stats(self, pick_line_id):
        """Points breakdown popup of a player of the pitch view."""
        line = self.browse(int(pick_line_id)).exists()
        if not line:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': _("Player Stats"),
            'res_model': self._name,
            'res_id': line.id,
            'view_mode': 'form',
            'views': [(self.env.ref('fantasy_premier_league.fpl_gameweek_pick_lines_stats_form_view').id, 'form')],
            'target': 'new',
        }
