"""Store and require the selected AI provider in the browser session."""

from ai_models.embedding_writer_router import (
    normalize_embedding_provider,
)
from ai_models.provider_router import (
    normalize_ai_provider,
)


AI_PROVIDER_SESSION_KEY = (
    "ai_provider"
)


class AIProviderNotSelectedError(
    RuntimeError
):
    """Indicate that an operation requires an AI provider selection."""
    pass


def normalize_application_provider(
    provider: str,
) -> str:
    """Validate a provider used for generation and embeddings."""
    ai_provider = normalize_ai_provider(
        provider
    )

    embedding_provider = (
        normalize_embedding_provider(
            provider
        )
    )

    if ai_provider != embedding_provider:
        raise RuntimeError(
            "Generierungs- und "
            "Embedding-Provider stimmen "
            "nicht überein."
        )

    return ai_provider


def get_selected_ai_provider(
    request,
) -> str | None:
    """Return the valid provider stored in the current session."""
    stored_provider = request.session.get(
        AI_PROVIDER_SESSION_KEY
    )

    if stored_provider is None:
        return None

    try:
        return normalize_application_provider(
            stored_provider
        )

    except (TypeError, ValueError):
        request.session.pop(
            AI_PROVIDER_SESSION_KEY,
            None,
        )

        return None


def set_selected_ai_provider(
    request,
    provider: str,
) -> str:
    """Validate and store the selected provider in the session."""
    selected_provider = (
        normalize_application_provider(
            provider
        )
    )

    request.session[
        AI_PROVIDER_SESSION_KEY
    ] = selected_provider

    return selected_provider


def require_selected_ai_provider(
    request,
) -> str:
    """Return the selected provider or raise when none is available."""
    selected_provider = (
        get_selected_ai_provider(
            request
        )
    )

    if selected_provider is None:
        raise AIProviderNotSelectedError(
            "Bitte wähle zuerst auf der "
            "Landingpage ein KI-Modell aus."
        )

    return selected_provider