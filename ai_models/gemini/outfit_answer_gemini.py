from models import Session, Wardrobe


SLOT_LABELS = {
    "top_id": "Oberteil",
    "bottom_id": "Unterteil",
    "shoes_id": "Schuhe",
    "headwear_id": "Kopfbedeckung",
    "outerwear_id": "Jacke oder Mantel",
    "socks_id": "Socken",
    "bag_id": "Tasche",
    "accessory_id": "Accessoire",
}


def build_gemini_answer_text(
    result: dict,
) -> str:
    if not isinstance(result, dict):
        raise TypeError(
            "result muss ein Dictionary sein."
        )

    if result.get("is_valid") is not True:
        raise ValueError(
            "Aus einer ungültigen Gemini-Antwort "
            "kann kein Outfittext erstellt werden."
        )

    outfits = result.get("outfits")

    if not isinstance(outfits, list) or not outfits:
        raise ValueError(
            "Die Gemini-Antwort enthält keine Outfits."
        )

    used_ids: set[int] = set()

    for outfit in outfits:
        slots = outfit.get("slots") or {}

        for slot_name in SLOT_LABELS:
            item_id = slots.get(slot_name)

            if item_id is not None:
                used_ids.add(item_id)

    if not used_ids:
        raise ValueError(
            "Die Outfits enthalten keine Kleidungs-IDs."
        )

    session = Session()

    try:
        items = (
            session.query(Wardrobe)
            .filter(Wardrobe.id.in_(used_ids))
            .all()
        )

        item_names = {
            item.id: item.name
            for item in items
        }

    finally:
        session.close()

    lines: list[str] = []

    for position, outfit in enumerate(
        outfits,
        start=1,
    ):
        lines.append("=" * 40)
        lines.append(
            f"Outfit {position}: {outfit['name']}"
        )
        lines.append(
            f"So tragen: {outfit['how_to_wear']}"
        )
        lines.append(
            f"Warum: {outfit['rationale']}"
        )
        lines.append("-" * 40)

        slots = outfit["slots"]

        for slot_name, label in SLOT_LABELS.items():
            item_id = slots.get(slot_name)

            if item_id is None:
                continue

            item_name = item_names.get(item_id)

            if item_name is None:
                lines.append(
                    f"{label}: ID {item_id} "
                    "nicht in der Datenbank gefunden"
                )
                continue

            lines.append(
                f"{label}: {item_name}"
            )

        lines.append("")

    return "\n".join(lines).strip()