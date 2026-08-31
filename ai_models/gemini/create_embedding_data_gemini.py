"""Backfill missing Gemini embeddings for wardrobe items."""

from models import Session, Wardrobe

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


def create_missing_gemini_embeddings(
    limit: int | None = None,
) -> int:
    """Create and store missing Gemini embeddings in resumable steps."""
    if limit is not None and limit <= 0:
        raise ValueError("limit muss größer als 0 sein.")

    session = Session()

    try:
        existing_ids = {
            wardrobe_id
            for (wardrobe_id,) in (
                session.query(
                    GeminiWardrobeEmbedding.wardrobe_id
                )
                .filter(
                    GeminiWardrobeEmbedding.model
                    == EMBEDDING_MODEL,
                    GeminiWardrobeEmbedding.dimensions
                    == EMBEDDING_DIMENSIONS,
                )
                .all()
            )
        }

        items_query = (
            session.query(Wardrobe)
            .order_by(Wardrobe.id.asc())
        )

        if existing_ids:
            items_query = items_query.filter(
                Wardrobe.id.notin_(existing_ids)
            )

        if limit is not None:
            items_query = items_query.limit(limit)

        items = items_query.all()

        if not items:
            print(
                "Alle Kleidungsstücke besitzen bereits "
                "ein passendes Gemini-Embedding."
            )
            return 0

        created_count = 0
        total = len(items)

        for position, item in enumerate(items, start=1):
            print(
                f"[{position}/{total}] "
                f"Erzeuge Gemini-Embedding für "
                f"ID {item.id}: {item.name}"
            )

            vector = item_to_vector(
                name=item.name,
                description=item.description,
                color=item.color,
                condition=item.condition,
                item_type=item.type,
                score=item.score,
            )

            embedding_record = GeminiWardrobeEmbedding(
                wardrobe_id=item.id,
                model=EMBEDDING_MODEL,
                dimensions=EMBEDDING_DIMENSIONS,
                embedding=vector,
            )

            session.add(embedding_record)




            session.commit()

            created_count += 1

        return created_count

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()