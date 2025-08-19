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
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',

        'views/fpl_manager_team_view.xml',
        'views/menu.xml',
        
        'wizards/views/fpl_manager_team_wizard_view.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'assets': {},
}
