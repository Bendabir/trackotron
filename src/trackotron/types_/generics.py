"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

from typing import TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
