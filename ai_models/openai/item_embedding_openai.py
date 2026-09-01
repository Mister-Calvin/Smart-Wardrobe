"""Build and generate OpenAI embeddings for wardrobe items."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings


load_dotenv()


OPENAI_EMBEDDING_MODEL = (
    "text-embedding-3-small"
)

OPENAI_EMBEDDING_DIMENSIONS = 1536


@lru_cache(maxsize=1)
def get_openai_embedding_client(
) -> OpenAIEmbeddings:
    """Return the cached OpenAI embedding client."""
    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY fehlt. "
            "Bitte in der .env konfigurieren."
        )

    return OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        dimensions=(
            OPENAI_EMBEDDING_DIMENSIONS
        ),
        api_key=api_key,
    )


def build_item_text(
    name: str,
    description: str,
    color: str,
    condition: str,
    item_type: str | None,
    score: int | None,
) -> str:
    """Convert wardrobe attributes into the text used for embedding."""
    return (
        f"name: {name}\n"
        f"description: {description}\n"
        f"color: {color}\n"
        f"condition: {condition}\n"
        f"type: {item_type}\n"
        f"score: {score}"
    )


def item_to_vector(
    name: str,
    description: str,
    color: str,
    condition: str,
    item_type: str | None,
    score: int | None,
) -> list[float]:
    """Generate and validate an OpenAI embedding for one wardrobe item."""
    item_text = build_item_text(
        name=name,
        description=description,
        color=color,
        condition=condition,
        item_type=item_type,
        score=score,
    )

    client = (
        get_openai_embedding_client()
    )

    vector = client.embed_query(
        item_text
    )

    item_vector = list(vector)

    if (
        len(item_vector)
        != OPENAI_EMBEDDING_DIMENSIONS
    ):
        raise RuntimeError(
            "Falsche OpenAI-"
            "Embedding-Dimension: "
            f"{len(item_vector)} statt "
            f"{OPENAI_EMBEDDING_DIMENSIONS}"
        )

    return item_vector