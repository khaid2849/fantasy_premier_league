from odoo import api, fields, models


class FPLTeams(models.Model):
    _name = 'fpl.teams'
    _description = 'FPL Teams'
    _order = 'name'

    active = fields.Boolean(default=True,
                            help="Clubs that are no longer in the Premier League are archived by the bootstrap sync.")
    name = fields.Char(string='Name')
    # The club 'code' is stable across seasons, while 'team_id' (1..20) is
    # re-assigned every season in alphabetical order.
    code = fields.Char(string='Code', index=True)
    form = fields.Char(string='Form')
    team_id = fields.Integer(string='Team ID', index=True)
    loss = fields.Integer(string='Loss')
    played = fields.Integer(string='Played')
    points = fields.Integer(string='Points')
    position = fields.Integer(string='Position')
    short_name = fields.Char(string='Short Name')
    strength = fields.Integer(string='Strength')
    team_division = fields.Char(string='Team Division')
    unavailable = fields.Boolean(string='Unavailable')
    win = fields.Integer(string='Win')
    draw = fields.Integer(string='Draw')
    strength_overall_home = fields.Integer(string='Strength Overall Home')
    strength_overall_away = fields.Integer(string='Strength Overall Away')
    strength_attack_home = fields.Integer(string='Strength Attack Home')
    strength_attack_away = fields.Integer(string='Strength Attack Away')
    strength_defence_home = fields.Integer(string='Strength Defence Home')
    strength_defence_away = fields.Integer(string='Strength Defence Away')
    pulse_id = fields.Integer(string='Pulse ID')
    element_ids = fields.One2many('fpl.elements', 'fpl_team_id', string='Elements')
    # Images downloaded from the FPL CDN by the "Download FPL Images" cron
    photo = fields.Image(string='Photo')
    photo_checksum = fields.Char(string='Photo Source Checksum', readonly=True, copy=False)
    shirt_image = fields.Binary(string='Shirt', attachment=True)
    shirt_gkp_image = fields.Binary(string='Goalkeeper Shirt', attachment=True)
    # Last download attempts (an image missing on the CDN is retried later)
    logo_checked_at = fields.Datetime(string='Badge Checked At', readonly=True, copy=False)
    shirts_checked_at = fields.Datetime(string='Shirts Checked At', readonly=True, copy=False)

    def _logo_url(self):
        """URL of the club badge (cached by the browser until the badge changes)."""
        self.ensure_one()
        return f'/web/image/fpl.teams/{self.id}/photo?unique={self.photo_checksum or ""}'

    @api.model
    def _get_teams_by_api_id(self):
        """``{FPL team id: record}`` of the clubs of the current season."""
        return {team.team_id: team for team in self.search([('team_id', '!=', 0)])}

    @api.model
    def _get_teams_by_code(self):
        return {team.code: team for team in self.with_context(active_test=False).search([('code', '!=', False)])}
