"""Copyright (c) 2024 Bendabir."""

from __future__ import annotations

import abc
import datetime as dt
import functools as ft
import inspect
import traceback as tb
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Generic,
    TypeVar,
    final,
    overload,
)

from typing_extensions import Concatenate, Self, override

from trackotron.proxies import O_co, ObservationProxy
from trackotron.updates import ObservationUpdate

if TYPE_CHECKING:
    from contextvars import ContextVar
    from types import TracebackType

    from trackotron.types_ import Arguments, P, R_co
    from trackotron.types_.compatibility import Langfuse, StatefulClient
    from trackotron.types_.misc import ObservationParameters, TraceParameters

U_co = TypeVar("U_co", bound=ObservationUpdate, covariant=True)


class ObservationContext(
    AbstractAsyncContextManager[ObservationProxy[O_co, U_co]],
    AbstractContextManager[ObservationProxy[O_co, U_co]],
    Generic[O_co, U_co],
):
    """Context manager and decorator to observe a block of code."""

    __slots__ = (
        "_metadata",
        "_proxy",
        "capture_input",
        "capture_output",
        "client",
        "level",
        "name",
        "public",
        "session",
        "stack",
        "tags",
        "user",
        "version",
    )

    def __init__(
        self,
        client: Langfuse,
        stack: ContextVar[tuple[StatefulClient, ...]],
        *,
        name: str | None = None,
        trace: TraceParameters | None = None,
        observation: ObservationParameters | None = None,
        capture_input: bool = True,
        capture_output: bool = True,
    ) -> None:
        super().__init__()

        self.client = client
        self.stack = stack
        self.name = name
        self.trace = trace or {}
        self.observation = observation or {}
        self.capture_input = capture_input
        self.capture_output = capture_output

        self._proxy: ObservationProxy[O_co, U_co] | None = None

    @final
    @staticmethod
    def _now() -> dt.datetime:
        return dt.datetime.now(dt.timezone.utc)

    @abc.abstractmethod
    def _new_proxy(self, parent: StatefulClient) -> ObservationProxy[O_co, U_co]:
        raise NotImplementedError

    @final
    @override
    def __enter__(self) -> ObservationProxy[O_co, U_co]:
        # TODO : Support reuse with an internal stack  # noqa: FIX002
        if self._proxy is not None:
            raise RuntimeError("The observation context is already in use.")

        stack = self.stack.get()
        metadata = self.observation.get("metadata")

        if stack:
            parent = stack[-1]
        else:
            parent = self.client.trace(
                name=f"<{self.name}>" if self.name else None,
                user_id=self.trace.get("user"),
                session_id=self.trace.get("session"),
                # Ensure consistency with the observation
                metadata=metadata,
                version=self.observation.get("version"),
                release=self.trace.get("release"),
                tags=self.trace.get("tags"),
                timestamp=self._now(),
                public=self.trace.get("public"),
            )

        self._proxy = self._new_proxy(parent)
        update = ObservationUpdate(metadata=metadata)

        self._proxy.update(update)

        self.stack.set((*stack, self._proxy.observation))

        return self._proxy

    @final
    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        stack = self.stack.get()

        if exc_value is not None:
            message = str(exc_value)
            update = ObservationUpdate(
                level="ERROR",
                status_message=message,
                metadata={
                    "error": {
                        "type": (
                            exc_type.__name__
                            if exc_type is not None
                            else exc_value.__class__.__name__
                        ),
                        "message": message,
                        "traceback": "".join(
                            tb.format_exception(exc_type, exc_value, traceback)
                        ).strip()
                        or None,
                    }
                },
            )

            if self._proxy:
                self._proxy.update(update)

        if self._proxy:
            self._proxy.finalize()

            self._proxy = None

        self.stack.set(stack[:-1])

        return None

    @final
    @override
    async def __aenter__(self) -> ObservationProxy[O_co, U_co]:
        raise NotImplementedError

    @final
    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        raise NotImplementedError

    # Inspired by contextlib
    @final
    def _context(self) -> Self:
        return self

    @final
    @staticmethod
    def _extract_arguments(
        f: Callable[
            Concatenate[ObservationProxy[O_co, U_co], P],
            R_co,
        ],
        /,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Arguments:
        # For the arguments, we need to be a bit smarter
        # because arguments with defaults are not in the args nor kwargs
        # Therefore, we need to extract them from the function signature
        # We iterate in order. For positional only, we'll append to the args.
        # It safe because they can only be passed as args, so order is ensured.
        # If a default is used, it must be after the first provided args.
        # For other arguments, we'll inject them in the kwargs if not provided.
        signature = inspect.signature(f)

        default_args: list[Any] = []
        default_kwargs: dict[str, Any] = {}

        for n, p in signature.parameters.items():
            if p.default is inspect.Parameter.empty or p.name in {"self", "cls"}:
                continue

            if p.kind is inspect.Parameter.POSITIONAL_ONLY:
                default_args.append(p.default)
            elif n not in kwargs:
                default_kwargs[n] = p.default

        return {
            # We need to remove the first N defaults when args are provided
            "args": [*args, *default_args[len(args) :]],
            "kwargs": {**kwargs, **default_kwargs},
        }

    @final
    @staticmethod
    def _is_method(f: Callable[P, R_co], /) -> bool:
        # Inspired by what Langfuse is doing.
        # Methods are not bound when decorated, so we need another way to identify them.
        parameters = inspect.signature(f).parameters

        return inspect.ismethod(f) or any(p in parameters for p in ("self", "cls"))

    @final
    def _wrap_sync(
        self,
        f: Callable[
            Concatenate[ObservationProxy[O_co, U_co], P],
            R_co,
        ],
        /,
    ) -> Callable[P, R_co]:
        @ft.wraps(f)
        def wrap(*args: Any, **kwargs: Any) -> R_co:
            with self._context() as proxy:
                is_method = self._is_method(f)

                update = ObservationUpdate(
                    metadata={
                        "module": f.__module__,
                        "file": f.__code__.co_filename,
                        "qualname": f.__qualname__,
                    }
                )

                if self.capture_input:
                    update.input = self._extract_arguments(
                        f,
                        *(args[1:] if is_method else args),
                        **kwargs,
                    )

                # Couldn't find a way to have proper typing for methods,
                # so we need to work around a bit
                if is_method:
                    result = f(
                        args[0],
                        proxy,  # type: ignore[arg-type]
                        *args[1:],
                        **kwargs,
                    )
                else:
                    result = f(proxy, *args, **kwargs)

                if self.capture_output:
                    update.output = result

                proxy.update(update)

                return result

        return wrap

    @final
    def _wrap_async(
        self,
        f: Callable[
            Concatenate[ObservationProxy[O_co, U_co], P],
            Coroutine[Any, Any, R_co],
        ],
        /,
    ) -> Callable[P, Coroutine[Any, Any, R_co]]:
        raise NotImplementedError

    @overload
    def __call__(
        self,
        f: Callable[
            Concatenate[ObservationProxy[O_co, U_co], P],
            R_co,
        ],
        /,
    ) -> Callable[P, R_co]: ...

    @overload
    def __call__(
        self,
        f: Callable[
            Concatenate[ObservationProxy[O_co, U_co], P],
            Coroutine[Any, Any, R_co],
        ],
        /,
    ) -> Callable[P, Coroutine[Any, Any, R_co]]: ...

    @final
    def __call__(
        self,
        f: Callable[
            Concatenate[ObservationProxy[O_co, U_co], P],
            R_co,
        ],
        /,
    ) -> Callable[P, R_co] | Callable[P, Coroutine[Any, Any, R_co]]:
        """Decorate a function to observe it in Langfuse.

        If the name was not provided, it will infer it from the function/method.

        Returns
        -------
        Callable[P, R_co]
            The function or method to observe.
        """
        self.name = self.name or f.__qualname__

        if inspect.iscoroutinefunction(f):
            return self._wrap_async(f)

        return self._wrap_sync(f)
