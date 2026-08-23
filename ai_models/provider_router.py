AVAILABLE_AI_PROVIDERS = (
    "gemini",
    "openai",
)


class AIProviderError(Exception):
    pass


class UnknownAIProviderError(
    AIProviderError,
    ValueError,
):
    pass


class AIProviderRequestError(AIProviderError):
    pass


class AIProviderHallucinationError(AIProviderError):
    pass


class AIProviderGenerationError(AIProviderError):
    pass


def normalize_ai_provider(
    provider: str,
) -> str:
    if not isinstance(provider, str):
        raise TypeError(
            "provider muss ein String sein."
        )

    normalized_provider = (
        provider
        .strip()
        .casefold()
    )

    if normalized_provider not in AVAILABLE_AI_PROVIDERS:
        raise UnknownAIProviderError(
            f"Unbekannter AI-Provider: {provider}. "
            f"Erlaubt sind: {AVAILABLE_AI_PROVIDERS}"
        )

    return normalized_provider


def build_outfit_with_gemini_provider(
    payload: dict,
    filtered_ids: list[int] | None,
) -> str:
    from ai_models.gemini.main_gemini import (
        build_outfit_with_gemini,
    )
    from ai_models.gemini.outfit_retry_gemini import (
        GeminiHallucinationError,
    )

    try:
        return build_outfit_with_gemini(
            payload=payload,
            filtered_ids=filtered_ids,
        )

    except GeminiHallucinationError as error:
        raise AIProviderHallucinationError(
            str(error)
        ) from error

    except ValueError as error:
        raise AIProviderRequestError(
            str(error)
        ) from error

    except RuntimeError as error:
        raise AIProviderGenerationError(
            str(error)
        ) from error


def build_outfit_with_openai_provider(
    payload: dict,
    filtered_ids: list[int] | None,
) -> str:
    try:
        from ai_models.openai.main import (
            BuildOutfitError,
            HallucinationError,
            build_outfit,
        )
        from ai_models.openai.openai_model import (
            NotEnoughItemsForOutfitError,
        )

    except Exception as error:
        raise AIProviderGenerationError(
            "OpenAI konnte nicht geladen werden: "
            f"{error}"
        ) from error

    try:
        return build_outfit(
            payload=payload,
            filtered_ids=filtered_ids,
        )

    except NotEnoughItemsForOutfitError as error:
        raise AIProviderRequestError(
            str(error)
        ) from error

    except HallucinationError as error:
        raise AIProviderHallucinationError(
            str(error)
        ) from error

    except BuildOutfitError as error:
        raise AIProviderGenerationError(
            str(error)
        ) from error


def build_outfit_with_provider(
    provider: str,
    payload: dict,
    filtered_ids: list[int] | None = None,
) -> str:
    normalized_provider = normalize_ai_provider(
        provider
    )

    if normalized_provider == "gemini":
        return build_outfit_with_gemini_provider(
            payload=payload,
            filtered_ids=filtered_ids,
        )

    if normalized_provider == "openai":
        return build_outfit_with_openai_provider(
            payload=payload,
            filtered_ids=filtered_ids,
        )

    raise UnknownAIProviderError(
        f"Nicht unterstützter Provider: "
        f"{normalized_provider}"
    )