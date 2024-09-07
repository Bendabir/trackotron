"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

from typing import final

from typing_extensions import override

from trackotron.contexts.context import ObservationContext
from trackotron.proxies import EventProxy, ObservationProxy
from trackotron.types_.compatibility import StatefulClient
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
                version=self.observation.get("version"),
                level=self.observation.get("level"),
            ),
            parent,
        )
