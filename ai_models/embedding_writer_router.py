AVAILABLE_EMBEDDING_PROVIDERS = (
    "gemini",
    "openai",
)


class EmbeddingProviderError(Exception):
    pass


class UnknownEmbeddingProviderError(
    EmbeddingProviderError,
    ValueError,
):
    pass


def normalize_embedding_provider(
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

    if (
        normalized_provider
        not in AVAILABLE_EMBEDDING_PROVIDERS
    ):
        raise UnknownEmbeddingProviderError(
            "Unbekannter Embedding-Provider: "
            f"{provider}. "
            "Verfügbar sind: "
            f"{AVAILABLE_EMBEDDING_PROVIDERS}"
        )

    return normalized_provider


def upsert_item_embedding(
    *,
    session,
    item,
    provider: str,
):
    normalized_provider = (
        normalize_embedding_provider(
            provider
        )
    )

    if normalized_provider == "gemini":
        from ai_models.gemini.item_embedding_writer_gemini import (
            upsert_gemini_item_embedding,
        )

        return upsert_gemini_item_embedding(
            session=session,
            item=item,
        )

    if normalized_provider == "openai":
        from ai_models.openai.item_embedding_writer_openai import (
            upsert_openai_item_embedding,
        )

        return upsert_openai_item_embedding(
            session=session,
            item=item,
        )

    raise UnknownEmbeddingProviderError(
        "Nicht unterstützter "
        "Embedding-Provider: "
        f"{normalized_provider}"
    )