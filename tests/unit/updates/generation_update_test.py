"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

import dataclasses as dc

import pytest

from trackotron.updates import GenerationUpdate


@pytest.fixture
def update() -> GenerationUpdate:
    return GenerationUpdate()


def test_defaults(update: GenerationUpdate) -> None:
    assert dc.asdict(update) == {
        "metadata": None,
        "input": None,
        "output": None,
        "level": None,
        "status_message": None,
        "end_time": None,
        "completion_start_time": None,
        "model": None,
        "model_parameters": None,
        "usage": None,
        "prompt": None,
    }
