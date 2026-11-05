from odoo import fields, models

FIXTURE_STAT_IDENTIFIERS = [
    ('goals_scored', 'Goals Scored'),
    ('assists', 'Assists'),
    ('own_goals', 'Own Goals'),
    ('penalties_saved', 'Penalties Saved'),
    ('penalties_missed', 'Penalties Missed'),
    ('yellow_cards', 'Yellow Cards'),
    ('red_cards', 'Red Cards'),
    ('saves', 'Saves'),
    ('bonus', 'Bonus'),
    ('bps', 'Bonus Points System'),
    ('defensive_contribution', 'Defensive Contribution'),
]
FIXTURE_STAT_KEYS = {key for key, _label in FIXTURE_STAT_IDENTIFIERS}
SIDES = [('h', 'Home'), ('a', 'Away')]


class FplFixtureStat(models.Model):
    """One player statistic of a fixture (goals, assists, cards, bonus...).

    Replaces the 22 identical ``fpl.team.{a,h}.<stat>`` models: a single
    table keyed by (fixture, side, identifier, player) lets the live sync
    read and diff the stats of a whole gameweek with one query.
    """
    _name = 'fpl.fixture.stat'
    _description = 'FPL Fixture Player Stat'
    _order = 'fixture_id, side desc, identifier, value desc, id'

    fixture_id = fields.Many2one('fpl.gameweek.fixtures', string='Fixture', required=True,
                                 index=True, ondelete='cascade')
    side = fields.Selection(SIDES, string='Side', required=True)
    identifier = fields.Selection(FIXTURE_STAT_IDENTIFIERS, string='Statistic', required=True)
    element_id = fields.Many2one('fpl.elements', string='Player', index=True, ondelete='cascade')
    value = fields.Integer(string='Value')
    web_name = fields.Char(related='element_id.web_name', string='Player Name')

    _sql_constraints = [
        ('fixture_stat_uniq', 'unique(fixture_id, side, identifier, element_id)',
         'A player can only have one value per statistic and fixture.'),
    ]
