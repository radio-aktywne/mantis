from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from emischeduler.client import HttpClient
from emischeduler.shows.models.api import TimetableResponse
from emischeduler.shows.models.data import Event
from emischeduler.time import utcnow, stringify


class RawShowsClient:
    def __init__(
        self,
        host: str,
        port: int,
        secure: bool = False,
        http_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._http_client = HttpClient(
            host, port, secure, **(http_kwargs or {})
        )

    async def timetable(
        self, from_date: datetime, to_date: datetime
    ) -> TimetableResponse:
        response = await self._http_client.get(
            "timetable",
            params={
                "from": stringify(from_date.replace(tzinfo=None)),
                "to": stringify(to_date.replace(tzinfo=None)),
            },
        )
        return TimetableResponse.parse_obj(response)


class ShowsClient:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._client = RawShowsClient(*args, **kwargs)

    async def timetable(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Event]:
        from_date = utcnow() if from_date is None else from_date
        to_date = from_date + timedelta(days=1) if to_date is None else to_date
        response = await self._client.timetable(from_date, to_date)
        return response.__root__
