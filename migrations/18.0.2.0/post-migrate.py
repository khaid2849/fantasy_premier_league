"""Move the data of the models replaced in 2.0."""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# old table suffix -> fpl.fixture.stat identifier
OLD_STAT_TABLES = {
    'goals_scored': 'goals_scored',
    'assists': 'assists',
    'own_goals': 'own_goals',
    'penalties_saved': 'penalties_saved',
    'penalties_missed_scored': 'penalties_missed',
    'yellow_cards': 'yellow_cards',
    'red_cards': 'red_cards',
    'goals_saved': 'saves',
    'bonus': 'bonus',
    'bps': 'bps',
    'defensive_contribution': 'defensive_contribution',
}


def _table_exists(cr, table):
    cr.execute("SELECT 1 FROM information_schema.tables WHERE table_name = %s", [table])
    return bool(cr.fetchone())


def migrate(cr, version):
    if not version:
        return

    # The 22 fpl.team.{a,h}.<stat> models were merged into fpl.fixture.stat.
    # Their tables are dropped by Odoo at the end of the upgrade.
    moved = 0
    for side in ('a', 'h'):
        for suffix, identifier in OLD_STAT_TABLES.items():
            table = f'fpl_team_{side}_{suffix}'
            if not _table_exists(cr, table):
                continue
            cr.execute(f"""
                INSERT INTO fpl_fixture_stat (fixture_id, side, identifier, element_id, value,
                                              create_uid, create_date, write_uid, write_date)
                SELECT gw_fixture_id, %s, %s, element_id, MAX(value),
                       MIN(create_uid), MIN(create_date), MAX(write_uid), MAX(write_date)
                  FROM {table}
                 WHERE gw_fixture_id IS NOT NULL AND element_id IS NOT NULL
                 GROUP BY gw_fixture_id, element_id
                ON CONFLICT DO NOTHING
            """, [side, identifier])
            moved += cr.rowcount
    _logger.info("fantasy_premier_league: moved %s fixture stats to fpl.fixture.stat", moved)

    # 1.2 looked events up by id only (ignoring the season): re-derive the
    # season of every fixture from its kick-off time (Aug-May season, same
    # rule as fpl.events._season_from_date) and link the matching event.
    cr.execute("""
        UPDATE fpl_gameweek_fixtures f
           SET season = CASE WHEN EXTRACT(MONTH FROM f.kickoff_time) >= 7
                             THEN EXTRACT(YEAR FROM f.kickoff_time)::int || '/' || (EXTRACT(YEAR FROM f.kickoff_time)::int + 1)
                             ELSE (EXTRACT(YEAR FROM f.kickoff_time)::int - 1) || '/' || EXTRACT(YEAR FROM f.kickoff_time)::int
                        END
         WHERE f.kickoff_time IS NOT NULL
    """)
    cr.execute("""
        UPDATE fpl_gameweek_fixtures f
           SET event_id = e.id
          FROM fpl_events e
         WHERE e.event_id = f.gameweek AND e.season = f.season AND f.event_id IS DISTINCT FROM e.id
    """)
    if cr.rowcount:
        _logger.info("fantasy_premier_league: %s fixtures re-linked to the event of their season", cr.rowcount)

    env = api.Environment(cr, SUPERUSER_ID, {})

    # The fixtures no longer store a copy of the team badges (related fields now)
    attachments = env['ir.attachment'].search([
        ('res_model', '=', 'fpl.gameweek.fixtures'),
        ('res_field', 'in', ['team_a_photo', 'team_h_photo']),
    ])
    _logger.info("fantasy_premier_league: removing %s duplicated team badge attachments", len(attachments))
    attachments.unlink()

    # Odoo removes the metadata of deleted models but leaves their tables
    # behind (it only drops tables of models still in the registry):
    # - the 22 stat models (data copied above)
    # - the player stats wizard (replaced by a form view on the pick line)
    # - fpl.import.data, an AbstractModel now (it never stored anything)
    obsolete_tables = [
        f'fpl_team_{side}_{suffix}' for side in ('a', 'h') for suffix in OLD_STAT_TABLES
    ] + [
        'fpl_element_stats_fpl_gameweek_pick_lines_wizard_rel',
        'fpl_gameweek_pick_lines_wizard',
        'fpl_import_data',
    ]
    for table in obsolete_tables:
        if _table_exists(cr, table):
            cr.execute(f'DROP TABLE "{table}" CASCADE')

    # Photos are only re-written when their source file changes: seed the
    # source checksum with the stored one
    for table, model in (('fpl_elements', 'fpl.elements'), ('fpl_teams', 'fpl.teams')):
        cr.execute(f"""
            UPDATE {table} rec SET photo_checksum = att.checksum
              FROM ir_attachment att
             WHERE att.res_model = %s AND att.res_field = 'photo' AND att.res_id = rec.id
        """, [model])

    # Live notifications now go to the "FPL Live" channel instead of a
    # private chat per user (the channel itself comes from data.xml)
    env['fpl.gameweek.fixtures']._init_live_channel_members()

    # Refresh every player summary at the next cron run (value/costs used to
    # be truncated to integers)
    cr.execute("UPDATE fpl_elements SET summary_synced_at = NULL")
