# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Fantasy Premier League',
    'version': '1.1',
    'category': 'Fantasy Premier League',
    'sequence': 30,
    'summary': 'Manage Fantasy Premier League',
    'description': """
        Fantasy Premier League (FPL) is a free-to-play game where you win points based on the real-life performances of players in the Premier League.
        ================================================
        This module allows you to manage your FPL team and track your performance.
        It also allows you to import your FPL team from the FPL website.
    """,
    'website': 'https://www.fantasypremierleague.com/',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',

        'data/ir_cron.xml',

        'views/fpl_manager_team_view.xml',
        'views/fpl_teams_view.xml',
        'views/fpl_elements_view.xml',
        'views/fpl_gameweek_fixtures_view.xml',
        'views/fpl_leagues_view.xml',
        'views/menu.xml',

        'wizards/views/fpl_manager_team_wizard_view.xml',
        'wizards/views/fpl_manager_team_history_wizard_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'icon': '/fantasy_premier_league/static/description/icon.png',
    'assets': {
        'web.assets_backend': [
            '/fantasy_premier_league/static/src/js/*.js',
            '/fantasy_premier_league/static/src/xml/*.xml',
        ]
    },
}
