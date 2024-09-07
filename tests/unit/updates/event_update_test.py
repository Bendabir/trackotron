"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

import dataclasses as dc

import pytest

from trackotron.updates import EventUpdate


@pytest.fixture
def update() -> EventUpdate:
    return EventUpdate()


def test_defaults(update: EventUpdate) -> None:
    assert dc.asdict(update) == {
        "metadata": None,
        "input": None,
        "output": None,
        "level": None,
        "status_message": None,
    }
