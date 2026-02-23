from data_manager import DataManager
import json

#with open("llm_answer.json", "r", encoding="utf-8") as f:
 #   result = json.load(f)

data_manager = DataManager()

# Alle Outfits durchgehen und Slots als Namen ausgeben (nur wenn befüllt)
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

        lines.append("")  # Leerzeile zwischen Outfits

    return "\n".join(lines).strip()

#print(build_extended_answer_text())