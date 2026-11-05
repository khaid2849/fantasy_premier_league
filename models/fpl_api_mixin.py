import logging
from datetime import date, datetime, timezone

from odoo import _, api, models
from odoo.exceptions import UserError

from ..services.fpl_api_client import FPLApiClient, fetch_many
from ..services.fpl_pulse_api_client import FPLPulseLiveApiClient

_logger = logging.getLogger(__name__)

# Field types that cannot be compared cheaply through the cache format
_NON_COMPARABLE_TYPES = {'one2many', 'many2many', 'binary', 'image', 'html', 'properties', 'json'}


class FPLApiMixin(models.AbstractModel):
    """Shared helpers for every model that talks to the FPL APIs."""
    _name = 'fpl.api.mixin'
    _description = 'FPL API Mixin'

    # ------------------------------------------------------------------
    # API access
    # ------------------------------------------------------------------

    @api.model
    def _fpl_client(self, access_token=None):
        return FPLApiClient(x_api_authorization=f'Bearer {access_token}' if access_token else None)

    @api.model
    def sync_from_fpl_api(self, endpoint_method, *args, **kwargs):
        """Call a public endpoint of :class:`FPLApiClient` by method name."""
        return self._fpl_call(self._fpl_client(), endpoint_method, *args, **kwargs)

    @api.model
    def sync_authenticated_data(self, endpoint_method, access_token, *args, **kwargs):
        """Call a private endpoint of :class:`FPLApiClient` with an OIDC access token."""
        return self._fpl_call(self._fpl_client(access_token), endpoint_method, *args, **kwargs)

    @api.model
    def sync_from_pulse_live_api(self, endpoint_method, *args, **kwargs):
        """Call a method of :class:`FPLPulseLiveApiClient` by name."""
        return self._fpl_call(FPLPulseLiveApiClient(), endpoint_method, *args, **kwargs)

    @api.model
    def _fpl_call(self, client, endpoint_method, *args, **kwargs):
        method = getattr(client, endpoint_method, None)
        if method is None:
            raise ValueError(f"Unknown API method: {endpoint_method}")
        return method(*args, **kwargs)

    @api.model
    def _fpl_fetch_many(self, calls, access_token=None, max_workers=8):
        """Fetch several FPL endpoints concurrently (network I/O only).

        :param dict calls: ``{key: (endpoint_method, args_tuple)}``
        :return: ``(results, errors)`` dicts keyed like ``calls``
        """
        client = self._fpl_client(access_token)
        jobs = {
            key: (lambda method=method, args=args: self._fpl_call(client, method, *args))
            for key, (method, args) in calls.items()
        }
        return fetch_many(jobs, max_workers=max_workers)

    @api.model
    def _fpl_user_error(self, message, error):
        """Translate an API exception into a UserError."""
        if isinstance(error, UserError):
            return error
        return UserError(_("%(message)s: %(error)s", message=message, error=error))

    # ------------------------------------------------------------------
    # Value parsing
    # ------------------------------------------------------------------

    @api.model
    def _fpl_parse_datetime(self, value):
        """ISO-8601 string from the API (e.g. '2026-08-15T11:00:00Z') -> naive UTC datetime."""
        if not value:
            return False
        if isinstance(value, datetime):
            dt = value
        else:
            try:
                dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
            except ValueError:
                _logger.warning("Unparsable FPL datetime %r", value)
                return False
        if dt.tzinfo:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt

    @api.model
    def _fpl_parse_date(self, value):
        if not value:
            return False
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            _logger.warning("Unparsable FPL date %r", value)
            return False

    @api.model
    def _fpl_tenths(self, value):
        """FPL prices/banks are expressed in tenths of a million (e.g. 55 -> 5.5)."""
        return (value or 0) / 10.0

    # ------------------------------------------------------------------
    # Upsert helpers
    # ------------------------------------------------------------------

    @api.model
    def _fpl_changed_vals(self, record, vals):
        """Subset of ``vals`` that differs from what ``record`` already holds.

        Writing unchanged values is not free: it issues UPDATEs, bumps
        write_date, triggers recomputations and tracking. The sync jobs
        re-send the same data most of the time, so diffing first avoids most
        of the database work.
        """
        changed = {}
        for fname, value in vals.items():
            field = record._fields[fname]
            if field.type in _NON_COMPARABLE_TYPES:
                changed[fname] = value
                continue
            try:
                new = field.convert_to_cache(value, record, validate=False)
                old = field.convert_to_cache(record[fname], record, validate=False)
            except (ValueError, TypeError):
                changed[fname] = value
                continue
            if new != old:
                changed[fname] = value
        return changed

    @api.model
    def _fpl_upsert(self, model, existing, vals_by_key, unlink_missing=False):
        """Create/update records from API values in batch.

        :param str|BaseModel model: target model
        :param dict existing: ``{key: record}`` already in database
        :param dict vals_by_key: ``{key: vals}`` wanted state
        :param bool unlink_missing: delete the existing records whose key is
            not in ``vals_by_key``
        :return: ``{key: record}`` for every key of ``vals_by_key``
        """
        Model = self.env[model] if isinstance(model, str) else model
        result = {}
        create_keys, create_vals = [], []
        for key, vals in vals_by_key.items():
            record = existing.get(key)
            if record:
                changed = self._fpl_changed_vals(record, vals)
                if changed:
                    record.write(changed)
                result[key] = record
            else:
                create_keys.append(key)
                create_vals.append(vals)
        if create_vals:
            result.update(zip(create_keys, Model.create(create_vals)))
        if unlink_missing:
            obsolete_ids = [rec.id for key, rec in existing.items() if key not in vals_by_key]
            if obsolete_ids:
                Model.browse(obsolete_ids).unlink()
        return result

    @api.model
    def _fpl_filter_vals(self, model, data, exclude=()):
        """Keep only the keys of an API dict that are real fields of ``model``.

        The FPL API regularly adds new keys between seasons; passing them
        blindly to create()/write() would make the whole sync crash.
        """
        fields_map = self.env[model]._fields
        return {
            key: value for key, value in data.items()
            if key in fields_map and key not in exclude and key not in models.MAGIC_COLUMNS
            and not fields_map[key].compute
        }
