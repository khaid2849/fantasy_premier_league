from odoo import _, fields, models
from odoo.exceptions import UserError


class FplManagerTeamWizard(models.TransientModel):
    _name = 'fpl.manager.team.wizard'
    _description = 'FPL Manager Team Wizard'

    manager_id = fields.Char(string='Manager ID')
    refresh_token = fields.Char(string='FPL Refresh Token')

    def action_verify_manager_team(self):
        """Create/update the manager from the FPL API.

        Without a refresh token only the public data is synced (or the token
        already stored on the manager is used). Errors are raised, so that a
        failed sync is rolled back instead of half-saved.
        """
        self.ensure_one()
        if not self.refresh_token and not self.manager_id:
            raise UserError(_("Please provide a Manager ID or an FPL Refresh Token"))
        manager_team = self.env['fpl.manager.team'].sync_manager_data(
            refresh_token=self.refresh_token,
            manager_id=(self.manager_id or '').strip() or None,
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Manager team data has been successfully synced from FPL API for Manager ID: %s',
                             manager_team.manager_id),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
