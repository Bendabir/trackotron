"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

from typing import Any, Callable, Coroutine

from typing_extensions import Concatenate

from trackotron.types_.generics import C, I, P, R_co

Function = Callable[P, R_co]
InjectedFunction = Callable[Concatenate[I, P], R_co]
Method = Callable[Concatenate[C, P], R_co]
InjectedMethod = Callable[Concatenate[C, I, P], R_co]
ClassMethod = Callable[Concatenate[type[C], P], R_co]
InjectedClassMethod = Callable[Concatenate[type[C], I, P], R_co]

AsyncFunction = Callable[P, Coroutine[Any, Any, R_co]]
AsyncInjectedFunction = Callable[Concatenate[I, P], Coroutine[Any, Any, R_co]]
AsyncMethod = Callable[Concatenate[C, P], Coroutine[Any, Any, R_co]]
AsyncInjectedMethod = Callable[Concatenate[C, I, P], Coroutine[Any, Any, R_co]]
AsyncClassMethod = Callable[Concatenate[type[C], P], Coroutine[Any, Any, R_co]]
AsyncInjectedClassMethod = Callable[
    Concatenate[type[C], I, P],
    Coroutine[Any, Any, R_co],
]
