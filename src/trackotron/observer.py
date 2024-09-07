"""Copyright (c) 2024 Bendabir."""

# mypy: allow-any-unimported
from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Literal, final, overload

from trackotron.contexts import EventContext, GenerationContext, SpanContext

if TYPE_CHECKING:
    from langfuse.client import (
        Langfuse,
        StatefulClient,
        StatefulGenerationClient,
        StatefulSpanClient,
    )
    from langfuse.types import SpanLevel

    from trackotron.contexts import ObservationContext
    from trackotron.types_ import ObservationType
    from trackotron.updates import EventUpdate, GenerationUpdate, SpanUpdate


@final
class Observer:
    """Factory to build new observation contexts."""

    def __init__(self, client: Langfuse) -> None:
        self.client = client
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
        metadata: dict[str, Any] | None = None,
        user: str | None = None,
        session: str | None = None,
        version: str | None = None,
        tags: list[str] | None = None,
        level: SpanLevel | None = None,
        capture_input: bool = True,
        capture_output: bool = True,
    ) -> ObservationContext[StatefulSpanClient, SpanUpdate]: ...

    @overload
    def observe(
        self,
        *,
        type_: Literal["generation"],
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        user: str | None = None,
        session: str | None = None,
        version: str | None = None,
        tags: list[str] | None = None,
        level: SpanLevel | None = None,
        capture_input: bool = True,
        capture_output: bool = True,
    ) -> ObservationContext[StatefulGenerationClient, GenerationUpdate]: ...

    @overload
    def observe(
        self,
        *,
        type_: Literal["event"],
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        user: str | None = None,
        session: str | None = None,
        version: str | None = None,
        tags: list[str] | None = None,
        level: SpanLevel | None = None,
        capture_input: bool = True,
        capture_output: bool = True,
    ) -> ObservationContext[StatefulClient, EventUpdate]: ...

    def observe(
        self,
        *,
        type_: ObservationType = "span",
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        user: str | None = None,
        session: str | None = None,
        version: str | None = None,
        tags: list[str] | None = None,
        level: SpanLevel | None = None,
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
        if type_ == "span":
            return SpanContext(
                client=self.client,
                stack=self._stack,
                name=name,
                metadata=metadata,
                user=user,
                session=session,
                version=version,
                tags=tags,
                level=level,
                capture_input=capture_input,
                capture_output=capture_output,
            )

        if type_ == "generation":
            return GenerationContext(
                client=self.client,
                stack=self._stack,
                name=name,
                metadata=metadata,
                user=user,
                session=session,
                version=version,
                tags=tags,
                capture_input=capture_input,
                capture_output=capture_output,
            )

        if type_ == "event":
            return EventContext(
                client=self.client,
                stack=self._stack,
                name=name,
                metadata=metadata,
                user=user,
                session=session,
                version=version,
                tags=tags,
                capture_input=capture_input,
                capture_output=capture_output,
            )

        raise ValueError(f"Unsupported type '{type_}'.")
