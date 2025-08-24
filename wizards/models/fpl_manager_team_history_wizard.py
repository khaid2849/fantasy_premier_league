from odoo import models, fields, api, _

class FplManagerTeamHistoryWizard(models.TransientModel):
    _name = 'fpl.manager.team.history.wizard'
    _description = 'FPL Manager Team Wizard'

    entry_history_ids = fields.Many2many('fpl.entry.history', string=_('Entry History'))
    entry_past_ids = fields.Many2many('fpl.past', string=_('Entry Past'))
