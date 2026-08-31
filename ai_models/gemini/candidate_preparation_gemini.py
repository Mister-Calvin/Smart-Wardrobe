"""Prepare compact wardrobe candidates for Gemini."""

from ai_models.shared.item_category_mapper import (
    get_item_category,
)


def prepare_candidates_for_gemini(
    items: list[dict],
) -> tuple[dict[str, dict], list[int]]:
    """Build a compact candidate mapping and its ordered allowed IDs."""
    if not isinstance(items, list):
        raise TypeError(
            "items muss eine Liste sein."
        )

    if not items:
        raise ValueError(
            "Die Kandidatenliste darf nicht leer sein."
        )

    candidates: dict[str, dict] = {}
    allowed_ids: list[int] = []
    seen_ids: set[int] = set()

    required_fields = {
        "id",
        "name",
        "color",
        "type",
    }

    for position, item in enumerate(
        items,
        start=1,
    ):
        if not isinstance(item, dict):
            raise TypeError(
                f"Kandidat {position} muss "
                "ein Dictionary sein."
            )

        missing_fields = (
            required_fields - item.keys()
        )

        if missing_fields:
            raise ValueError(
                f"Kandidat {position} enthält nicht "
                "alle Pflichtfelder: "
                f"{sorted(missing_fields)}"
            )

        item_id = item["id"]

        if not isinstance(item_id, int):
            raise TypeError(
                f"Die ID von Kandidat {position} "
                "muss eine Ganzzahl sein."
            )

        if item_id in seen_ids:
            raise ValueError(
                "Die Kandidatenliste enthält "
                f"die ID {item_id} mehrfach."
            )

        category = get_item_category(
            item
        )

        if category is None:
            raise ValueError(
                f"Kandidat {position} mit ID "
                f"{item_id} konnte keiner "
                "Outfit-Kategorie zugeordnet werden."
            )

        seen_ids.add(item_id)
        allowed_ids.append(item_id)

        candidates[f"item_{position}"] = {
            "id": item_id,
            "name": item["name"],
            "color": item["color"],
            "category": category,
        }

    return candidates, allowed_ids