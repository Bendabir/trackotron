from __future__ import annotations

import os
from typing import TYPE_CHECKING, Generator

import httpx
import pytest
from langfuse.client import Langfuse as _Langfuse

if TYPE_CHECKING:
    from trackotron.types_.compatibility import Langfuse


@pytest.fixture(scope="session", autouse=True)
def clean_env() -> None:
    env_vars = set(os.environ.keys())

    for e in env_vars:
        if e.startswith("LANGFUSE_"):
            del os.environ[e]


@pytest.fixture(scope="session")
def transport() -> httpx.BaseTransport:
    return httpx.MockTransport(handler=lambda _: httpx.Response(200))


@pytest.fixture(scope="session")
def client(transport: httpx.BaseTransport) -> Generator[Langfuse, None, None]:
    with httpx.Client(transport=transport) as client:
        yield _Langfuse(httpx_client=client, enabled=False)
