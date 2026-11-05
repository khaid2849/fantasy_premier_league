from collections import defaultdict

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
    auto_sub = fields.Selection([('in', 'Substituted in'), ('out', 'Substituted out')],
                                string='Automatic substitution',
                                help="FPL automatic substitution: the API already swaps the positions of the players.")

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
    def _sync_pick_lines(self, gameweek_pick, picks, live_elements, event, automatic_subs=()):
        """Replace the lines of ``gameweek_pick`` with ``picks`` and their
        points breakdown taken from the gameweek live data.

        :param automatic_subs: API ``automatic_subs`` list
            (``[{'element_in': id, 'element_out': id, ...}]``)
        """
        subs_in = {sub.get('element_in') for sub in automatic_subs or ()}
        subs_out = {sub.get('element_out') for sub in automatic_subs or ()}
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
                'auto_sub': ('in' if pick.get('element') in subs_in
                             else 'out' if pick.get('element') in subs_out else False),
            }
            explains[element.id] = explain

        lines = self._fpl_upsert(self, existing, vals_by_key, unlink_missing=True)
        self.env['fpl.element.stats']._sync_points_breakdown(
            {lines[key]: explains[key] for key in lines}, fixtures,
        )

    # ------------------------------------------------------------------
    # Pitch view
    # ------------------------------------------------------------------

    def _get_pitch_player(self, team_fixtures, statuses):
        """One player of the pitch view.

        :param list team_fixtures: fixtures of the player's team in the
            gameweek (none on a blank gameweek, two on a double one)
        :param dict statuses: labels of the ``fpl.elements`` statuses
        """
        self.ensure_one()
        element = self.element_id
        team = self.team_id
        position = self.element_type_id.plural_name_short or element.element_type_id.plural_name_short or ''

        stats_by_fixture = defaultdict(list)
        for stat in self.element_stats_ids:
            stats_by_fixture[stat.fixture_id].append({
                'id': stat.id,
                'label': stat.name,
                'value': stat.value,
                'points': stat.points,
            })
        fixtures = list(team_fixtures)
        # Breakdown of a fixture not found by team (player moved club since)
        fixtures += [fixture for fixture in stats_by_fixture if fixture and fixture not in fixtures]

        # Char field, False when FPL gives no estimate (int(False) would be 0)
        chance = element.chance_of_playing_this_round
        chance = int(chance) if chance and str(chance).isdigit() else None
        status = element.status or 'a'
        return {
            'id': self.id,
            'name': self.web_name or element.web_name or '',
            'full_name': element.display_name or '',
            'team_id': team.id,
            'team_name': self.team_name or team.name or '',
            'position': position,
            'position_name': self.element_type_id.singular_name or position,
            'shirt_url': f"/web/image/fpl.teams/{team.id}/{'shirt_gkp_image' if position == 'GKP' else 'shirt_image'}",
            'multiplier': self.multiplier,
            'is_captain': self.is_captain,
            'is_vice_captain': self.is_vice_captain,
            'raw_points': self.raw_points,
            'points': self.total_points,
            'bench_order': max(self.position - 11, 0),
            'auto_sub': self.auto_sub or False,
            'status': status,
            'status_label': statuses.get(status, ''),
            'chance': chance,
            'news': element.news or '',
            'news_added': element.news_added or False,
            'fixtures': [
                self._get_pitch_fixture(fixture, team, stats_by_fixture.get(fixture, []))
                for fixture in fixtures
            ],
        }

    @api.model
    def _get_pitch_fixture(self, fixture, team, stats):
        is_home = fixture.team_h == team
        opponent = fixture.team_a if is_home else fixture.team_h
        finished = fixture.finished or fixture.finished_provisional
        return {
            'id': fixture.id,
            'is_home': is_home,
            'opponent': opponent.short_name or opponent.name or '',
            'home_name': fixture.team_h.name or '',
            'away_name': fixture.team_a.name or '',
            'home_score': fixture.team_h_score,
            'away_score': fixture.team_a_score,
            'started': fixture.started,
            'finished': finished,
            'live': fixture.started and not finished,
            'minutes': fixture.minutes,
            'kickoff_time': fields.Datetime.to_string(fixture.kickoff_time) if fixture.kickoff_time else False,
            'stats': stats,
        }

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
