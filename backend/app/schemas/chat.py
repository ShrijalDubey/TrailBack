from uuid import UUID

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class RouteConstraints(BaseModel):

    budget_usd: float | None = Field(default=None, ge=0)
    max_latency_ms: int | None = Field(default=None, ge=0)
    min_quality: float | None = Field(default=None, ge=0, le=1)
    policy: str = "balanced" 


class ChatCompletionRequest(BaseModel):
    model: str = "auto"  
    messages: list[ChatMessage]
    route: RouteConstraints | None = None


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class RoutingMeta(BaseModel):
    estimated_cost: float
    predicted_quality: float | None = None
    predicted_latency_ms: float | None = None
    fallback_used: bool = False
    fallback_reason: str | None = None
    fallbacks_attempted: list[str] = Field(default_factory=list)


class ResponseMessage(BaseModel):
    role: str = "assistant"
    content: str


class Choice(BaseModel):
    index: int = 0
    message: ResponseMessage
    finish_reason: str = "stop"


class ChatCompletionResponse(BaseModel):
    id: UUID
    model: str
    provider: str
    choices: list[Choice]
    usage: Usage
    routing: RoutingMeta