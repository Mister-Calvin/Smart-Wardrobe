"""Generate structured outfit suggestions with Gemini."""

import json

from pydantic import ValidationError

from ai_models.gemini.gemini_client import (
    GENERATION_MODEL,
    get_gemini_client,
)
from ai_models.gemini.outfit_prompt_gemini import (
    SYSTEM_PROMPT,
)
from ai_models.gemini.outfit_schema_gemini import (
    OutfitSuggestions,
)


def generate_outfits_with_gemini(
    input_data: dict,
    candidates: dict[str, dict],
    allowed_ids: list[int],
) -> OutfitSuggestions:
    """Request three structured outfits from the available candidates."""
    if not isinstance(input_data, dict):
        raise TypeError(
            "input_data muss ein Dictionary sein."
        )

    if not candidates:
        raise ValueError(
            "Es wurden keine Kandidaten übergeben."
        )

    if not allowed_ids:
        raise ValueError(
            "allowed_ids darf nicht leer sein."
        )

    candidate_ids = [
        item["id"]
        for item in candidates.values()
    ]

    if candidate_ids != allowed_ids:
        raise ValueError(
            "Die Kandidaten-IDs stimmen nicht mit "
            "allowed_ids überein."
        )

    payload = {
        "request": input_data,
        "candidates": candidates,
        "allowed_ids": allowed_ids,
    }

    compact_payload = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    client = get_gemini_client()

    interaction = client.interactions.create(
        model=GENERATION_MODEL,
        input=compact_payload,
        system_instruction=SYSTEM_PROMPT,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": (
                OutfitSuggestions.model_json_schema()
            ),
        },
        generation_config={
            "max_output_tokens": 4096,
            "thinking_level": "low",
        },
        store=False,
    )

    response_text = interaction.output_text

    if not response_text:
        status = getattr(
            interaction,
            "status",
            None,
        )

        usage = getattr(
            interaction,
            "usage",
            None,
        )

        raise RuntimeError(
            "Gemini hat keinen Antworttext geliefert. "
            f"Status: {status}; Usage: {usage}"
        )

    try:
        return OutfitSuggestions.model_validate_json(
            response_text
        )

    except ValidationError as error:
        raise RuntimeError(
            "Die Gemini-Antwort entspricht nicht "
            "dem Outfit-Schema. "
            f"Antwort: {response_text}"
        ) from error
