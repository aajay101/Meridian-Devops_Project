import logging
import time

from flask_caching import Cache
from flask_caching.backends.rediscache import RedisCache
from redis.exceptions import RedisError

cache = Cache()
logger = logging.getLogger(__name__)


class SafeRedisCache(RedisCache):
    """RedisCache with circuit-breaker and cooldown-based recovery.

    Behaviour:
      Redis healthy  -> attempt Redis normally.
      Redis fails    -> mark unhealthy, record timestamp, fall back to SQLite.
      Subsequent req -> skip Redis instantly (0 ms), serve from database.
      After cooldown -> ONE lightweight probe.  Succeeds? Resume caching.
                        Fails? Reset cooldown, continue fallback.

    No background threads.  No Celery tasks.  Entirely request-driven.

    Only redis.exceptions.RedisError is caught.  Unrelated programming
    errors (TypeError, ValueError, ...) propagate normally.
    """

    _default_cooldown = 30

    # ── Factory: inject cooldown from app.config ──────────────────────
    @classmethod
    def factory(cls, app, config, args, kwargs):
        instance = super().factory(app, config, args, kwargs)
        instance._cooldown = config.get(
            "REDIS_FAILURE_COOLDOWN", cls._default_cooldown
        )
        return instance

    # ── Constructor ───────────────────────────────────────────────────
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._healthy = True
        self._last_failure_time = 0.0
        self._cooldown = self._default_cooldown  # overridden by factory

    # ── Circuit-breaker core ──────────────────────────────────────────
    def _is_available(self):
        """Return True if a Redis attempt should be made.

        Healthy             -> True  (attempt normally).
        Unhealthy + cooled  -> True  (allow ONE recovery probe).
        Unhealthy + active  -> False (skip instantly).
        """
        if self._healthy:
            return True
        return (time.monotonic() - self._last_failure_time) >= self._cooldown

    def _mark_failed(self):
        """Transition: healthy -> unhealthy.  Logs ONCE per outage."""
        if self._healthy:
            logger.warning("Redis unavailable, falling back to SQLite")
        self._healthy = False
        self._last_failure_time = time.monotonic()

    def _mark_healthy(self):
        """Transition: unhealthy -> healthy.  Logs ONCE on recovery."""
        if not self._healthy:
            logger.info("Redis connection restored")
        self._healthy = True

    # ── Cache operations ──────────────────────────────────────────────
    def get(self, key):
        if not self._is_available():
            return None
        try:
            rv = super().get(key)
            self._mark_healthy()
            return rv
        except RedisError:
            self._mark_failed()
            return None

    def set(self, key, value, timeout=None):
        if not self._is_available():
            return False
        try:
            rv = super().set(key, value, timeout=timeout)
            self._mark_healthy()
            return rv
        except RedisError:
            self._mark_failed()
            return False

    def delete(self, key):
        if not self._is_available():
            return False
        try:
            rv = super().delete(key)
            self._mark_healthy()
            return rv
        except RedisError:
            self._mark_failed()
            return False

    def has(self, key):
        if not self._is_available():
            return False
        try:
            rv = super().has(key)
            self._mark_healthy()
            return rv
        except RedisError:
            self._mark_failed()
            return False

    def delete_many(self, *keys):
        if not self._is_available():
            return []
        try:
            rv = super().delete_many(*keys)
            self._mark_healthy()
            return rv
        except RedisError:
            self._mark_failed()
            return []

    def set_many(self, mapping, timeout=None):
        if not self._is_available():
            return []
        try:
            rv = super().set_many(mapping, timeout=timeout)
            self._mark_healthy()
            return rv
        except RedisError:
            self._mark_failed()
            return []

    def clear(self):
        if not self._is_available():
            return False
        try:
            rv = super().clear()
            self._mark_healthy()
            return rv
        except RedisError:
            self._mark_failed()
            return False


def init_cache(app):
    cache.init_app(app)
    return cache


def _delete_keys(*keys):
    for key in keys:
        try:
            cache.delete(key)
        except Exception:
            logger.warning("Cache invalidation failed for key: %s", key)


def invalidate_admin_dashboard():
    _delete_keys("admin:dashboard")


def invalidate_admin_companies():
    _delete_keys("admin:companies_list", "admin:companies_pending")


def invalidate_admin_drives():
    _delete_keys("admin:drives_list", "admin:drives_pending")


def invalidate_admin_students():
    _delete_keys("admin:students_list")


def invalidate_admin_reports():
    _delete_keys("admin:reports_summary")


def invalidate_student_resume(user_id):
    _delete_keys(
        f"student:{user_id}:profile",
        "admin:students_list",
    )


def _invalidate_company_dashboard_for_drive(drive_id):
    from models import PlacementDrive
    drive = PlacementDrive.query.get(drive_id)
    if drive:
        _delete_keys(f"company:{drive.company_profile_id}:dashboard")


def invalidate_company_profile(company_profile_id):
    from models import Application, PlacementDrive, db

    keys = [f"company:{company_profile_id}:profile"]
    drives = PlacementDrive.query.filter_by(company_profile_id=company_profile_id).all()
    if drives:
        keys.extend(["shared:drives_approved", "admin:drives_list"])
        keys.extend(f"shared:drive:{drive.id}" for drive in drives)
        for drive in drives:
            keys.extend(_company_applicant_cache_keys(drive.id))

        applications = (
            db.session.query(Application)
            .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
            .filter(PlacementDrive.company_profile_id == company_profile_id)
            .all()
        )
        for user_id in {application.student_profile.user_id for application in applications}:
            keys.extend([
                f"student:{user_id}:applications",
                f"student:{user_id}:applications_history",
            ])
        if applications:
            keys.append("admin:applications_list")
    _delete_keys(*keys)


def invalidate_company_drive(company_profile_id, drive_id):
    _delete_keys(
        f"company:{company_profile_id}:drives",
        f"company:{company_profile_id}:drive:{drive_id}",
        f"company:{company_profile_id}:dashboard",
    )


def _company_applicant_cache_keys(drive_id):
    """Return both legacy and ownership-scoped applicant cache keys."""
    from models import PlacementDrive

    drive = PlacementDrive.query.get(drive_id)
    keys = [
        f"company:drive:{drive_id}:applicants",
        f"company:drive:{drive_id}:count",
    ]
    if drive:
        keys.extend([
            f"company:{drive.company_profile_id}:drive:{drive_id}:applicants",
            f"company:{drive.company_profile_id}:drive:{drive_id}:count",
        ])
    return keys


def _student_application_cache_keys_for_drive(drive_id):
    from models import Application

    user_ids = {
        application.student_profile.user_id
        for application in Application.query.filter_by(drive_id=drive_id).all()
    }
    keys = []
    for user_id in user_ids:
        keys.extend([
            f"student:{user_id}:applications",
            f"student:{user_id}:applications_history",
        ])
    return keys


def invalidate_company_applicants(drive_id):
    # Applicant endpoints include the owning company in their cache keys.
    # Resolve it from the drive so status/application mutations cannot leave
    # a stale response visible to the owning company.
    _delete_keys(*_company_applicant_cache_keys(drive_id))


def invalidate_drive_status(company_profile_id, drive_id, include_shared=True):
    keys = [
        "admin:drives_list",
        "admin:drives_pending",
        f"company:{company_profile_id}:drives",
        f"company:{company_profile_id}:drive:{drive_id}",
        f"company:{company_profile_id}:dashboard",
    ]
    if include_shared:
        keys.extend(["shared:drives_approved", f"shared:drive:{drive_id}"])
    keys.extend(_student_application_cache_keys_for_drive(drive_id))
    _delete_keys(*keys)


def invalidate_drive_created(company_profile_id):
    _delete_keys(
        f"company:{company_profile_id}:drives",
        f"company:{company_profile_id}:dashboard",
        "admin:drives_list",
        "admin:drives_pending",
        "admin:dashboard",
        "admin:reports_summary",
    )


def invalidate_drive_deleted(company_profile_id, drive_id):
    _delete_keys(
        f"company:{company_profile_id}:drives",
        f"company:{company_profile_id}:drive:{drive_id}",
        f"company:{company_profile_id}:dashboard",
        "admin:drives_list",
        "admin:drives_pending",
        "admin:dashboard",
        "admin:reports_summary",
    )


def invalidate_application_created(student_user_id, drive_id):
    keys = [
        f"student:{student_user_id}:dashboard",
        f"student:{student_user_id}:applications",
        "admin:applications_list",
        "admin:reports_summary",
    ]
    keys.extend(_company_applicant_cache_keys(drive_id))
    _delete_keys(*keys)
    _invalidate_company_dashboard_for_drive(drive_id)


def invalidate_application_status(student_user_id, drive_id, include_history=False):
    keys = [
        f"student:{student_user_id}:dashboard",
        f"student:{student_user_id}:applications",
    ]
    if include_history:
        keys.append(f"student:{student_user_id}:applications_history")
    keys.extend(_company_applicant_cache_keys(drive_id))
    keys.extend([
        "admin:applications_list",
        "admin:reports_summary",
    ])
    _delete_keys(*keys)


def invalidate_student_profile_data(student_user_id, application_drive_ids=()):
    keys = [
        f"student:{student_user_id}:dashboard",
        f"student:{student_user_id}:profile",
        "admin:students_list",
        "admin:applications_list",
    ]
    for drive_id in dict.fromkeys(application_drive_ids):
        keys.extend(_company_applicant_cache_keys(drive_id))
    _delete_keys(*keys)


def invalidate_offer_status(student_user_id, drive_ids=()):
    keys = [
        f"student:{student_user_id}:dashboard",
        f"student:{student_user_id}:applications",
        f"student:{student_user_id}:applications_history",
        "admin:applications_list",
        "admin:reports_summary",
    ]
    for drive_id in dict.fromkeys(drive_ids):
        keys.extend(_company_applicant_cache_keys(drive_id))
    _delete_keys(*keys)
