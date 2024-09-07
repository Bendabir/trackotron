from __future__ import annotations

from typing import Any, final

import pytest
from typing_extensions import override

from trackotron.proxies import ObservationProxy
from trackotron.types_.compatibility import Langfuse, StatefulClient
from trackotron.updates import ObservationUpdate


@final
class FakeProxy(ObservationProxy[StatefulClient, ObservationUpdate]):
    @override
    def _finalize(self) -> None:
        return None


@pytest.fixture
def parent(client: Langfuse) -> StatefulClient:
    return client.trace()


@pytest.fixture
def observation(parent: StatefulClient) -> StatefulClient:
    return parent.event()


@pytest.fixture
def proxy(observation: StatefulClient, parent: StatefulClient) -> FakeProxy:
    return FakeProxy(observation, parent)


def test_defaults(proxy: FakeProxy) -> None:
    assert proxy.patch == {}


@pytest.mark.parametrize(
    ("update", "expected"),
    [
        (
            ObservationUpdate(),
            {
                "metadata": None,
                "input": None,
                "output": None,
                "level": None,
                "status_message": None,
            },
        ),
        (
            ObservationUpdate(
                input="input",
                output="output",
                level="ERROR",
                status_message="message",
            ),
            {
                "metadata": None,
                "input": "input",
                "output": "output",
                "level": "ERROR",
                "status_message": "message",
            },
        ),
        (
            ObservationUpdate(metadata={}),
            {
                "metadata": None,
                "input": None,
                "output": None,
                "level": None,
                "status_message": None,
            },
        ),
        (
            ObservationUpdate(metadata={"field": "value"}),
            {
                "metadata": {"field": "value"},
                "input": None,
                "output": None,
                "level": None,
                "status_message": None,
            },
        ),
    ],
    ids=["empty", "partial", "empty-metadata", "new-metadata"],
)
def test_update(
    proxy: FakeProxy,
    update: ObservationUpdate,
    expected: dict[str, Any],
) -> None:
    proxy.update(update)

    assert proxy.patch == expected


@pytest.mark.parametrize(
    ("updates", "expected"),
    [
        (
            [ObservationUpdate(), ObservationUpdate()],
            {
                "metadata": None,
                "input": None,
                "output": None,
                "level": None,
                "status_message": None,
            },
        ),
        (
            [
                ObservationUpdate(),
                ObservationUpdate(
                    input="input",
                    output="output",
                    level="ERROR",
                    status_message="message",
                ),
            ],
            {
                "metadata": None,
                "input": "input",
                "output": "output",
                "level": "ERROR",
                "status_message": "message",
            },
        ),
        (
            [
                ObservationUpdate(
                    input="init",
                    output="init",
                    level="DEFAULT",
                    status_message="init",
                ),
                ObservationUpdate(
                    input="input",
                    output="output",
                    level="ERROR",
                    status_message="message",
                ),
            ],
            {
                "metadata": None,
                "input": "input",
                "output": "output",
                "level": "ERROR",
                "status_message": "message",
            },
        ),
        (
            [
                ObservationUpdate(),
                ObservationUpdate(metadata={}),
            ],
            {
                "metadata": None,
                "input": None,
                "output": None,
                "level": None,
                "status_message": None,
            },
        ),
        (
            [
                ObservationUpdate(metadata={}),
                ObservationUpdate(),
            ],
            {
                "metadata": None,
                "input": None,
                "output": None,
                "level": None,
                "status_message": None,
            },
        ),
        (
            [
                ObservationUpdate(),
                ObservationUpdate(metadata={"field": "value"}),
            ],
            {
                "metadata": {"field": "value"},
                "input": None,
                "output": None,
                "level": None,
                "status_message": None,
            },
        ),
        (
            [
                ObservationUpdate(metadata={"field": "value"}),
                ObservationUpdate(),
            ],
            {
                "metadata": {"field": "value"},
                "input": None,
                "output": None,
                "level": None,
                "status_message": None,
            },
        ),
        (
            [
                ObservationUpdate(metadata={"field": "value"}),
                ObservationUpdate(metadata={"other": 0}),
            ],
            {
                "metadata": {"field": "value", "other": 0},
                "input": None,
                "output": None,
                "level": None,
                "status_message": None,
            },
        ),
        (
            [
                ObservationUpdate(metadata={"field": "value"}),
                ObservationUpdate(metadata={"field": "other"}),
            ],
            {
                "metadata": {"field": "other"},
                "input": None,
                "output": None,
                "level": None,
                "status_message": None,
            },
        ),
    ],
    ids=[
        "empty",
        "from-empty",
        "overwrite",
        "merge-empty-1",
        "merge-empty-2",
        "fill-empty-1",
        "fill-empty-2",
        "merge-1",
        "merge-2",
    ],
)
def test_many_updates(
    proxy: FakeProxy,
    updates: list[ObservationUpdate],
    expected: dict[str, Any],
) -> None:
    for u in updates:
        proxy.update(u)

    assert proxy.patch == expected
