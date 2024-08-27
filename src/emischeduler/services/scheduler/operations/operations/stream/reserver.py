import asyncio
from http import HTTPStatus

from emischeduler.config.models import Config
from emischeduler.services.emistream import errors as este
from emischeduler.services.emistream import models as estm
from emischeduler.services.emistream.service import EmistreamService
from emischeduler.services.scheduler.operations.operations.stream import models as m
from emischeduler.utils.time import naiveutcnow


class Reserver:
    """Utility to reserve a stream."""

    def __init__(self, config: Config, emistream: EmistreamService) -> None:
        self._config = config
        self._emistream = emistream

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""

        data = estm.ReserveRequestData(
            event=request.event,
            format=request.format,
            record=False,
        )

        deadline = naiveutcnow() + self._config.operations.stream.timeout

        while naiveutcnow() < deadline:
            req = estm.SubscribeRequest()
            res = await self._emistream.sse.subscribe(req)
            sse = asyncio.create_task(anext(res.events))

            req = estm.ReserveRequest(
                data=data,
            )

            try:
                res = await self._emistream.reserve.reserve(req)
            except este.ServiceError as ex:
                if hasattr(ex, "response"):
                    if ex.response.status_code == HTTPStatus.CONFLICT:
                        timeout = deadline - naiveutcnow()
                        await asyncio.wait_for(sse, timeout=timeout.total_seconds())
                        continue

                raise
            else:
                credentials = res.data.credentials

                return m.ReserveResponse(
                    credentials=credentials,
                )
            finally:
                sse.cancel()
