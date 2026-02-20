from typing import Annotated

from pydantic import Field

from mantis.models.events import test

type Event = Annotated[
    test.TestEvent,
    Field(discriminator="type"),
]
