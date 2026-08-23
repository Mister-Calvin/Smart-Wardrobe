from models import Session, Wardrobe

from ai_models.gemini.gemini_client import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
)
from ai_models.gemini.gemini_embedding_model import (
    GeminiWardrobeEmbedding,
)

def count_searchable_gemini_items(
    filtered_ids: list[int] | None = None,
) -> int:
    if filtered_ids is not None and not filtered_ids:
        return 0

    session = Session()

    try:
        query = (
            session.query(
                GeminiWardrobeEmbedding.id
            )
            .filter(
                GeminiWardrobeEmbedding.model
                == EMBEDDING_MODEL,
                GeminiWardrobeEmbedding.dimensions
                == EMBEDDING_DIMENSIONS,
            )
        )

        if filtered_ids is not None:
            query = query.filter(
                GeminiWardrobeEmbedding
                .wardrobe_id
                .in_(filtered_ids)
            )

        return query.count()

    finally:
        session.close()


def search_similar_items(
    input_vector: list[float],
    filtered_ids: list[int] | None = None,
    limit: int = 30,
) -> list[dict]:
    if len(input_vector) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Der Query-Vektor hat {len(input_vector)} Dimensionen. "
            f"Erwartet werden {EMBEDDING_DIMENSIONS}."
        )

    if limit <= 0:
        raise ValueError("limit muss größer als 0 sein.")

    if filtered_ids is not None and not filtered_ids:
        return []

    session = Session()

    try:
        distance = (
            GeminiWardrobeEmbedding.embedding
            .l2_distance(input_vector)
            .label("distance")
        )

        query = (
            session.query(
                Wardrobe,
                distance,
            )
            .join(
                GeminiWardrobeEmbedding,
                GeminiWardrobeEmbedding.wardrobe_id
                == Wardrobe.id,
            )
            .filter(
                GeminiWardrobeEmbedding.model
                == EMBEDDING_MODEL,
                GeminiWardrobeEmbedding.dimensions
                == EMBEDDING_DIMENSIONS,
            )
        )

        if filtered_ids is not None:
            query = query.filter(
                Wardrobe.id.in_(filtered_ids)
            )

        rows = (
            query
            .order_by(distance.asc(), Wardrobe.id.asc(),)
            .limit(limit)
            .all()
        )

        results = []

        for item, item_distance in rows:
            results.append(
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "color": item.color,
                    "condition": item.condition,
                    "type": item.type,
                    "score": item.score,
                    "distance": float(item_distance),
                }
            )

        return results

    finally:
        session.close()