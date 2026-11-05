import base64
import hashlib
import io
import logging
from datetime import timedelta

from PIL import Image

from odoo import _, api, fields, models

from ..services.fpl_api_client import FPLApiException, fetch_many, http_get_bytes
from .master_data import REGIONS

try:
    import cairosvg
except (ImportError, OSError):  # OSError: cairo system library missing
    cairosvg = None

_logger = logging.getLogger(__name__)

REGION_ISO_BY_ID = {region['id']: region['iso_code_short'] for region in REGIONS}

PLAYER_PHOTO_URL = 'https://resources.premierleague.com/premierleague25/photos/players/110x140/{code}.png'
TEAM_BADGE_URL = 'https://resources.premierleague.com/premierleague25/badges/{code}.svg'
TEAM_SHIRT_URL = 'https://fantasy.premierleague.com/dist/img/shirts/standard/{name}'
# fpl.teams field -> file name on the FPL CDN (the 110px kits used by the pitch view)
SHIRT_VARIANTS = {
    'shirt_image': 'shirt_{code}-110.webp',
    'shirt_gkp_image': 'shirt_{code}_1-110.webp',
}
# Size of the PNG rendered from the SVG club badges
LOGO_SIZE = 256
# An image that does not exist on the CDN (404) is asked again after that delay
IMAGE_RETRY_DELAY = timedelta(days=7)
IMAGE_CRON_XMLID = 'fantasy_premier_league.ir_cron_download_fpl_images'

# API keys that are not copied as-is into fpl.elements
_ELEMENT_SPECIAL_KEYS = {
    'id', 'code', 'team', 'team_code', 'element_type', 'now_cost', 'photo', 'status',
    'team_join_date', 'birth_date', 'region',
}


class FplImportData(models.AbstractModel):
    """Bootstrap-static sync (reference data) and image downloads."""
    _name = 'fpl.import.data'
    _inherit = ['fpl.api.mixin']
    _description = 'FPL Import Data'

    # ------------------------------------------------------------------
    # Bootstrap static
    # ------------------------------------------------------------------

    @api.model
    def cron_get_data_boostrap_static(self):
        try:
            data = self.sync_from_fpl_api('get_bootstrap_static')
        except FPLApiException as e:
            raise self._fpl_user_error(_("Failed to fetch the FPL bootstrap data"), e) from e

        _logger.info("Starting bootstrap static data sync")
        self._sync_chips_data(data.get('chips') or [])
        self._sync_events_data(data.get('events') or [])
        self._sync_phases_data(data.get('phases') or [])
        self._sync_teams_data(data.get('teams') or [])
        self._sync_element_types_data(data.get('element_types') or [])
        self._sync_elements_data(data.get('elements') or [])
        _logger.info("Bootstrap static data sync completed successfully")
        return True

    def _sync_chips_data(self, chips_data):
        Chips = self.env['fpl.chips']
        existing = {chip.chip_id: chip for chip in Chips.search([])}
        vals_by_key = {
            str(chip['id']): {
                'chip_id': str(chip['id']),
                'name': chip.get('name'),
                'number': chip.get('number'),
                'start_event': chip.get('start_event'),
                'stop_event': chip.get('stop_event'),
                'chip_type': chip.get('chip_type'),
            }
            for chip in chips_data
        }
        self._fpl_upsert(Chips, existing, vals_by_key)
        _logger.info("Synced %s chips", len(vals_by_key))

    def _sync_events_data(self, events_data):
        Events = self.env['fpl.events']
        existing = {(event.event_id, event.season): event for event in Events.search([])}
        vals_by_key = {}
        chip_plays_by_key = {}
        for event in events_data:
            deadline_time = self._fpl_parse_datetime(event.get('deadline_time'))
            # The FPL API re-uses event ids 1-38 every season: match on (id, season)
            key = (event['id'], Events._season_from_date(deadline_time))
            vals = self._fpl_filter_vals(Events._name, event, exclude={'id', 'deadline_time', 'release_time'})
            vals.update({
                'event_id': event['id'],
                'deadline_time': deadline_time,
                'release_time': self._fpl_parse_datetime(event.get('release_time')),
            })
            vals_by_key[key] = vals
            chip_plays_by_key[key] = event.get('chip_plays') or []

        events = self._fpl_upsert(Events, existing, vals_by_key)

        # Events of past seasons are not returned anymore: they must not stay
        # flagged as the current/next gameweek forever.
        stale = Events.browse([
            rec.id for key, rec in existing.items()
            if key not in vals_by_key and (rec.is_current or rec.is_next or rec.is_previous)
        ])
        if stale:
            stale.write({'is_current': False, 'is_next': False, 'is_previous': False})

        self._sync_event_chip_plays(events, chip_plays_by_key)
        _logger.info("Synced %s events", len(vals_by_key))

    def _sync_event_chip_plays(self, events, chip_plays_by_key):
        ChipPlays = self.env['fpl.event.chip.plays']
        event_ids = [event.id for event in events.values()]
        existing = {
            (play.event_id.id, play.chip_name): play
            for play in ChipPlays.search([('event_id', 'in', event_ids)])
        }
        vals_by_key = {}
        for key, chip_plays in chip_plays_by_key.items():
            event = events[key]
            for chip_play in chip_plays:
                vals_by_key[(event.id, chip_play.get('chip_name'))] = {
                    'event_id': event.id,
                    'chip_name': chip_play.get('chip_name'),
                    'num_played': chip_play.get('num_played') or 0,
                }
        self._fpl_upsert(ChipPlays, existing, vals_by_key, unlink_missing=True)

    def _sync_phases_data(self, phases_data):
        Phases = self.env['fpl.phases']
        existing = {phase.phase_id: phase for phase in Phases.search([])}
        vals_by_key = {
            phase['id']: {
                'phase_id': phase['id'],
                'name': phase.get('name'),
                'start_event': phase.get('start_event'),
                'stop_event': phase.get('stop_event'),
                'highest_score': phase.get('highest_score'),
            }
            for phase in phases_data
        }
        self._fpl_upsert(Phases, existing, vals_by_key)
        _logger.info("Synced %s phases", len(vals_by_key))

    def _sync_teams_data(self, teams_data):
        Teams = self.env['fpl.teams'].with_context(active_test=False)
        existing = Teams._get_teams_by_code()
        vals_by_key = {}
        for team in teams_data:
            vals = self._fpl_filter_vals(Teams._name, team, exclude={'id', 'code', 'photo'})
            vals.update({'team_id': team['id'], 'code': str(team['code']), 'active': True})
            vals_by_key[str(team['code'])] = vals

        teams = self._fpl_upsert(Teams, existing, vals_by_key)

        # Relegated clubs: archived, and their (re-assigned) team id freed so
        # that API ids always resolve to a club of the current season.
        relegated = Teams.browse([rec.id for code, rec in existing.items() if code not in vals_by_key])
        if relegated:
            relegated.write({'active': False, 'team_id': 0})

        if set(vals_by_key) - set(existing):
            self._trigger_image_download()
        _logger.info("Synced %s teams", len(teams))

    def _sync_element_types_data(self, element_types_data):
        Types = self.env['fpl.element.types']
        existing = Types._get_types_by_api_id()
        vals_by_key = {}
        for element_type in element_types_data:
            vals = self._fpl_filter_vals(Types._name, element_type, exclude={'id'})
            vals['element_type_id'] = str(element_type['id'])
            vals_by_key[str(element_type['id'])] = vals
        self._fpl_upsert(Types, existing, vals_by_key)
        _logger.info("Synced %s element types", len(vals_by_key))

    def _sync_elements_data(self, elements_data):
        Elements = self.env['fpl.elements'].with_context(active_test=False)
        existing = {element.code: element for element in Elements.search([('code', '!=', False)])}
        teams = self.env['fpl.teams']._get_teams_by_api_id()
        element_types = self.env['fpl.element.types']._get_types_by_api_id()
        countries = {
            country.code: country.id
            for country in self.env['res.country'].search([('code', 'in', list(REGION_ISO_BY_ID.values()))])
        }
        statuses = dict(Elements._fields['status'].selection)

        vals_by_key = {}
        for element in elements_data:
            code = str(element['code'])
            team = teams.get(element.get('team'))
            element_type = element_types.get(str(element.get('element_type')))
            status = element.get('status')
            vals = self._fpl_filter_vals(Elements._name, element, exclude=_ELEMENT_SPECIAL_KEYS)
            vals.update({
                'active': True,
                'element_id': element['id'],
                'code': code,
                'fpl_team_id': team.id if team else False,
                'element_type_id': element_type.id if element_type else False,
                'now_cost': self._fpl_tenths(element.get('now_cost')),
                'status': status if status in statuses else False,
                'team_join_date': self._fpl_parse_date(element.get('team_join_date')),
                'birth_date': self._fpl_parse_date(element.get('birth_date')),
                'region': element.get('region'),
                'country_id': countries.get(REGION_ISO_BY_ID.get(element.get('region')), False),
            })
            vals_by_key[code] = vals

        elements = self._fpl_upsert(Elements, existing, vals_by_key)

        # Players gone from the API, and duplicated records of a same player
        departed = Elements.search([('active', '=', True), ('id', 'not in', [rec.id for rec in elements.values()])])
        if departed:
            # Element ids are re-assigned every season: free them so that API
            # ids always resolve to a player of the current season.
            departed.write({'active': False, 'element_id': 0})

        if set(vals_by_key) - set(existing):
            self._trigger_image_download()
        _logger.info("Synced %s elements (%s archived)", len(elements), len(departed))

    # ------------------------------------------------------------------
    # Images (club badges, kits, player photos), stored in database
    # ------------------------------------------------------------------

    @api.model
    def _trigger_image_download(self):
        """New clubs/players (e.g. a new season): fetch their images right away."""
        cron = self.env.ref(IMAGE_CRON_XMLID, raise_if_not_found=False)
        if cron:
            cron.sudo()._trigger()

    @api.model
    def cron_download_images(self, force=False):
        """Download the club badges, kits and player photos that are missing.

        Images are stored on the records (attachments), so this works on any
        instance, including one whose module source is read-only. An image
        that does not exist on the CDN is asked again after
        ``IMAGE_RETRY_DELAY`` only.

        :param bool force: download every image again (only the ones that
            changed are written)
        """
        teams = self.env['fpl.teams'].search([('code', '!=', False)])
        players = self.env['fpl.elements'].search([('code', '!=', False)])
        logos = self._download_team_logos(teams, force)
        shirts = self._download_team_shirts(teams, force)
        photos = self._download_player_photos(players, force)
        _logger.info("FPL images: %s badges, %s kits and %s player photos updated", logos, shirts, photos)
        return logos + shirts + photos

    @api.model
    def _image_candidates(self, records, is_missing, checked_field, force):
        """Records whose image is missing and was not looked for recently."""
        if force:
            return records
        retry_before = fields.Datetime.now() - IMAGE_RETRY_DELAY
        return records.filtered(
            lambda rec: is_missing(rec) and (not rec[checked_field] or rec[checked_field] < retry_before)
        )

    @api.model
    def _fetch_images(self, urls):
        """Download ``{key: url}`` concurrently.

        :return: ``{key: content}`` for the requests that got an answer;
            ``content`` is None when the image does not exist (404). Network
            errors are left out, so that they are retried at the next run.
        """
        results, errors = fetch_many({key: (lambda url=url: http_get_bytes(url)) for key, url in urls.items()})
        for key, error in errors.items():
            _logger.warning("Download of %s failed: %s", urls[key], error)
        return results

    @api.model
    def _stored_checksums(self, records, field_name):
        """``{record id: checksum}`` of a binary field, read from its attachments."""
        if not records:
            return {}
        self.env.cr.execute("""
            SELECT res_id, checksum FROM ir_attachment
             WHERE res_model = %s AND res_field = %s AND res_id = ANY(%s)
        """, [records._name, field_name, records.ids])
        return dict(self.env.cr.fetchall())

    @api.model
    def _download_team_logos(self, teams, force=False):
        """Club badges: SVG on the CDN, rendered as PNG in ``fpl.teams.photo``.

        The CDN keys badges by the club ``code``, not ``team_id``
        (badges/43.svg = Man City, whose team_id is 15). The
        "badges-alt" variant is meant for dark backgrounds (white crests).
        """
        teams = self._image_candidates(teams, lambda team: not team.photo_checksum, 'logo_checked_at', force)
        if not teams:
            return 0
        if cairosvg is None:
            _logger.warning("cairosvg is not installed (pip install cairosvg): club badges cannot be downloaded")
            return 0
        results = self._fetch_images({team.id: TEAM_BADGE_URL.format(code=team.code) for team in teams})
        updated = 0
        for team in teams.filtered(lambda team: team.id in results):
            svg = results[team.id]
            checksum = svg and hashlib.sha1(svg).hexdigest()
            vals = {'logo_checked_at': fields.Datetime.now()}
            if svg and checksum != team.photo_checksum:
                try:
                    png = self._normalize_logo_png(cairosvg.svg2png(bytestring=svg, output_width=LOGO_SIZE))
                except Exception as e:  # noqa: BLE001 - a broken badge must not stop the others
                    _logger.warning("Cannot render the badge of %s: %s", team.name, e)
                else:
                    vals.update(photo=base64.b64encode(png), photo_checksum=checksum)
                    updated += 1
            team.write(vals)
        return updated

    @api.model
    def _download_team_shirts(self, teams, force=False):
        """Outfield and goalkeeper kits, shown on the pitch view."""
        teams = self._image_candidates(
            teams, lambda team: not (team.shirt_image and team.shirt_gkp_image), 'shirts_checked_at', force,
        )
        if not teams:
            return 0
        results = self._fetch_images({
            (team.id, field_name): TEAM_SHIRT_URL.format(name=remote_name.format(code=team.code))
            for team in teams
            for field_name, remote_name in SHIRT_VARIANTS.items()
        })
        stored = {field_name: self._stored_checksums(teams, field_name) for field_name in SHIRT_VARIANTS}
        updated = 0
        for team in teams:
            vals = {}
            for field_name in SHIRT_VARIANTS:
                key = (team.id, field_name)
                if key not in results:
                    continue
                vals['shirts_checked_at'] = fields.Datetime.now()
                content = results[key]
                if content and hashlib.sha1(content).hexdigest() != stored[field_name].get(team.id):
                    vals[field_name] = base64.b64encode(content)
                    updated += 1
            if vals:
                team.write(vals)
        return updated

    @api.model
    def _download_player_photos(self, players, force=False):
        players = self._image_candidates(players, lambda player: not player.photo_checksum, 'images_checked_at', force)
        if not players:
            return 0
        results = self._fetch_images({player.id: PLAYER_PHOTO_URL.format(code=player.code) for player in players})
        updated = 0
        for player in players.filtered(lambda player: player.id in results):
            content = results[player.id]
            checksum = content and hashlib.sha1(content).hexdigest()
            vals = {'images_checked_at': fields.Datetime.now()}
            if content and checksum != player.photo_checksum:
                vals.update(photo=base64.b64encode(content), photo_checksum=checksum)
                updated += 1
            player.write(vals)
        return updated

    @api.model
    def _normalize_logo_png(self, png_bytes, size=LOGO_SIZE):
        """Square transparent canvas, the badge centered with its aspect ratio kept."""
        img = Image.open(io.BytesIO(png_bytes)).convert('RGBA')
        img.thumbnail((size, size), Image.LANCZOS)
        canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
        output = io.BytesIO()
        canvas.save(output, format='PNG', optimize=True)
        return output.getvalue()
