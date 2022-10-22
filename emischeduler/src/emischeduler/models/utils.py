from emischeduler.shows.models.data import Event as ShowsEvent
from emischeduler.stream.models.data import (
    Event as StreamEvent,
    Show as StreamShow,
)
from emischeduler.time import to_utc


def map_event(event: ShowsEvent) -> StreamEvent:
    metadata = {"title": event.show.title}
    if event.show.description is not None:
        metadata["description"] = event.show.description
    show = StreamShow(label=str(event.show.label), metadata=metadata)
    return StreamEvent(
        show=show,
        type=event.type,
        start=to_utc(event.params.start),
        end=to_utc(event.params.end),
    )
