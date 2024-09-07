"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

import dataclasses as dc

import pytest

from trackotron.updates import SpanUpdate


@pytest.fixture
def update() -> SpanUpdate:
    return SpanUpdate()


def test_defaults(update: SpanUpdate) -> None:
    assert dc.asdict(update) == {
        "metadata": None,
        "input": None,
        "output": None,
        "level": None,
        "status_message": None,
        "end_time": None,
    }
