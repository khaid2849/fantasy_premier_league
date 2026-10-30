import logging

from odoo import models, fields, api
from odoo.exceptions import UserError
from .fpl_api_mixin import FPLApiMixin
from ..services.fpl_api_client import FPLApiException
from datetime import datetime

_logger = logging.getLogger(__name__)

class FplGameweekPicks(models.Model, FPLApiMixin):
    _name = 'fpl.gameweek.picks'
    _description = 'FPL Gameweek Picks'
    
    manager_id = fields.Many2one('fpl.manager.team', string='Manager')
    event_id = fields.Many2one('fpl.events', string='Event')
    points = fields.Integer(string='Points')
    total_points = fields.Integer(string='Total Points')
    rank = fields.Integer(string='Rank')
    rank_sort = fields.Integer(string='Rank Sort')
    overall_rank = fields.Integer(string='Overall Rank')
    percentile_rank = fields.Integer(string='Percentile Rank')
    bank = fields.Integer(string='Bank')
    value = fields.Integer(string='Value')
    event_transfers = fields.Integer(string='Event Transfers')
    event_transfers_cost = fields.Integer(string='Event Transfers Cost')
    points_on_bench = fields.Integer(string='Points on Bench')
    pick_lines = fields.One2many('fpl.gameweek.pick.lines', 'gameweek_pick_id', string='Pick Lines')