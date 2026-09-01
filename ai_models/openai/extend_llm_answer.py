"""Render OpenAI outfit slots with wardrobe item names."""

from data_manager import DataManager


data_manager = DataManager()


slot_labels = {
    "top_id": "Top",
    "bottom_id": "Bottom",
    "shoes_id": "Shoes",
    "headwear_id": "Headwear",
    "outerwear_id": "Outerwear",
    "socks_id": "Socks",
    "bag_id": "Bag",
    "accessory_id": "Accessory",
}
def build_extended_answer_text(result) -> str:
    """Resolve outfit IDs and format the outfits as readable text."""
    lines: list[str] = []

    for idx, outfit in enumerate(result["outfits"], start=1):
        lines.append("=" * 40)
        lines.append(f"Outfit {idx}: {outfit['name']}")
        lines.append(f"How to wear: {outfit['how_to_wear']}")
        lines.append(f"Why: {outfit['rationale']}")
        lines.append("-" * 40)

        slots = outfit["slots"]
        for key, label in slot_labels.items():
            item_id = slots.get(key)
            if not item_id:
                continue

            item = data_manager.get_item_by_id(item_id)
            if not item:
                lines.append(f"{label}: (ID {item_id} nicht gefunden)")
                continue

            lines.append(f"{label}: {item.name}")

        lines.append("")

    return "\n".join(lines).strip()
