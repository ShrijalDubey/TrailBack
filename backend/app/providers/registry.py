
from app.providers.base import ModelProvider
from app.utils.settings import settings

_instances: dict[str, ModelProvider] = {}


class ProviderNotConfigured(Exception):
    """Raised when a provider slug has no API key or no adapter."""


def get_provider(slug: str) -> ModelProvider:
    if slug in _instances:
        return _instances[slug]

    adapter = _build(slug)
    _instances[slug] = adapter
    return adapter


def _build(slug: str) -> ModelProvider:

    if slug == "groq":
        from app.providers.groq_provider import GroqProvider

        if not settings.GROQ_API_KEY:
            raise ProviderNotConfigured("GROQ_API_KEY is not set.")
        return GroqProvider(api_key=settings.GROQ_API_KEY)

    if slug == "openai":
        from app.providers.openai_provider import OpenAIProvider

        if not settings.OPENAI_API_KEY:
            raise ProviderNotConfigured("OPENAI_API_KEY is not set.")
        return OpenAIProvider(api_key=settings.OPENAI_API_KEY)

    if slug == "anthropic":
        from app.providers.anthropic_provider import AnthropicProvider

        if not settings.ANTHROPIC_API_KEY:
            raise ProviderNotConfigured("ANTHROPIC_API_KEY is not set.")
        return AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)

    raise ProviderNotConfigured(f"No adapter registered for provider slug '{slug}'.")
