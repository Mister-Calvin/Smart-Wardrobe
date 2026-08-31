"""Build outfit request text and Gemini query embeddings."""

from google.genai import types

from ai_models.gemini.gemini_client import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    get_gemini_client,
)


def build_query_text(payload: dict) -> str:
    """Convert an outfit request and context into retrieval text."""
    if not isinstance(payload, dict):
        raise TypeError("payload muss ein Dictionary sein.")

    question = str(payload.get("user_input") or "").strip()

    if not question:
        raise ValueError("user_input darf nicht leer sein.")

    context = payload.get("context") or {}

    if not isinstance(context, dict):
        raise TypeError("payload['context'] muss ein Dictionary sein.")

    styling_hints = context.get("styling_hints") or []

    if isinstance(styling_hints, list):
        styling_hints_text = ", ".join(
            str(hint) for hint in styling_hints
        )
    else:
        styling_hints_text = str(styling_hints)

    return (
        "Task: Represent this outfit request for retrieving matching "
        "wardrobe items.\n"
        f"question: {question}\n"
        f"event: {context.get('event_input') or ''}\n"
        f"location: {context.get('location_input') or ''}\n"
        f"season: {context.get('season_input') or ''}\n"
        f"weather: {context.get('weather_input') or ''}\n"
        f"mood: {context.get('mood_input') or ''}\n"
        f"styling hints: {styling_hints_text}"
    )


def input_to_vector(payload: dict) -> list[float]:
    """Generate and validate a Gemini embedding for an outfit request."""
    query_text = build_query_text(payload)
    client = get_gemini_client()

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query_text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )

    if not result.embeddings:
        raise RuntimeError("Gemini hat kein Query-Embedding zurückgegeben.")

    values = result.embeddings[0].values

    if values is None:
        raise RuntimeError("Das Query-Embedding enthält keine Werte.")

    query_vector = list(values)

    if len(query_vector) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Falsche Embedding-Dimension: "
            f"{len(query_vector)} statt {EMBEDDING_DIMENSIONS}"
        )

    return query_vector