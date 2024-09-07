"""Copyright (c) 2024 Bendabir."""

# mypy: allow-any-unimported
from __future__ import annotations

from typing import final

from typing_extensions import override

from trackotron.contexts.context import ObservationContext
from trackotron.proxies import GenerationProxy, ObservationProxy
from trackotron.types_.compatibility import StatefulClient, StatefulGenerationClient
from trackotron.updates import GenerationUpdate


@final
class GenerationContext(ObservationContext[StatefulGenerationClient, GenerationUpdate]):
    """Observation context for generations."""

    @override
    def _new_proxy(
        self,
        parent: StatefulClient,
    ) -> ObservationProxy[StatefulGenerationClient, GenerationUpdate]:
        return GenerationProxy(
            parent.generation(
                name=self.name,
                start_time=self._now(),
                version=self.observation.get("version"),
                level=self.observation.get("level"),
                model="<model>",
                model_parameters={
                    "PARAMETER": "<value>",
                },
                usage={
                    "input": 0,
                    "output": 0,
                    "total": 0,
                    "unit": "TOKENS",
                },
            ),
            parent,
        )
