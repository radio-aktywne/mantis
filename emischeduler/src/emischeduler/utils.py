from datetime import date, datetime, time, timedelta, timezone
from time import sleep

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


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def next_at(t: time, tzinfo: timezone = timezone.utc) -> datetime:
    candidate = to_utc(datetime.combine(date.today(), t, tzinfo=tzinfo))
    return candidate if utcnow() < candidate else candidate + timedelta(days=1)
