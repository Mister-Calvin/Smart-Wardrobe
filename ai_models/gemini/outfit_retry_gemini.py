"""Retry Gemini outfit generation until validation succeeds."""

from ai_models.gemini.outfit_generation_gemini import (
    generate_outfits_with_gemini,
)
from ai_models.gemini.outfit_response_validation_gemini import (
    validate_gemini_outfit_ids,
)


class GeminiHallucinationError(RuntimeError):
    """Indicate that Gemini exhausted its attempts without a valid response."""
    pass


def generate_valid_gemini_outfit_result(
    input_data: dict,
    candidates: dict[str, dict],
    allowed_ids: list[int],
    max_tries: int = 3,
) -> dict:
    """Generate and validate outfits until one attempt succeeds."""
    if max_tries <= 0:
        raise ValueError(
            "max_tries muss größer als 0 sein."
        )

    last_validation_errors: list[str] = []

    for attempt in range(
        1,
        max_tries + 1,
    ):
        outfits = generate_outfits_with_gemini(
            input_data=input_data,
            candidates=candidates,
            allowed_ids=allowed_ids,
        )

        result = validate_gemini_outfit_ids(
            outfits=outfits,
            allowed_ids=allowed_ids,
            candidates=candidates,
            required_unique_bases=3,
        )

        if result["is_valid"]:
            result["generation_attempts"] = (
                attempt
            )

            return result

        last_validation_errors = result[
            "validation_errors"
        ]

    raise GeminiHallucinationError(
        "Gemini hat nach "
        f"{max_tries} Versuchen weiterhin "
        "keine gültige Outfit-Antwort "
        "erzeugt. Fehler: "
        f"{last_validation_errors}"
    )