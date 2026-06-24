from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from datetime import datetime, time, timedelta, timezone
from typing import Any

from config.game import DEFAULTS
from core.error import DailyResetSessionExpiredError
from core.i18n import t

DOTNET_UNIX_EPOCH_TICKS = 621355968000000000
TICKS_PER_SECOND = 10_000_000


def stamp_session_daily_reset(
    session: MutableMapping[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    moment = _session_created_at(session) or _utc_now(now)
    metadata = {
        "region": DEFAULTS.daily_reset_region,
        "created_at_utc": _format_utc(moment),
        "daily_reset_utc": _reset_time_label(),
        "daily_reset_local": _local_reset_time_label(),
        "daily_reset_day": daily_reset_day_key(moment),
    }
    session[DEFAULTS.session_lifecycle_key] = metadata
    return metadata


def validate_session_daily_reset(
    session: Mapping[str, Any],
    *,
    now: datetime | None = None,
) -> None:
    if not DEFAULTS.session_daily_reset_guard_enabled:
        return
    created_at = _session_created_at(session)
    if created_at is None:
        return
    created_day = _session_daily_reset_day(session) or daily_reset_day_key(created_at)
    current_day = daily_reset_day_key(_utc_now(now))
    if created_day >= current_day:
        return
    raise DailyResetSessionExpiredError(t(
        "session.daily_reset_expired",
        session_day=created_day,
        current_day=current_day,
        reset_utc=_reset_time_label(),
        local_reset=_local_reset_time_label(),
    ))


def daily_reset_day_key(moment: datetime) -> str:
    moment = _as_utc(moment)
    reset_at = datetime.combine(
        moment.date(),
        time(DEFAULTS.daily_reset_utc_hour, DEFAULTS.daily_reset_utc_minute, tzinfo=timezone.utc),
    )
    if moment < reset_at:
        return (moment.date() - timedelta(days=1)).isoformat()
    return moment.date().isoformat()


def _session_daily_reset_day(session: Mapping[str, Any]) -> str | None:
    lifecycle = session.get(DEFAULTS.session_lifecycle_key)
    if isinstance(lifecycle, Mapping):
        value = lifecycle.get("daily_reset_day")
        if isinstance(value, str) and value:
            return value
    return None


def _session_created_at(session: Mapping[str, Any]) -> datetime | None:
    lifecycle = session.get(DEFAULTS.session_lifecycle_key)
    if isinstance(lifecycle, Mapping):
        parsed = _parse_datetime(lifecycle.get("created_at_utc"))
        if parsed is not None:
            return parsed
    parsed = _parse_datetime(session.get("created_at_utc"))
    if parsed is not None:
        return parsed
    return _datetime_from_dotnet_ticks(session.get("server_time_ticks"))


def _datetime_from_dotnet_ticks(value: Any) -> datetime | None:
    try:
        ticks = int(value)
    except (TypeError, ValueError):
        return None
    if ticks < DOTNET_UNIX_EPOCH_TICKS:
        return None
    seconds = (ticks - DOTNET_UNIX_EPOCH_TICKS) / TICKS_PER_SECOND
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OSError, OverflowError, ValueError):
        return None


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return _as_utc(value)
    if not isinstance(value, str) or not value:
        return None
    try:
        return _as_utc(datetime.fromisoformat(value.replace("Z", "+00:00")))
    except ValueError:
        return None


def _utc_now(value: datetime | None) -> datetime:
    return _as_utc(value or datetime.now(timezone.utc))


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _format_utc(value: datetime) -> str:
    return _as_utc(value).isoformat(timespec="seconds").replace("+00:00", "Z")


def _reset_time_label() -> str:
    return f"{DEFAULTS.daily_reset_utc_hour:02d}:{DEFAULTS.daily_reset_utc_minute:02d}Z"


def _local_reset_time_label() -> str:
    return (
        f"{DEFAULTS.daily_reset_local_timezone} "
        f"{DEFAULTS.daily_reset_local_hour:02d}:{DEFAULTS.daily_reset_local_minute:02d}"
    )
