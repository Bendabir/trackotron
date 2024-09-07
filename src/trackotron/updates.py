"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

import dataclasses as dc
import sys
from typing import TYPE_CHECKING, Any, final

if TYPE_CHECKING:

    import datetime as dt

    from trackotron.types_.compatibility import ModelUsage, PromptClient, SpanLevel

_DATACLASS_KWARGS: dict[str, Any] = {}

if sys.version_info > (3, 10):  # pragma: no cover
    _DATACLASS_KWARGS["slots"] = True

# NOTE : Using dataclasses as it behaves better with inheritance.
#        There could be some advantages of using TypedDict
#        but it's not so straight forward.


@dc.dataclass(**_DATACLASS_KWARGS)
class ObservationUpdate:
    """Updatable fields of an observation."""

    metadata: dict[str, Any] | None = None
    input: Any | None = None
    output: Any | None = None
    level: SpanLevel | None = None
    status_message: str | None = None


@dc.dataclass(**_DATACLASS_KWARGS)
class SpanUpdate(ObservationUpdate):
    """Updatable fields of a span."""

    end_time: dt.datetime | None = None


@final
@dc.dataclass(**_DATACLASS_KWARGS)
class GenerationUpdate(SpanUpdate):
    """Updatable fields of a generation."""

    completion_start_time: dt.datetime | None = None
    model: str | None = None
    model_parameters: dict[str, Any] | None = None
    usage: ModelUsage | None = None
    prompt: PromptClient | None = None


@final
@dc.dataclass(**_DATACLASS_KWARGS)
class EventUpdate(ObservationUpdate):
    """Updatable fields of an event."""
