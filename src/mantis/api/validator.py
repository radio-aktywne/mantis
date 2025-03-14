import builtins
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from pydantic import RootModel, ValidationError

from mantis.api.exceptions import BadRequestException


class Validator[T]:
    """Validates input data."""

    def __init__(self, type: builtins.type[T]) -> None:
        self.Model = RootModel[type]

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except ValidationError as ex:
            raise BadRequestException(extra=ex.errors(include_context=False)) from ex

    def object(self, value: Any) -> T:
        """Validate an object."""

        with self._handle_errors():
            return self.Model.model_validate(value).root

    def json(self, value: str) -> T:
        """Validate a JSON string."""

        with self._handle_errors():
            return self.Model.model_validate_json(value).root
