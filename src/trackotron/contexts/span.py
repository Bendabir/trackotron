"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

from typing import final

from typing_extensions import override

from trackotron.contexts.context import ObservationContext
from trackotron.proxies import ObservationProxy, SpanProxy
from trackotron.types_.compatibility import StatefulClient, StatefulSpanClient
from trackotron.updates import SpanUpdate


@final
class SpanContext(ObservationContext[StatefulSpanClient, SpanUpdate]):
    """Observation context for spans."""

    @override
    def _new_proxy(
        self,
        parent: StatefulClient,
    ) -> ObservationProxy[StatefulSpanClient, SpanUpdate]:
        return SpanProxy(
            parent.span(
                name=self.name,
                start_time=self._now(),
                version=self.observation.get("version"),
                level=self.observation.get("level"),
            ),
            parent,
        )
