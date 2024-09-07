"""Copyright (c) 2024 Bendabir."""

# mypy: allow-any-unimported
from __future__ import annotations

import abc
import dataclasses as dc
from typing import Any, Generic, TypeVar, final, overload

from langfuse.client import (
    StatefulClient,
    StatefulGenerationClient,
    StatefulSpanClient,
    StatefulTraceClient,
)
from typing_extensions import override

from trackotron.updates import (
    EventUpdate,
    GenerationUpdate,
    ObservationUpdate,
    SpanUpdate,
)

O_co = TypeVar("O_co", bound=StatefulClient, covariant=True)
U_contra = TypeVar("U_contra", bound=ObservationUpdate, contravariant=True)


class ObservationProxy(abc.ABC, Generic[O_co, U_contra]):
    """Proxy on an observation client.

    It will accumulate the updates until the context manager is exited.
    """

    __slots__ = ("_patch", "observation", "parent")

    def __init__(self, observation: O_co, parent: StatefulClient) -> None:
        self.observation = observation
        self.parent = parent
        self._patch: dict[str, Any] = {}

    @final
    @property
    def patch(self) -> dict[str, Any]:
        """View of the internal update patch."""
        return self._patch.copy()

    @overload
    def update(self, update: U_contra) -> None: ...

    @overload
    def update(self, update: ObservationUpdate) -> None: ...

    @final
    def update(self, update: U_contra | ObservationUpdate) -> None:
        """Store the update until finalization.

        Note
        ----
        All fields over overwritten, except the metadata which is merged.
        """
        metadata: dict[str, Any] = self._patch.get("metadata", {}) or {}

        if update.metadata is not None:
            update.metadata = {**metadata, **update.metadata}

        self._patch = {**self._patch, **dc.asdict(update)}

    @final
    def finalize(self) -> None:
        """Send the updates to Langfuse."""
        if self._patch:
            self._finalize()

            # If the parent is a trace, also inject some useful data
            # Couldn't find a more elegant way to achieve this
            if isinstance(self.parent, StatefulTraceClient):
                self.parent.update(
                    **{k: self._patch.get(k) for k in ("input", "output", "metadata")}
                )

            self._patch = {}

    @abc.abstractmethod
    def _finalize(self) -> None:
        raise NotImplementedError


@final
class SpanProxy(ObservationProxy[StatefulSpanClient, SpanUpdate]):
    """Proxy for a span observation."""

    @override
    def _finalize(self) -> None:
        self.observation.end(**self._patch)


@final
class GenerationProxy(ObservationProxy[StatefulGenerationClient, GenerationUpdate]):
    """Proxy for a generation observation."""

    @override
    def _finalize(self) -> None:
        self.observation.end(**self._patch)


@final
class EventProxy(ObservationProxy[StatefulClient, EventUpdate]):
    """Proxy for an event observation."""

    @override
    def _finalize(self) -> None:
        # Appears to be the only way to update an event...
        self.parent.event(id=self.observation.id, **self._patch)
