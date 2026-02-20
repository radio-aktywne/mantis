import asyncio
from http import HTTPStatus

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
        data = om.ReservationInput(
            event=request.event, format=request.format, record=False
        )

        deadline = naiveutcnow() + self._config.operations.stream.timeout

        while naiveutcnow() < deadline:
            subscribe_request = om.SubscribeRequest(
                types={om.EventType.AVAILABILITY_CHANGED}
            )
            subscribe_response = await self._octopus.sse.subscribe(subscribe_request)
            message_task = asyncio.create_task(
                coroutine(anext(subscribe_response.messages))
            )

            reserve_request = om.ReserveRequest(data=data)

            try:
                reserve_response = await self._octopus.reserve.reserve(reserve_request)
            except oe.ResponseError as ex:
                if ex.response.status_code == HTTPStatus.CONFLICT:
                    timeout = deadline - naiveutcnow()
                    await asyncio.wait_for(
                        message_task, timeout=timeout.total_seconds()
                    )
                    continue

                raise
            else:
                credentials = reserve_response.reservation.credentials

                return m.ReserveResponse(credentials=credentials)
            finally:
                message_task.cancel()
                await asyncio.wait([message_task])

        raise e.ReservationFailedError(request.event)
