"""Build retrieval text and Gemini vectors for wardrobe items."""

from google.genai import types

from ai_models.gemini.gemini_client import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    get_gemini_client,
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
    cleaned_name = str(name or "").strip()
    cleaned_description = str(description or "").strip()
    cleaned_color = str(color or "").strip()
    cleaned_condition = str(condition or "").strip()
    cleaned_type = str(item_type or "").strip()

    if not cleaned_name:
        raise ValueError("Der Name des Kleidungsstücks darf nicht leer sein.")

    if not cleaned_description:
        raise ValueError(
            "Die Beschreibung des Kleidungsstücks darf nicht leer sein."
        )

    return (
        "Task: Represent this wardrobe item for retrieval by outfit requests.\n"
        f"name: {cleaned_name}\n"
        f"description: {cleaned_description}\n"
        f"color: {cleaned_color}\n"
        f"condition: {cleaned_condition}\n"
        f"type: {cleaned_type}\n"
        f"score: {score if score is not None else ''}"
    )


def item_to_vector(
    name: str,
    description: str,
    color: str,
    condition: str,
    item_type: str | None,
    score: int | None,
) -> list[float]:
    """Generate and validate a Gemini embedding for one wardrobe item."""
    item_text = build_item_text(
        name=name,
        description=description,
        color=color,
        condition=condition,
        item_type=item_type,
        score=score,
    )

    client = get_gemini_client()

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=item_text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )

    if not result.embeddings:
        raise RuntimeError("Gemini hat kein Item-Embedding zurückgegeben.")

    values = result.embeddings[0].values

    if values is None:
        raise RuntimeError("Das Item-Embedding enthält keine Werte.")

    item_vector = list(values)

    if len(item_vector) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Falsche Embedding-Dimension: "
            f"{len(item_vector)} statt {EMBEDDING_DIMENSIONS}"
        )

    return item_vector