import time

import httpx

from app.providers.base import (
    ModelProvider,
    ProviderChatResponse,
    ProviderError,
    ProviderHealthStatus,
    ProviderModelInfo,
)

_BASE_URL = "https://api.anthropic.com/v1"
_ANTHROPIC_VERSION = "2023-06-01"

_PRICING: dict[str, dict[str, float]] = {
    "claude-3-7-sonnet-20250219": {"input_per_1k": 0.00300, "output_per_1k": 0.01500},
    "claude-3-5-sonnet-20241022": {"input_per_1k": 0.00300, "output_per_1k": 0.01500},
    "claude-3-5-haiku-20241022":  {"input_per_1k": 0.00080, "output_per_1k": 0.00400},
    "claude-3-opus-20240229":     {"input_per_1k": 0.01500, "output_per_1k": 0.07500},
    "claude-3-haiku-20240307":    {"input_per_1k": 0.00025, "output_per_1k": 0.00125},
}

_DEFAULT_PRICING = {"input_per_1k": 0.00300, "output_per_1k": 0.01500}


class AnthropicProvider(ModelProvider):

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = httpx.Client(
            base_url=_BASE_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": _ANTHROPIC_VERSION,
                "content-type": "application/json",
            },
            timeout=120.0,
        )

    def list_models(self) -> list[ProviderModelInfo]:
        try:
            resp = self._client.get("/models")
            resp.raise_for_status()
            data = resp.json().get("data", [])
            return [
                ProviderModelInfo(
                    id=m["id"],
                    name=m.get("display_name", m["id"]),
                    context_window=None,
                )
                for m in data
            ]
        except Exception:
            return [
                ProviderModelInfo(id=model_id, name=model_id, context_window=200000)
                for model_id in _PRICING.keys()
            ]

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        prices = _PRICING.get(model)
        if prices is None:
            if "haiku" in model:
                prices = {"input_per_1k": 0.00080, "output_per_1k": 0.00400}
            elif "opus" in model:
                prices = {"input_per_1k": 0.01500, "output_per_1k": 0.07500}
            else:
                prices = _DEFAULT_PRICING

        return (
            (input_tokens / 1000) * prices["input_per_1k"]
            + (output_tokens / 1000) * prices["output_per_1k"]
        )

    def chat(self, messages: list[dict], model: str) -> ProviderChatResponse:
        system_parts = [m["content"] for m in messages if m.get("role") == "system"]
        system_prompt = "\n\n".join(system_parts) if system_parts else None

        filtered_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m.get("role") in ("user", "assistant")
        ]

        payload: dict = {
            "model": model,
            "messages": filtered_messages,
            "max_tokens": 4096,
        }
        if system_prompt:
            payload["system"] = system_prompt

        resp = self._client.post("/messages", json=payload)
        resp.raise_for_status()
        body = resp.json()

        text_parts = [
            block.get("text", "")
            for block in body.get("content", [])
            if block.get("type") == "text"
        ]
        content = "".join(text_parts)
        usage = body.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = input_tokens + output_tokens

        return ProviderChatResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            model=body.get("model", model),
            finish_reason=body.get("stop_reason", "stop"),
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
                err_body = error.response.json().get("error", {})
                detail = err_body.get("message", str(error))
                err_type = err_body.get("type", "")
            except Exception:
                detail = str(error)
                err_type = ""

            if code in (401, 403) or err_type == "authentication_error":
                return ProviderError("auth", code, detail)
            if code == 429 or err_type == "rate_limit_error":
                return ProviderError("rate_limit", 429, detail, retryable=True)
            if code == 400 or err_type == "invalid_request_error":
                return ProviderError("bad_request", 400, detail)
            if code == 404 or err_type == "not_found_error":
                return ProviderError("not_found", 404, detail)
            if code in (503, 529) or err_type == "overloaded_error":
                return ProviderError("server", 503, detail, retryable=True)
            if code >= 500:
                return ProviderError("server", 502, detail, retryable=True)
            return ProviderError("unknown", code, detail)

        if isinstance(error, httpx.TimeoutException):
            return ProviderError("timeout", 504, str(error), retryable=True)

        return ProviderError("unknown", 500, str(error))
