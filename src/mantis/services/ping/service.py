from mantis.services.ping import models as m


class PingService:
    """Service for pings."""

    async def ping(self, request: m.PingRequest) -> m.PingResponse:
        """Ping."""

        return m.PingResponse()
