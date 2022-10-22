import logging
from datetime import timedelta, datetime
from tempfile import mkstemp
from typing import Dict, List
from uuid import UUID

from rocketry import Session
from rocketry.args import Arg, Session as SessionArg
from rocketry.conditions.api import after_success, after_finish
from rocketry.core import Task

from emischeduler.models.data import TaskGroup
from emischeduler.scheduler.conditions import once
from emischeduler.scheduler.tasks.cleanup import cleanup
from emischeduler.scheduler.tasks.fetch import fetch
from emischeduler.scheduler.tasks.reserve import reserve
from emischeduler.scheduler.tasks.stream import stream
from emischeduler.shows.client import ShowsClient
from emischeduler.shows.models.data import Event
from emischeduler.time import utcnow

logger = logging.getLogger(__name__)


def hash_event(event: Event) -> UUID:
    return UUID(int=hash(event))


def filter_groups(
    groups: Dict[UUID, TaskGroup], from_date: datetime, to_date: datetime
) -> Dict[UUID, TaskGroup]:
    return {
        group_id: group
        for group_id, group in groups.items()
        if from_date <= group.event.params.start <= to_date
    }


def clean_tasks(
    groups: Dict[UUID, TaskGroup],
    events_map: Dict[UUID, Event],
    session: Session,
    from_date: datetime,
    to_date: datetime,
) -> int:
    groups_in_range = filter_groups(groups, from_date, to_date)
    n = 0

    for event_hash, group in groups_in_range.items():
        if event_hash not in events_map:
            logger.warning(
                f"Event for {group.event.show.label} not found in timetable. "
                f"Deleting..."
            )
            for task in group.tasks:
                session.remove_task(task)
            n += len(group.tasks)
            groups.pop(event_hash, None)

    return n


def create_tasks(
    event: Event,
    session: Session,
    event_hash: UUID,
) -> List[Task]:
    _, path = mkstemp()
    fetch_task = session.create_task(
        name=f"fetch-{event_hash}",
        func=fetch,
        start_cond=once.at(event.params.start - timedelta(minutes=30)),
        parameters={"event": event, "path": path},
    )
    reserve_task = session.create_task(
        name=f"reserve-{event_hash}",
        func=reserve,
        start_cond=(
            after_success(fetch_task)
            & once.at(event.params.start - timedelta(seconds=5))
        ),
        parameters={"event": event},
    )
    stream_task = session.create_task(
        name=f"stream-{event_hash}",
        func=stream,
        start_cond=(after_success(reserve_task) & once.at(event.params.start)),
        parameters={
            "event": event,
            "path": path,
            "reservation_task_name": reserve_task.name,
        },
    )
    cleanup_task = session.create_task(
        name=f"cleanup-{event_hash}",
        func=cleanup,
        start_cond=(
            after_finish(fetch_task)
            & once.at(event.params.end + timedelta(minutes=30))
        ),
        parameters={"path": path, "group": event_hash},
    )
    return [fetch_task, reserve_task, stream_task, cleanup_task]


def add_tasks(
    events_map: Dict[UUID, Event],
    groups: Dict[UUID, TaskGroup],
    session: Session,
) -> int:
    n = 0

    for event_hash, event in events_map.items():
        if event_hash not in groups:
            tasks = create_tasks(event, session, event_hash)
            groups[event_hash] = TaskGroup(event=event, tasks=tasks)
            n += len(tasks)

    return n


async def sync(
    delta: timedelta,
    client: ShowsClient = Arg("shows"),
    groups: Dict[UUID, TaskGroup] = Arg("groups"),
    session: Session = SessionArg(),
) -> None:
    logger.info("Syncing events...")

    from_date = utcnow()
    to_date = from_date + delta

    events = await client.timetable(from_date, to_date)
    events_map = {hash_event(event): event for event in events}

    logger.info(f"Cleaning tasks...")
    n = clean_tasks(groups, events_map, session, from_date, to_date)
    logger.info(f"{n} tasks cleaned.")

    logger.info(f"Adding tasks...")
    n = add_tasks(events_map, groups, session)
    logger.info(f"{n} tasks added.")
