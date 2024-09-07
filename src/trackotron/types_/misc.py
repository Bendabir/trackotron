"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

from typing import Any, Literal, final

from typing_extensions import TypedDict

ObservationType = Literal["span", "generation", "event"]


@final
class Arguments(TypedDict):
    """Arguments of a function/method."""

    args: list[Any]
    kwargs: dict[str, Any]
