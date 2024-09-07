"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

import dataclasses as dc

import pytest

from trackotron.updates import ObservationUpdate


@pytest.fixture
def update() -> ObservationUpdate:
    return ObservationUpdate()


def test_defaults(update: ObservationUpdate) -> None:
    assert dc.asdict(update) == {
        "metadata": None,
        "input": None,
        "output": None,
        "level": None,
        "status_message": None,
    }
