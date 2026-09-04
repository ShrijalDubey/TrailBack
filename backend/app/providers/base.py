
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ProviderModelInfo:
    id: str
    name: str
    context_window: int | None = None


@dataclass
class ProviderChatResponse:
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    finish_reason: str = "stop"


@dataclass
class ProviderHealthStatus:
    healthy: bool
    latency_ms: float = 0.0
    detail: str = ""


@dataclass
class ProviderError:
    category: str        
    http_status: int
    message: str
    retryable: bool = False


class ModelProvider(ABC):

    @abstractmethod
    def list_models(self) -> list[ProviderModelInfo]:
        """Return models available from this provider."""

    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost in USD for the given token counts."""

    @abstractmethod
    def chat(self, messages: list[dict], model: str) -> ProviderChatResponse:
        """Synchronous chat completion — send messages, get response."""

    @abstractmethod
    def stream(self, messages: list[dict], model: str):
        """Streaming chat completion (future use). Can raise NotImplementedError for now."""

    @abstractmethod
    def health_check(self) -> ProviderHealthStatus:
        """Quick check whether the provider is reachable and responding."""

    @abstractmethod
    def normalize_error(self, error: Exception) -> ProviderError:
        """Convert a provider-specific exception into a ProviderError."""
