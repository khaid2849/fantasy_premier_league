from odoo import fields, models


class FplManagerTeamHistoryWizard(models.TransientModel):
    _name = 'fpl.manager.team.history.wizard'
    _description = 'FPL Manager Team History Wizard'

    entry_history_ids = fields.Many2many('fpl.entry.history', string='Entry History')
    entry_past_ids = fields.Many2many('fpl.past', string='Entry Past')
