"""Expose the public entry point for Gemini outfit generation."""

from ai_models.gemini.outfit_pipeline_gemini import (
    create_gemini_outfit_result,
)
from ai_models.gemini.outfit_answer_gemini import (
    build_gemini_answer_text,
)


def build_outfit_with_gemini(
    payload: dict,
    filtered_ids: list[int] | None = None,
    search_limit: int | None = None,
    max_generation_tries: int = 3,
    *,
    retrieval_limit: int = 100,
    candidate_limit: int = 20,
) -> str:
    """Run the Gemini pipeline and return its readable German response."""
    result = create_gemini_outfit_result(
        input_data=payload,
        filtered_ids=filtered_ids,
        search_limit=search_limit,
        max_generation_tries=max_generation_tries,
        retrieval_limit=retrieval_limit,
        candidate_limit=candidate_limit,
    )

    return build_gemini_answer_text(
        result
    )