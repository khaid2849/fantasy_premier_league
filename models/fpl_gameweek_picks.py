import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .fpl_api_mixin import FPLApiMixin
from ..services.fpl_api_client import FPLApiException
from datetime import datetime

_logger = logging.getLogger(__name__)

class FplGameweekPicks(models.Model, FPLApiMixin):
    _name = 'fpl.gameweek.picks'
    _description = 'FPL Gameweek Picks'
    
    manager_id = fields.Many2one('fpl.manager.team', string=_('Manager'))
    event_id = fields.Many2one('fpl.events', string=_('Event'))
    points = fields.Integer(string=_('Points'))
    total_points = fields.Integer(string=_('Total Points'))
    rank = fields.Integer(string=_('Rank'))
    rank_sort = fields.Integer(string=_('Rank Sort'))
    overall_rank = fields.Integer(string=_('Overall Rank'))
    percentile_rank = fields.Integer(string=_('Percentile Rank'))
    bank = fields.Integer(string=_('Bank'))
    value = fields.Integer(string=_('Value'))
    event_transfers = fields.Integer(string=_('Event Transfers'))
    event_transfers_cost = fields.Integer(string=_('Event Transfers Cost'))
    points_on_bench = fields.Integer(string=_('Points on Bench'))
    pick_lines = fields.One2many('fpl.gameweek.pick.lines', 'gameweek_pick_id', string=_('Pick Lines'))