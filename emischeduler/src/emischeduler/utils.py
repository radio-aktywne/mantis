from datetime import date, datetime, time, timedelta, timezone, tzinfo
from time import sleep
from zoneinfo import ZoneInfo

from rq import Retry


class GracefulShutdown:
    def __enter__(self) -> None:
        while True:
            try:
                sleep(60)
            except KeyboardInterrupt:
                return

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False


class ExponentialBackoffRetry(Retry):
    def __init__(self, max: int = 3, delay: int = 1, backoff: float = 2):
        super().__init__(max, [delay * (backoff**i) for i in range(max)])


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
            "Datetime should be naive. Pass timezone name atfer space."
        )
    tz = ZoneInfo(tz) if tz else utczone()
    return dt.replace(tzinfo=tz)


def is_timezone_aware(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


def next_at(t: time, tz: tzinfo = utczone()) -> datetime:
    candidate = to_utc(datetime.combine(date.today(), t, tzinfo=tz))
    return candidate if utcnow() < candidate else candidate + timedelta(days=1)
