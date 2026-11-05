import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """2.3: pick lines know the automatic substitutions. The picks of a
    finished gameweek are never synced again, so drop them: they are fetched
    again from the FPL API the next time they are displayed."""
    cr.execute("DELETE FROM fpl_gameweek_picks")
    _logger.info("Dropped %s gameweek picks, re-fetched on display", cr.rowcount)
