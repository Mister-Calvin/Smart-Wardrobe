"""Store Gemini item embeddings in their provider-specific table."""

from models import Wardrobe

from ai_models.gemini.gemini_client import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
)
from ai_models.gemini.gemini_embedding_model import (
    GeminiWardrobeEmbedding,
)
from ai_models.gemini.item_embedding_gemini import (
    item_to_vector,
)


def upsert_gemini_item_embedding(
    *,
    session,
    item: Wardrobe,
) -> GeminiWardrobeEmbedding:
    """Create or update the configured Gemini embedding for an item."""
    if not isinstance(item, Wardrobe):
        raise TypeError(
            "item muss ein Wardrobe-Objekt sein."
        )

    if item.id is None:
        raise ValueError(
            "Das Wardrobe-Item benötigt vor dem "
            "Embedding eine Datenbank-ID. "
            "session.flush() wurde vermutlich "
            "noch nicht ausgeführt."
        )

    vector = item_to_vector(
        name=item.name,
        description=item.description,
        color=item.color,
        condition=item.condition,
        item_type=item.type,
        score=item.score,
    )

    embedding_record = (
        session.query(
            GeminiWardrobeEmbedding
        )
        .filter(
            GeminiWardrobeEmbedding.wardrobe_id
            == item.id,
            GeminiWardrobeEmbedding.model
            == EMBEDDING_MODEL,
            GeminiWardrobeEmbedding.dimensions
            == EMBEDDING_DIMENSIONS,
        )
        .one_or_none()
    )

    if embedding_record is None:
        embedding_record = (
            GeminiWardrobeEmbedding(
                wardrobe_id=item.id,
                model=EMBEDDING_MODEL,
                dimensions=(
                    EMBEDDING_DIMENSIONS
                ),
                embedding=vector,
            )
        )

        session.add(
            embedding_record
        )

    else:
        embedding_record.embedding = vector

    return embedding_record