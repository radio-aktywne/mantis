import asyncio
from http import HTTPStatus

from mantis.config.models import Config
from mantis.services.octopus import errors as oe
from mantis.services.octopus import models as om
from mantis.services.octopus.service import OctopusService
from mantis.services.scheduler.operations.operations.stream import errors as e
from mantis.services.scheduler.operations.operations.stream import models as m
from mantis.utils.time import naiveutcnow


class Reserver:
    """Utility to reserve a stream."""

    def __init__(self, config: Config, octopus: OctopusService) -> None:
        self._config = config
        self._octopus = octopus

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""
        subscribe_request = om.SubscribeRequest(
            types={om.EventType.AVAILABILITY_CHANGED}
        )
        subscribe_response = await self._octopus.sse.subscribe(subscribe_request)

        try:
            deadline = naiveutcnow() + self._config.operations.stream.timeout

            while naiveutcnow() < deadline:
                message_task = asyncio.ensure_future(anext(subscribe_response.messages))

                try:
                    reserve_request = om.ReserveRequest(
                        data=om.ReservationInput(
                            event=request.event, format=request.format
                        )
                    )
                    reserve_response = await self._octopus.reserve.reserve(
                        reserve_request
                    )
                except oe.ResponseError as ex:
                    if ex.response.status_code == HTTPStatus.CONFLICT:
                        await asyncio.wait_for(
                            message_task,
                            timeout=(deadline - naiveutcnow()).total_seconds(),
                        )
                        continue

                    raise
                else:
                    return m.ReserveResponse(
                        credentials=reserve_response.reservation.credentials
                    )
                finally:
                    message_task.cancel()
                    await asyncio.wait([message_task])

            raise e.ReservationFailedError(request.event)
        finally:
            await subscribe_response.messages.aclose()
