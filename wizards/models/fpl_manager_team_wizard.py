from odoo import models, fields, api, _

class FPLManagerTeamWizard(models.TransientModel):
    _name = 'fpl.manager.team.wizard'
    _description = 'FPL Manager Team Wizard'

    manager_id = fields.Char(string=_('Manager ID'))
    cookies = fields.Char(string=_('Cookies'))
    token = fields.Char(string=_('Token'))
    tooltip = fields.Text(string=_('Tooltip'), compute='_compute_tooltip')

    def _compute_tooltip(self):
        for record in self:
            tooltip = f'How to get your manager_id?\n\n'
            tooltip += f'1. Log in to https://fantasy.premierleague.com/\n'
            tooltip += f'2. Access your team: Navigate to either the "Pick Team" or "Points" section.\n'
            tooltip += f"3. Check the URL: Look at the address bar of your browser. You'll see a URL similar to this: https://fantasy.premierleague.com/entry/1234567/event/1. The number after /entry/ and before /event/ (in this case, 1234567) is your FPL ID, according to several FPL resources. \n"

            tooltip += f'How to get your cookies and token?\n\n'
            tooltip += f'1. Open the developer tools (Ctrl+Shift+I or F12)\n'
            tooltip += f'2. Go to the Network tab\n'
            tooltip += f'3. Find the request to https://fantasy.premierleague.com/api/me/\n'
            tooltip += f'4. Copy the Cookies and X-api-authorization from the request headers\n'
            record.tooltip = tooltip

    def action_verify_manager_team(self):
        pass
