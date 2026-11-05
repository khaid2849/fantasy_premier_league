"""2.1: images are stored in database instead of the module's static folders."""
import hashlib
import logging

from odoo import SUPERUSER_ID, api
from odoo.tools.misc import file_open

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Players without a real photo used to get the blank placeholder image:
    # remove it, so that the image cron downloads their photo (the views show
    # Odoo's own placeholder meanwhile).
    with file_open('fantasy_premier_league/static/src/img/blank_image.png', 'rb') as blank_file:
        blank_checksum = hashlib.sha1(blank_file.read()).hexdigest()
    cr.execute("""
        SELECT res_id FROM ir_attachment
         WHERE res_model = 'fpl.elements' AND res_field = 'photo' AND checksum = %s
    """, [blank_checksum])
    blank_ids = [row[0] for row in cr.fetchall()]
    if blank_ids:
        env['fpl.elements'].with_context(active_test=False).browse(blank_ids).write({
            'photo': False, 'photo_checksum': False,
        })
        _logger.info("fantasy_premier_league: removed %s placeholder player photos", len(blank_ids))

    # Club badges are now rendered from the SVG in a higher resolution: fetch
    # them again (the current badge is kept until the new one is stored).
    cr.execute("UPDATE fpl_teams SET photo_checksum = NULL")

    # Kits and missing photos are downloaded right after the upgrade
    env.ref('fantasy_premier_league.ir_cron_download_fpl_images')._trigger()
