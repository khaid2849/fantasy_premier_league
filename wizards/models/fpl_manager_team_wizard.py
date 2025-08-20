from odoo import models, fields, api, _

class FPLManagerTeamWizard(models.TransientModel):
    _name = 'fpl.manager.team.wizard'
    _description = 'FPL Manager Team Wizard'

    manager_id = fields.Char(string=_('Manager ID'))
    cookies = fields.Char(string=_('Cookies'))
    x_api_authorization = fields.Char(string=_('X-api-authorization'))
    tooltip = fields.Html(string=_('Tooltip'), default=lambda self: self._get_default_tooltip())

    def _get_default_tooltip(self):
        tooltip = """<p><strong>How to get your Manager ID (Optional)?</strong><br/>
<em>Note: Manager ID will be automatically extracted from the API if not provided.</em><br/>
1. Log in to <a href="https://fantasy.premierleague.com/" target="_blank">https://fantasy.premierleague.com/</a><br/>
2. Access your team: Navigate to either the "Pick Team" or "Points" section.<br/>
3. Check the URL: Look at the address bar of your browser.<br/>
You'll see a URL similar to this: https://fantasy.premierleague.com/entry/1234567/event/1.<br/>
The number after /entry/ and before /event/ (in this case, 1234567) is your FPL ID, according to several FPL resources.<br/><br/>

<strong>How to get your Cookies and X-api-authorization (Required)?</strong><br/>
1. Open the developer tools (Ctrl+Shift+I or F12)<br/>
2. Go to the Network tab<br/>
3. Find the request to https://fantasy.premierleague.com/api/me/<br/>
4. Copy the Cookies and X-api-authorization value from the request headers</p>"""
        return tooltip

    def action_verify_manager_team(self):
        """Verify and sync manager team data using FPL API"""
        try:
            # Sync data from FPL API - this will create/update the record automatically
            manager_team = self.env['fpl.manager.team'].sync_manager_data(
                self.cookies, 
                self.x_api_authorization, 
                self.manager_id  # Optional fallback if API doesn't provide manager_id
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Manager team data has been successfully synced from FPL API for Manager ID: %s') % manager_team.manager_id,
                    'type': 'success',
                }
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
