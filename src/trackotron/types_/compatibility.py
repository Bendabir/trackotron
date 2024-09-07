"""Copyright (c) 2024 Bendabir."""

# ruff: noqa: A002, D101, D102, PLR0913
# NOTE : Reimplementing the interfaces with protocols for compatibility
#        as Langfuse doesn't respect PEP 561 (thus causing some issues with MyPy).
#        Keeping same naming for consistency, but only porting what's useful.
from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    List,
    Literal,
    Optional,
    Protocol,
    Union,
    final,
    overload,
)

from typing_extensions import NotRequired, TypedDict

if TYPE_CHECKING:
    import datetime as dt

SpanLevel = Literal["DEBUG", "DEFAULT", "WARNING", "ERROR"]
ScoreDataType = Literal["NUMERIC", "CATEGORICAL", "BOOLEAN"]
MapValue = Union[Optional[str], Optional[int], Optional[bool], Optional[List[str]]]


@final
class ModelUsage(TypedDict):
    unit: NotRequired[str | None]
    input: NotRequired[int | None]
    output: NotRequired[int | None]
    total: NotRequired[int | None]
    input_cost: NotRequired[float | None]
    output_cost: NotRequired[float | None]
    total_cost: NotRequired[float | None]


class BasePromptClient(Protocol):
    name: str
    version: int
    config: dict[str, Any]
    labels: list[str]
    tags: list[str]


class TextPromptClient(BasePromptClient, Protocol):
    def compile(self, **kwargs: Any) -> str: ...


class ChatMessageDict(TypedDict):
    role: str
    content: str


class ChatPromptClient(BasePromptClient, Protocol):
    def compile(self, **kwargs: Any) -> list[ChatMessageDict]: ...


PromptClient = Union[TextPromptClient, ChatPromptClient]


class StatefulClient(Protocol):
    id: str
    trace_id: str

    def generation(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        start_time: dt.datetime | None = None,
        end_time: dt.datetime | None = None,
        metadata: Any | None = None,
        level: SpanLevel | None = None,
        status_message: str | None = None,
        version: str | None = None,
        completion_start_time: dt.datetime | None = None,
        model: str | None = None,
        model_parameters: dict[str, MapValue] | None = None,
        input: Any | None = None,
        output: Any | None = None,
        usage: ModelUsage | None = None,
        prompt: PromptClient | None = None,
        **kwargs: Any,
    ) -> StatefulGenerationClient: ...

    def span(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        start_time: dt.datetime | None = None,
        end_time: dt.datetime | None = None,
        metadata: Any | None = None,
        input: Any | None = None,
        output: Any | None = None,
        level: SpanLevel | None = None,
        status_message: str | None = None,
        version: str | None = None,
        **kwargs: Any,
    ) -> StatefulSpanClient: ...

    @overload
    def score(
        self,
        *,
        id: str | None = None,
        name: str,
        value: float,
        data_type: Literal["NUMERIC", "BOOLEAN"] | None = None,
        comment: str | None = None,
        config_id: str | None = None,
        **kwargs: Any,
    ) -> StatefulClient: ...

    @overload
    def score(
        self,
        *,
        id: str | None = None,
        name: str,
        value: str,
        data_type: Literal["CATEGORICAL"],
        comment: str | None = None,
        config_id: str | None = None,
        **kwargs: Any,
    ) -> StatefulClient: ...

    def score(
        self,
        *,
        id: str | None = None,
        name: str,
        value: float | str,
        data_type: ScoreDataType | None = None,
        comment: str | None = None,
        config_id: str | None = None,
        **kwargs: Any,
    ) -> StatefulClient: ...

    def event(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        start_time: dt.datetime | None = None,
        metadata: Any | None = None,
        input: Any | None = None,
        output: Any | None = None,
        level: SpanLevel | None = None,
        status_message: str | None = None,
        version: str | None = None,
        **kwargs: Any,
    ) -> StatefulClient: ...


class StatefulSpanClient(StatefulClient, Protocol):
    def update(
        self,
        *,
        name: str | None = None,
        start_time: dt.datetime | None = None,
        end_time: dt.datetime | None = None,
        metadata: Any | None = None,
        input: Any | None = None,
        output: Any | None = None,
        level: SpanLevel | None = None,
        status_message: str | None = None,
        version: str | None = None,
        **kwargs: Any,
    ) -> StatefulSpanClient: ...

    def end(
        self,
        *,
        name: str | None = None,
        start_time: dt.datetime | None = None,
        end_time: dt.datetime | None = None,
        metadata: Any | None = None,
        input: Any | None = None,
        output: Any | None = None,
        level: SpanLevel | None = None,
        status_message: str | None = None,
        version: str | None = None,
        **kwargs: Any,
    ) -> StatefulSpanClient: ...


class StatefulGenerationClient(StatefulClient, Protocol):
    def update(
        self,
        *,
        name: str | None = None,
        start_time: dt.datetime | None = None,
        end_time: dt.datetime | None = None,
        completion_start_time: dt.datetime | None = None,
        metadata: Any | None = None,
        level: SpanLevel | None = None,
        status_message: str | None = None,
        version: str | None = None,
        model: str | None = None,
        model_parameters: dict[str, MapValue] | None = None,
        input: Any | None = None,
        output: Any | None = None,
        usage: ModelUsage | None = None,
        prompt: PromptClient | None = None,
        **kwargs: Any,
    ) -> StatefulGenerationClient: ...

    def end(
        self,
        *,
        name: str | None = None,
        start_time: dt.datetime | None = None,
        end_time: dt.datetime | None = None,
        completion_start_time: dt.datetime | None = None,
        metadata: Any | None = None,
        level: SpanLevel | None = None,
        status_message: str | None = None,
        version: str | None = None,
        model: str | None = None,
        model_parameters: dict[str, MapValue] | None = None,
        input: Any | None = None,
        output: Any | None = None,
        usage: ModelUsage | None = None,
        prompt: PromptClient | None = None,
        **kwargs: Any,
    ) -> StatefulGenerationClient: ...


class StatefulTraceClient(StatefulClient, Protocol):
    def update(
        self,
        *,
        name: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        version: str | None = None,
        release: str | None = None,
        input: Any | None = None,
        output: Any | None = None,
        metadata: Any | None = None,
        tags: list[str] | None = None,
        public: bool | None = None,
        **kwargs: Any,
    ) -> StatefulTraceClient: ...


class Langfuse(Protocol):
    host: str
    enabled: bool
    base_url: str
    trace_id: str
    release: str | None

    def trace(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        version: str | None = None,
        input: Any | None = None,
        output: Any | None = None,
        metadata: Any | None = None,
        tags: list[str] | None = None,
        timestamp: dt.datetime | None = None,
        public: bool | None = None,
        **kwargs: Any,
    ) -> StatefulTraceClient: ...

    @overload
    def score(
        self,
        *,
        name: str,
        value: float,
        data_type: Literal["NUMERIC", "BOOLEAN"] | None = None,
        trace_id: str | None = None,
        id: str | None = None,
        comment: str | None = None,
        observation_id: str | None = None,
        config_id: str | None = None,
        **kwargs: Any,
    ) -> StatefulClient: ...

    @overload
    def score(
        self,
        *,
        name: str,
        value: str,
        data_type: Literal["CATEGORICAL"],
        trace_id: str | None = None,
        id: str | None = None,
        comment: str | None = None,
        observation_id: str | None = None,
        config_id: str | None = None,
        **kwargs: Any,
    ) -> StatefulClient: ...

    def score(
        self,
        *,
        name: str,
        value: float | str,
        data_type: ScoreDataType | None = None,
        trace_id: str | None = None,
        id: str | None = None,
        comment: str | None = None,
        observation_id: str | None = None,
        config_id: str | None = None,
        **kwargs: Any,
    ) -> StatefulClient: ...

    def span(
        self,
        *,
        id: str | None = None,
        trace_id: str | None = None,
        parent_observation_id: str | None = None,
        name: str | None = None,
        start_time: dt.datetime | None = None,
        end_time: dt.datetime | None = None,
        metadata: Any | None = None,
        level: SpanLevel | None = None,
        status_message: str | None = None,
        input: Any | None = None,
        output: Any | None = None,
        version: str | None = None,
        **kwargs: Any,
    ) -> StatefulSpanClient: ...

    def event(
        self,
        *,
        id: str | None = None,
        trace_id: str | None = None,
        parent_observation_id: str | None = None,
        name: str | None = None,
        start_time: dt.datetime | None = None,
        metadata: Any | None = None,
        input: Any | None = None,
        output: Any | None = None,
        level: SpanLevel | None = None,
        status_message: str | None = None,
        version: str | None = None,
        **kwargs: Any,
    ) -> StatefulSpanClient: ...

    def generation(
        self,
        *,
        id: str | None = None,
        trace_id: str | None = None,
        parent_observation_id: str | None = None,
        name: str | None = None,
        start_time: dt.datetime | None = None,
        end_time: dt.datetime | None = None,
        completion_start_time: dt.datetime | None = None,
        metadata: Any | None = None,
        level: SpanLevel | None = None,
        status_message: str | None = None,
        version: str | None = None,
        model: str | None = None,
        model_parameters: dict[str, MapValue] | None = None,
        input: Any | None = None,
        output: Any | None = None,
        usage: ModelUsage | None = None,
        prompt: PromptClient | None = None,
        **kwargs: Any,
    ) -> StatefulGenerationClient: ...

    def join(self) -> None: ...

    def flush(self) -> None: ...

    def shutdown(self) -> None: ...
