import time

import httpx

from app.providers.base import (
    ModelProvider,
    ProviderChatResponse,
    ProviderError,
    ProviderHealthStatus,
    ProviderModelInfo,
)

_BASE_URL = "https://api.groq.com/openai/v1"

_PRICING: dict[str, dict[str, float]] = {
    "llama-3.3-70b-versatile":    {"input_per_1k": 0.00059, "output_per_1k": 0.00079},
    "llama-3.1-8b-instant":       {"input_per_1k": 0.00005, "output_per_1k": 0.00008},
    "gemma2-9b-it":               {"input_per_1k": 0.00020, "output_per_1k": 0.00020},
    "meta-llama/llama-4-scout-17b-16e-instruct": {"input_per_1k": 0.00011, "output_per_1k": 0.00034},
}

_DEFAULT_PRICING = {"input_per_1k": 0.001, "output_per_1k": 0.001}


class GroqProvider(ModelProvider):

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = httpx.Client(
            base_url=_BASE_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60.0,
        )

    def list_models(self) -> list[ProviderModelInfo]:
        resp = self._client.get("/models")
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [
            ProviderModelInfo(
                id=m["id"],
                name=m["id"],
                context_window=m.get("context_window"),
            )
            for m in data
        ]

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        prices = _PRICING.get(model, _DEFAULT_PRICING)
        return (
            (input_tokens / 1000) * prices["input_per_1k"]
            + (output_tokens / 1000) * prices["output_per_1k"]
        )

    def chat(self, messages: list[dict], model: str) -> ProviderChatResponse:
        resp = self._client.post(
            "/chat/completions",
            json={"model": model, "messages": messages},
        )
        resp.raise_for_status()
        body = resp.json()

        choice = body["choices"][0]
        usage = body.get("usage", {})

        return ProviderChatResponse(
            content=choice["message"]["content"],
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            model=body.get("model", model),
            finish_reason=choice.get("finish_reason", "stop"),
        )

    def stream(self, messages: list[dict], model: str):
        raise NotImplementedError("Streaming not implemented yet.")

    def health_check(self) -> ProviderHealthStatus:
        start = time.time()
        try:
            resp = self._client.get("/models")
            latency = (time.time() - start) * 1000
            return ProviderHealthStatus(
                healthy=resp.status_code == 200,
                latency_ms=round(latency, 1),
                detail=f"status={resp.status_code}",
            )
        except Exception as exc:
            latency = (time.time() - start) * 1000
            return ProviderHealthStatus(
                healthy=False,
                latency_ms=round(latency, 1),
                detail=str(exc),
            )

    def normalize_error(self, error: Exception) -> ProviderError:
        if isinstance(error, httpx.HTTPStatusError):
            code = error.response.status_code
            try:
                detail = error.response.json().get("error", {}).get("message", str(error))
            except Exception:
                detail = str(error)

            if code == 401:
                return ProviderError("auth", 401, detail)
            if code == 429:
                return ProviderError("rate_limit", 429, detail, retryable=True)
            if code == 400:
                return ProviderError("bad_request", 400, detail)
            if code >= 500:
                return ProviderError("server", 502, detail, retryable=True)
            return ProviderError("unknown", code, detail)

        if isinstance(error, httpx.TimeoutException):
            return ProviderError("timeout", 504, str(error), retryable=True)

        return ProviderError("unknown", 500, str(error))
