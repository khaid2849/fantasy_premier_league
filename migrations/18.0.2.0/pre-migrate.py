"""Clean the data that would violate the constraints added in 2.0."""
import logging

_logger = logging.getLogger(__name__)


def _table_exists(cr, table):
    cr.execute("SELECT 1 FROM information_schema.tables WHERE table_name = %s", [table])
    return bool(cr.fetchone())


def _dedupe(cr, table, columns, order='id DESC'):
    """Keep one row (the first one in ``order``) of every group of duplicates."""
    if not _table_exists(cr, table):
        return
    cols = ', '.join(columns)
    cr.execute(f"""
        DELETE FROM {table} t
         USING (SELECT id, ROW_NUMBER() OVER (PARTITION BY {cols} ORDER BY {order}) AS rn FROM {table}) d
         WHERE t.id = d.id AND d.rn > 1
    """)
    if cr.rowcount:
        _logger.info("fantasy_premier_league: removed %s duplicated rows from %s", cr.rowcount, table)


def _delete_orphans(cr, table, column):
    if not _table_exists(cr, table):
        return
    cr.execute(f"DELETE FROM {table} WHERE {column} IS NULL")
    if cr.rowcount:
        _logger.info("fantasy_premier_league: removed %s orphan rows from %s", cr.rowcount, table)


def _drop_selection_values(cr, fields_by_model):
    """Fields converted from Selection to Char: their ir.model.fields.selection
    rows must go, otherwise Odoo tries to apply the selection ``ondelete`` of
    a field that is no longer a Selection at the end of the upgrade."""
    for model, field_names in fields_by_model.items():
        cr.execute("""
            SELECT s.id FROM ir_model_fields_selection s
              JOIN ir_model_fields f ON f.id = s.field_id
             WHERE f.model = %s AND f.name IN %s
        """, [model, tuple(field_names)])
        selection_ids = [row[0] for row in cr.fetchall()]
        if selection_ids:
            cr.execute("DELETE FROM ir_model_data WHERE model = 'ir.model.fields.selection' AND res_id IN %s",
                       [tuple(selection_ids)])
            cr.execute("DELETE FROM ir_model_fields_selection WHERE id IN %s", [tuple(selection_ids)])


def migrate(cr, version):
    if not version:
        return

    _drop_selection_values(cr, {
        'fpl.element.stats': ['identifier'],
        'fpl.chips': ['show_name'],
        'fpl.manager.chips': ['show_name'],
    })

    # Parents first: the 1.2 foreign keys are ON DELETE SET NULL, so removing
    # a duplicated parent leaves orphans that are cleaned just after.
    _dedupe(cr, 'fpl_manager_team', ['manager_id'], order='(refresh_token IS NOT NULL) DESC, id DESC')
    _dedupe(cr, 'fpl_leagues', ['manager_id', 'type', 'league_id'])
    _delete_orphans(cr, 'fpl_leagues', 'manager_id')
    _delete_orphans(cr, 'fpl_league_active_phases', 'league_id')

    # League standings were never matched with the existing rows (the lookup
    # used the active phase id instead of the phase id) and grew at each sync.
    _delete_orphans(cr, 'fpl_league_standings_results', 'league_id')
    _dedupe(cr, 'fpl_league_standings_results', ['league_id', 'phase_id', 'result_id'])

    for table in ('fpl_element_summary_history', 'fpl_element_summary_history_past', 'fpl_element_summary_fixture'):
        _delete_orphans(cr, table, 'element_id')
    _dedupe(cr, 'fpl_element_summary_history', ['element_id', 'fixture_id'])
    _dedupe(cr, 'fpl_element_summary_history_past', ['element_id', 'season_name'])
    _dedupe(cr, 'fpl_element_summary_fixture', ['element_id', 'fixture_id'])

    for table in ('fpl_entry_history', 'fpl_past', 'fpl_manager_chips', 'fpl_picks'):
        _delete_orphans(cr, table, 'manager_id')

    # Gameweek picks are a cache of the FPL API, re-fetched on demand. The old
    # rows stored bank/value/transfer cost truncated or divided by 10.
    for table in ('fpl_element_stats', 'fpl_gameweek_pick_lines', 'fpl_gameweek_picks'):
        if _table_exists(cr, table):
            cr.execute(f"DELETE FROM {table}")

    # fpl.picks.position: char -> integer
    if _table_exists(cr, 'fpl_picks'):
        cr.execute(r"UPDATE fpl_picks SET position = NULL WHERE position !~ '^\d+$'")
