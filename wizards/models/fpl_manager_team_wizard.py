from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FplManagerTeamWizard(models.TransientModel):
    _name = 'fpl.manager.team.wizard'
    _description = 'FPL Manager Team Wizard'

    manager_id = fields.Char(string=_('Manager ID'))
    refresh_token = fields.Char(string=_('FPL Refresh Token'))
    tooltip = fields.Html(string=_('Tooltip'), default=lambda self: self._get_default_tooltip())

    def _get_default_tooltip(self):
        tooltip = """<p><strong>How to get your Manager ID (Optional)?</strong><br/>
<em>Note: Manager ID will be automatically extracted from the API if not provided.</em><br/>
1. Log in to <a href="https://fantasy.premierleague.com/" target="_blank">https://fantasy.premierleague.com/</a><br/>
2. Access your team: Navigate to either the "Pick Team" or "Points" section.<br/>
3. Check the URL: Look at the address bar of your browser.<br/>
You'll see a URL similar to this: https://fantasy.premierleague.com/entry/1234567/event/1.<br/>
The number after /entry/ and before /event/ (in this case, 1234567) is your FPL ID, according to several FPL resources.<br/><br/>

<strong>How to get your FPL Refresh Token (only needed once)?</strong><br/>
1. Log in to https://fantasy.premierleague.com/ and open the developer tools (F12)<br/>
2. Go to the Console tab and run:<br/>
<code>copy(JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>k.startsWith('oidc.user:')))).refresh_token)</code><br/>
3. Paste the copied value here. Odoo refreshes the token automatically afterwards.</p>"""
        return tooltip

    def action_verify_manager_team(self):
        """Verify and sync manager team data using FPL API"""
        try:
            # Sync data from FPL API - this will create/update the record automatically
            if not self.refresh_token and not self.manager_id:
                raise UserError(_("Please provide a Manager ID or an FPL Refresh Token"))
            # Without a refresh token, only public data is synced (or the stored token is used)
            manager_team = self.env['fpl.manager.team'].sync_manager_data(
                refresh_token=self.refresh_token,
                manager_id=self.manager_id,  # Optional fallback if API doesn't provide manager_id
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Manager team data has been successfully synced from FPL API for Manager ID: %s') % manager_team.manager_id,
                    'type': 'success',
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }
            
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Failed to sync data: %s') % str(e),
                    'type': 'danger',
                }
            }
