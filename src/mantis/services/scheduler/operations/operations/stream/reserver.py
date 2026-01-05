import asyncio
from http import HTTPStatus
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from httpx import Response

from mantis.config.models import Config
from mantis.services.octopus import errors as oe
from mantis.services.octopus import models as om
from mantis.services.octopus.service import OctopusService
from mantis.services.scheduler.operations.operations.stream import errors as e
from mantis.services.scheduler.operations.operations.stream import models as m
from mantis.utils.asyncify import coroutine
from mantis.utils.time import naiveutcnow


class Reserver:
    """Utility to reserve a stream."""

    def __init__(self, config: Config, octopus: OctopusService) -> None:
        self._config = config
        self._octopus = octopus

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""
        data = om.ReserveRequestData(
            event=request.event,
            format=request.format,
            record=False,
        )

        deadline = naiveutcnow() + self._config.operations.stream.timeout

        while naiveutcnow() < deadline:
            req = om.SubscribeRequest()
            res = await self._octopus.sse.subscribe(req)
            sse = asyncio.create_task(coroutine(anext(res.events)))

            req = om.ReserveRequest(
                data=data,
            )

            try:
                res = await self._octopus.reserve.reserve(req)
            except oe.ServiceError as ex:
                if hasattr(ex, "response"):
                    response = cast("Response", ex.response)  # type: ignore[attr-defined]
                    if response.status_code == HTTPStatus.CONFLICT:
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

        raise e.ReservationFailedError(request.event)
