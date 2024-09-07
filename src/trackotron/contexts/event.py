"""Copyright (c) 2024 Bendabir."""

# mypy: allow-any-unimported
from __future__ import annotations

from typing import final

from langfuse.client import StatefulClient
from typing_extensions import override

from trackotron.contexts.context import ObservationContext
from trackotron.proxies import EventProxy, ObservationProxy
from trackotron.updates import EventUpdate


@final
class EventContext(ObservationContext[StatefulClient, EventUpdate]):
    """Observation context for events."""

    @override
    def _new_proxy(
        self,
        parent: StatefulClient,
    ) -> ObservationProxy[StatefulClient, EventUpdate]:
        return EventProxy(
            parent.event(
                name=self.name,
                start_time=self._now(),
                version=self.version,
                level=self.level,
            ),
            parent,
        )
