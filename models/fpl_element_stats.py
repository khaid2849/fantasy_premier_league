from odoo import api, fields, models

from .master_data import MAPPING_SELECTIONS_DATA

STAT_LABELS = dict(MAPPING_SELECTIONS_DATA['element_stats'])


class FplElementStats(models.Model):
    """One line of the points breakdown of a picked player ('explain' in the API)."""
    _name = 'fpl.element.stats'
    _description = 'FPL Element Stats'
    _order = 'pick_line_id, fixture_id, id'

    # Char, not Selection: FPL adds new scoring rules (e.g. defensive
    # contribution in 2025/26); an unknown identifier must not break the sync.
    identifier = fields.Char(string='Identifier')
    name = fields.Char(string='Statistic', compute='_compute_name')
    points = fields.Integer(string='Points')
    value = fields.Integer(string='Value')
    points_modification = fields.Integer(string='Points modification')
    pick_line_id = fields.Many2one('fpl.gameweek.pick.lines', string='Pick', required=True, index=True,
                                   ondelete='cascade')
    fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Fixture')

    @api.depends('identifier')
    def _compute_name(self):
        for stat in self:
            stat.name = STAT_LABELS.get(stat.identifier) or (stat.identifier or '').replace('_', ' ').capitalize()

    @api.model
    def _sync_points_breakdown(self, explains_by_line, fixtures):
        """Replace the breakdown lines of several pick lines at once.

        :param dict explains_by_line: ``{pick line: API 'explain' list}``; a
            double gameweek has one entry per fixture
        :param dict fixtures: ``{FPL fixture id: fixture record}``
        """
        line_ids = [line.id for line in explains_by_line]
        existing = {
            (stat.pick_line_id.id, stat.fixture_id.id, stat.identifier): stat
            for stat in self.search([('pick_line_id', 'in', line_ids)])
        }
        vals_by_key = {}
        for line, explains in explains_by_line.items():
            for explain in explains:
                fixture = fixtures.get(explain.get('fixture'))
                fixture_id = fixture.id if fixture else False
                for stat in explain.get('stats') or []:
                    vals_by_key[(line.id, fixture_id, stat.get('identifier'))] = {
                        'pick_line_id': line.id,
                        'fixture_id': fixture_id,
                        'identifier': stat.get('identifier'),
                        'points': stat.get('points') or 0,
                        'value': stat.get('value') or 0,
                        'points_modification': stat.get('points_modification') or 0,
                    }
        self.env['fpl.api.mixin']._fpl_upsert(self, existing, vals_by_key, unlink_missing=True)
