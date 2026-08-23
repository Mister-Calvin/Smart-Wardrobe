from ai_models.gemini.outfit_schema_gemini import (
    OutfitSuggestions,
)


SLOT_ALLOWED_CATEGORIES = {
    "top_id": {
        "top",
        "dress",
    },
    "bottom_id": {
        "bottom",
    },
    "shoes_id": {
        "shoes",
    },
    "headwear_id": {
        "headwear",
    },
    "outerwear_id": {
        "outerwear",
    },
    "socks_id": {
        "socks",
    },
    "bag_id": {
        "bag",
    },
    "accessory_id": {
        "accessory",
    },
}


SLOT_FIELDS = tuple(
    SLOT_ALLOWED_CATEGORIES
)


VALID_CATEGORIES = set().union(
    *SLOT_ALLOWED_CATEGORIES.values()
)


def build_candidate_category_map(
    candidates: dict[str, dict],
    allowed_ids: list[int],
) -> dict[int, str]:
    if not isinstance(candidates, dict):
        raise TypeError(
            "candidates muss ein Dictionary sein."
        )

    if not candidates:
        raise ValueError(
            "candidates darf nicht leer sein."
        )

    category_by_id: dict[int, str] = {}
    candidate_ids: list[int] = []

    for candidate_key, candidate in candidates.items():
        if not isinstance(candidate, dict):
            raise TypeError(
                f"{candidate_key} muss ein "
                "Dictionary sein."
            )

        item_id = candidate.get("id")
        category = candidate.get("category")

        if not isinstance(item_id, int):
            raise TypeError(
                f"{candidate_key} benötigt "
                "eine ganzzahlige ID."
            )

        if item_id in category_by_id:
            raise ValueError(
                f"Die Kandidaten-ID {item_id} "
                "kommt mehrfach vor."
            )

        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"{candidate_key} hat die unbekannte "
                f"Kategorie {category!r}."
            )

        candidate_ids.append(item_id)
        category_by_id[item_id] = category

    if candidate_ids != allowed_ids:
        raise ValueError(
            "Die Kandidaten-IDs stimmen nicht "
            "mit allowed_ids überein."
        )

    return category_by_id


def validate_gemini_outfit_ids(
    outfits: OutfitSuggestions,
    allowed_ids: list[int],
    candidates: dict[str, dict],
    required_unique_bases: int = 3,
) -> dict:
    if not isinstance(outfits, OutfitSuggestions):
        raise TypeError(
            "outfits muss ein "
            "OutfitSuggestions-Modell sein."
        )

    if not allowed_ids:
        raise ValueError(
            "allowed_ids darf nicht leer sein."
        )

    if (
        isinstance(required_unique_bases, bool)
        or not isinstance(
            required_unique_bases,
            int,
        )
    ):
        raise TypeError(
            "required_unique_bases muss "
            "eine Ganzzahl sein."
        )

    if required_unique_bases <= 0:
        raise ValueError(
            "required_unique_bases muss "
            "größer als 0 sein."
        )

    category_by_id = build_candidate_category_map(
        candidates=candidates,
        allowed_ids=allowed_ids,
    )

    allowed_id_set = set(allowed_ids)
    outfits_data = outfits.model_dump()

    ids_from_answer: list[int] = []
    category_errors: list[str] = []
    structure_errors: list[str] = []

    valid_base_combinations: set[
        tuple[int, int | None]
    ] = set()

    for outfit_position, outfit in enumerate(
        outfits_data["outfits"],
        start=1,
    ):
        slots = outfit["slots"]
        outfit_ids: list[int] = []

        for slot_name in SLOT_FIELDS:
            item_id = slots.get(slot_name)

            if item_id is None:
                continue

            outfit_ids.append(item_id)
            ids_from_answer.append(item_id)

            if item_id not in allowed_id_set:
                continue

            actual_category = category_by_id[
                item_id
            ]

            expected_categories = (
                SLOT_ALLOWED_CATEGORIES[
                    slot_name
                ]
            )

            if (
                actual_category
                not in expected_categories
            ):
                expected_text = ", ".join(
                    sorted(expected_categories)
                )

                category_errors.append(
                    f"Outfit {outfit_position}: "
                    f"{slot_name}={item_id} hat "
                    f"die Kategorie "
                    f"{actual_category!r}; erwartet "
                    f"wird {expected_text!r}."
                )

        slots["all_ids"] = outfit_ids

        top_id = slots["top_id"]
        bottom_id = slots["bottom_id"]

        top_category = category_by_id.get(
            top_id
        )

        if top_category == "dress":
            if bottom_id is not None:
                structure_errors.append(
                    f"Outfit {outfit_position}: "
                    "Ein Kleid in top_id verlangt "
                    "bottom_id=null."
                )
            else:
                valid_base_combinations.add(
                    (top_id, None)
                )

        elif top_category == "top":
            if bottom_id is None:
                structure_errors.append(
                    f"Outfit {outfit_position}: "
                    "Ein normales Oberteil verlangt "
                    "eine bottom_id."
                )

            elif (
                category_by_id.get(bottom_id)
                == "bottom"
            ):
                valid_base_combinations.add(
                    (top_id, bottom_id)
                )

    hallucinated_ids = sorted(
        set(ids_from_answer) - allowed_id_set
    )

    uniqueness_errors: list[str] = []

    unique_base_combination_count = len(
        valid_base_combinations
    )

    if (
        unique_base_combination_count
        < required_unique_bases
    ):
        uniqueness_errors.append(
            f"Nur {unique_base_combination_count} "
            f"von {required_unique_bases} "
            "erforderlichen Basiskombinationen "
            "sind gültig und eindeutig."
        )

    validation_errors: list[str] = []

    if hallucinated_ids:
        validation_errors.append(
            "Nicht erlaubte IDs: "
            f"{hallucinated_ids}"
        )

    validation_errors.extend(
        category_errors
    )
    validation_errors.extend(
        structure_errors
    )
    validation_errors.extend(
        uniqueness_errors
    )

    return {
        "outfits": outfits_data["outfits"],
        "allowed_ids": allowed_ids,
        "ids_from_answer": sorted(
            set(ids_from_answer)
        ),
        "hallucinated_ids": hallucinated_ids,
        "category_errors": category_errors,
        "structure_errors": structure_errors,
        "uniqueness_errors": uniqueness_errors,
        "unique_base_combination_count": (
            unique_base_combination_count
        ),
        "required_unique_base_combinations": (
            required_unique_bases
        ),
        "validation_errors": validation_errors,
        "is_valid": not validation_errors,
    }