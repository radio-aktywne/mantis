from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def utczone() -> ZoneInfo:
    return ZoneInfo("Etc/UTC")


def utcnow() -> datetime:
    return datetime.now(utczone())


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(utczone())


def parse_datetime_with_timezone(dt: str) -> datetime:
    parts = dt.split(" ")
    dt, tz = parts[0], (parts[1] if len(parts) > 1 else None)
    dt = datetime.fromisoformat(dt)
    if is_timezone_aware(dt):
        raise ValueError(
            "Datetime should be naive. Pass timezone name after space."
        )
    tz = ZoneInfo(tz) if tz else utczone()
    return dt.replace(tzinfo=tz)


def is_timezone_aware(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


def stringify(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")
