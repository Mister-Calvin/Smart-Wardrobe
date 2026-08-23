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
    pass


def normalize_application_provider(
    provider: str,
) -> str:
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