"""Attach OpenAI embeddings to wardrobe items in an existing session."""

from models import Wardrobe

from ai_models.openai.item_embedding_openai import (
    item_to_vector,
)


def upsert_openai_item_embedding(
    *,
    session,
    item: Wardrobe,
) -> Wardrobe:
    """Generate an OpenAI embedding and assign it to a flushed item."""
    if session is None:
        raise TypeError(
            "Eine Datenbank-Session "
            "ist erforderlich."
        )

    if not isinstance(item, Wardrobe):
        raise TypeError(
            "item muss ein "
            "Wardrobe-Objekt sein."
        )

    if item.id is None:
        raise ValueError(
            "Das Wardrobe-Item benötigt "
            "vor dem Embedding eine "
            "Datenbank-ID. session.flush() "
            "wurde vermutlich noch nicht "
            "ausgeführt."
        )

    vector = item_to_vector(
        name=item.name,
        description=item.description,
        color=item.color,
        condition=item.condition,
        item_type=item.type,
        score=item.score,
    )

    item.embedding = vector

    return item