"""Coordinate OpenAI outfit generation, retries, and answer rendering."""

from ai_models.openai.openai_model import (
    NotEnoughItemsForOutfitError,
    create_answer,
    create_response,
)
from ai_models.openai.extend_llm_answer import (
    build_extended_answer_text,
)

class BuildOutfitError(Exception):
    """Raised when outfit generation fails after retries."""


class HallucinationError(BuildOutfitError):
    """Raised when the LLM keeps hallucinating ids after retries."""


def build_outfit(payload, filtered_ids=None, max_tries=3):
    """Retry OpenAI generation and render the first accepted outfit response."""
    last_error = None
    last_invalid_reason = None

    for attempt in range(1, max_tries + 1):
        try:
            if filtered_ids is None:
                llm_answer = create_answer(create_response(payload))
            else:
                llm_answer = create_answer(create_response(payload, filtered_ids))


        except NotEnoughItemsForOutfitError:
            raise


        except Exception as e:
            last_error = f"Attempt {attempt}: {type(e).__name__}: {e}"
            continue

        is_valid = llm_answer.get("is_valid") is True
        hallucinated = llm_answer.get("hallucinated_ids") or []

        if is_valid and not hallucinated:
            return build_extended_answer_text(llm_answer)

        last_invalid_reason = (
            f"Attempt {attempt}: is_valid={llm_answer.get('is_valid')} | "
            f"hallucinated_ids={hallucinated}"
        )


    if last_invalid_reason:
        raise HallucinationError(
            f"LLM halluziniert nach {max_tries} Versuchen weiterhin: {last_invalid_reason}"
        )

    if last_error:
        raise BuildOutfitError(
            f"Outfit-Erstellung fehlgeschlagen nach {max_tries} Versuchen: {last_error}"
        )

    raise BuildOutfitError(f"Outfit-Erstellung fehlgeschlagen nach {max_tries} Versuchen (unbekannt).")