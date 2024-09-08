from __future__ import annotations

import datetime as dt
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Callable, final

import pytest
from typing_extensions import override

from trackotron.contexts.context import ObservationContext
from trackotron.proxies import ObservationProxy
from trackotron.types_.compatibility import StatefulClient
from trackotron.updates import ObservationUpdate

if TYPE_CHECKING:
    from trackotron.types_ import Arguments
    from trackotron.types_.compatibility import Langfuse


@final
class FakeProxy(ObservationProxy[StatefulClient, ObservationUpdate]):
    @override
    def _finalize(self) -> None:
        return None


FakeProxyAlias = ObservationProxy[StatefulClient, ObservationUpdate]


@final
class FakeContext(ObservationContext[StatefulClient, ObservationUpdate]):
    @override
    def _new_proxy(
        self,
        parent: StatefulClient,
    ) -> ObservationProxy[StatefulClient, ObservationUpdate]:
        return FakeProxy(parent.event(), parent)


@pytest.fixture
def stack() -> ContextVar[tuple[StatefulClient, ...]]:
    return ContextVar("stack", default=())


@pytest.fixture
def context(
    client: Langfuse,
    stack: ContextVar[tuple[StatefulClient, ...]],
) -> FakeContext:
    return FakeContext(client, stack)


def test_now() -> None:
    now = FakeContext._now()

    assert now.tzinfo == dt.timezone.utc


def test_enter_twice(context: FakeContext) -> None:
    with pytest.raises(RuntimeError), context, context:
        pass


def test_context_manager_sync(context: FakeContext) -> None:
    with context as _:
        pass


@pytest.mark.anyio
@pytest.mark.skip(reason="TODO : Support async.")
async def test_context_manager_async(context: FakeContext) -> None:
    async with context as _:
        pass


def test_decorator_sync(context: FakeContext) -> None:
    @context
    def run(proxy: FakeProxyAlias) -> None:
        pass

    run()


@pytest.mark.anyio
@pytest.mark.skip(reason="TODO : Support async.")
async def test_decorator_async(context: FakeContext) -> None:
    @context
    async def run(proxy: FakeProxyAlias) -> None:
        pass

    await run()


def _f(a: str, /, b: str, *, c: str = "c") -> str:
    return a or b or c


async def _af(a: str, /, b: str, *, c: str = "c") -> str:  # noqa: RUF029
    return a or b or c


def _im(self: Any) -> None:  # noqa: ARG001
    return None


async def _aim(self: Any) -> None:  # noqa: ARG001, RUF029
    return None


def _cm(cls: Any) -> None:  # noqa: ARG001
    return None


async def _acm(cls: Any) -> None:  # noqa: RUF029, ARG001
    return None


def _p(a: str = "a", b: str = "b", /) -> str:
    return a or b


async def _ap(a: str = "a", b: str = "b", /) -> str:  # noqa: RUF029
    return a or b


@pytest.mark.parametrize(
    ("f", "args", "kwargs", "expected"),
    [
        (
            _f,
            [],
            {},
            {"args": [], "kwargs": {"c": "c"}},
        ),
        (
            _af,
            [],
            {},
            {"args": [], "kwargs": {"c": "c"}},
        ),
        (
            _f,
            ["a"],
            {"b": "b"},
            {"args": ["a"], "kwargs": {"b": "b", "c": "c"}},
        ),
        (
            _af,
            ["a"],
            {"b": "b"},
            {"args": ["a"], "kwargs": {"b": "b", "c": "c"}},
        ),
        (
            _f,
            ["a"],
            {"b": "b", "c": "d"},
            {"args": ["a"], "kwargs": {"b": "b", "c": "d"}},
        ),
        (
            _af,
            ["a"],
            {"b": "b", "c": "d"},
            {"args": ["a"], "kwargs": {"b": "b", "c": "d"}},
        ),
        (
            _im,
            [],
            {},
            {"args": [], "kwargs": {}},
        ),
        (
            _aim,
            [],
            {},
            {"args": [], "kwargs": {}},
        ),
        (
            _cm,
            [],
            {},
            {"args": [], "kwargs": {}},
        ),
        (
            _acm,
            [],
            {},
            {"args": [], "kwargs": {}},
        ),
        (
            _p,
            [],
            {},
            {"args": ["a", "b"], "kwargs": {}},
        ),
        (
            _ap,
            [],
            {},
            {"args": ["a", "b"], "kwargs": {}},
        ),
        (
            _p,
            ["c"],
            {},
            {"args": ["c", "b"], "kwargs": {}},
        ),
        (
            _ap,
            ["c"],
            {},
            {"args": ["c", "b"], "kwargs": {}},
        ),
    ],
    ids=[
        "empty-sync",
        "empty-async",
        "partial-sync",
        "partial-async",
        "full-sync",
        "full-async",
        "instance-method-sync",
        "instance-method-async",
        "class-method-sync",
        "class-method-async",
        "positional-default-sync",
        "positional-default-async",
        "positional-sync",
        "positional-async",
    ],
)
def test_extract_arguments(
    f: Callable[..., Any],
    args: list[Any],
    kwargs: dict[str, Any],
    expected: Arguments,
) -> None:
    arguments = ObservationContext._extract_arguments(f, *args, **kwargs)

    assert arguments == expected


@pytest.mark.parametrize(
    ("f", "expected"),
    [
        (_f, False),
        (_af, False),
        (_im, True),
        (_aim, True),
        (_cm, True),
        (_acm, True),
    ],
    ids=[
        "function",
        "function-async",
        "instance-method",
        "instance-method-async",
        "class-method",
        "class-method-async",
    ],
)
def test_is_method(f: Callable[..., Any], expected: bool) -> None:  # noqa: FBT001
    assert ObservationContext._is_method(f) is expected
