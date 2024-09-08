"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING, Literal, final, overload

from typing_extensions import Unpack

from trackotron.contexts import EventContext, GenerationContext, SpanContext

if TYPE_CHECKING:
    from trackotron.contexts import ObservationContext
    from trackotron.types_ import ObservationType
    from trackotron.types_.compatibility import (
        Langfuse,
        StatefulClient,
        StatefulGenerationClient,
        StatefulSpanClient,
    )
    from trackotron.types_.misc import ObservationParameters, TraceParameters
    from trackotron.updates import EventUpdate, GenerationUpdate, SpanUpdate


@final
class Observer:
    """Factory to build new observation contexts."""

    def __init__(self, client: Langfuse, **trace: Unpack[TraceParameters]) -> None:
        self.client = client
        self.trace = trace
        self._stack: ContextVar[tuple[StatefulClient, ...]] = ContextVar(
            "stack",
            default=(),
        )

    @overload
    def observe(
        self,
        *,
        type_: Literal["span"] = "span",
        name: str | None = None,
        trace: TraceParameters | None = None,
        observation: ObservationParameters | None = None,
        capture_input: bool = True,
        capture_output: bool = True,
    ) -> ObservationContext[StatefulSpanClient, SpanUpdate]: ...

    @overload
    def observe(
        self,
        *,
        type_: Literal["generation"],
        name: str | None = None,
        trace: TraceParameters | None = None,
        observation: ObservationParameters | None = None,
        capture_input: bool = True,
        capture_output: bool = True,
    ) -> ObservationContext[StatefulGenerationClient, GenerationUpdate]: ...

    @overload
    def observe(
        self,
        *,
        type_: Literal["event"],
        name: str | None = None,
        trace: TraceParameters | None = None,
        observation: ObservationParameters | None = None,
        capture_input: bool = True,
        capture_output: bool = True,
    ) -> ObservationContext[StatefulClient, EventUpdate]: ...

    def observe(
        self,
        *,
        type_: ObservationType = "span",
        name: str | None = None,
        trace: TraceParameters | None = None,
        observation: ObservationParameters | None = None,
        capture_input: bool = True,
        capture_output: bool = True,
    ) -> ObservationContext[
        StatefulSpanClient | StatefulGenerationClient | StatefulClient,
        SpanUpdate | GenerationUpdate | EventUpdate,
    ]:
        """Get a new observation context.

        Some arguments (user, session, version, tags) will only be used
        on the parent trace if one is created.

        Returns
        -------
        SpanContext
            If the observation type is 'span'.
        GenerationContext
            If the observation type is 'generation'.
        EventContext
            If the observation type is 'event'.

        Raises
        ------
        ValueError
            If the observation type cannot be understood.
        """
        # Inject some defaults if not provided
        if self.trace:
            trace = {**self.trace, **(trace or {})}

        if type_ == "span":
            return SpanContext(
                client=self.client,
                stack=self._stack,
                name=name,
                trace=trace,
                observation=observation,
                capture_input=capture_input,
                capture_output=capture_output,
            )

        if type_ == "generation":
            return GenerationContext(
                client=self.client,
                stack=self._stack,
                name=name,
                trace=trace,
                observation=observation,
                capture_input=capture_input,
                capture_output=capture_output,
            )

        if type_ == "event":
            return EventContext(
                client=self.client,
                stack=self._stack,
                name=name,
                trace=trace,
                observation=observation,
                capture_input=capture_input,
                capture_output=capture_output,
            )

        raise ValueError(f"Unsupported type '{type_}'.")
