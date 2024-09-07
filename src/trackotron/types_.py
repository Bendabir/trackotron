"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

from typing import Any, Literal, TypeVar, final

from typing_extensions import ParamSpec, TypedDict

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)

ObservationType = Literal["span", "generation", "event"]


@final
class Arguments(TypedDict):
    """Arguments of a function/method."""

    args: list[Any]
    kwargs: dict[str, Any]
