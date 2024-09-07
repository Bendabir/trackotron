"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, final

from typing_extensions import NotRequired, TypedDict

if TYPE_CHECKING:
    from trackotron.types_.compatibility import SpanLevel

ObservationType = Literal["span", "generation", "event"]


@final
class Arguments(TypedDict):
    """Arguments of a function/method."""

    args: list[Any]
    kwargs: dict[str, Any]


@final
class TraceParameters(TypedDict):
    """Parameters to inject in the trace when creating it."""

    user: NotRequired[str]
    session: NotRequired[str]
    release: NotRequired[str]
    tags: NotRequired[list[str]]
    public: NotRequired[bool]


@final
class ObservationParameters(TypedDict):
    """Parameters to inject in the observation when creating it."""

    metadata: NotRequired[dict[str, Any]]
    version: NotRequired[str]
    level: NotRequired[SpanLevel]
