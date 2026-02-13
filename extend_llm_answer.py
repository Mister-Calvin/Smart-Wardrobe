import psycopg2
import os
from dotenv import load_dotenv
from openai_model3 import create_answer

load_dotenv()
DB_KEY = os.getenv("POSTGRESQL_KEY_ONLY")


def get_all_ids_list(data: dict) -> list[int]:
    outfits = data.get("outfits", [])
    ids_set = set()

    for outfit in outfits:
        slots = outfit.get("slots", {})

        # 1) all_ids nehmen (wenn vorhanden)
        for _id in (slots.get("all_ids") or []):
            if _id:
                ids_set.add(int(_id))

        # 2) Safety: Slot-IDs auch einsammeln (falls all_ids fehlt/unsauber ist)
        for key in [
            "top_id", "bottom_id", "shoes_id", "headwear_id",
            "outerwear_id", "socks_id", "bag_id", "accessory_id",
        ]:
            v = slots.get(key)
            if v:
                ids_set.add(int(v))

    return sorted(ids_set)


def get_db_by_id(ids: list[int]) -> dict[int, dict]:
    if not ids:
        return {}

    conn = psycopg2.connect(f"dbname=wardrobe user=postgres password={DB_KEY}")
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, description, color, condition, type, score
        FROM wardrobe
        WHERE id = ANY (%s);
        """,
        (ids,),
    )

    results = cur.fetchall()

    items_by_id: dict[int, dict] = {}
    for row in results:
        item_id = row[0]
        items_by_id[item_id] = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "color": row[3],
            "condition": row[4],
            "type": row[5],
            "score": row[6],
        }

    cur.close()
    conn.close()

    return items_by_id


def extended_answer(data: dict, items_by_id: dict[int, dict]) -> dict:
    """Baut die große Antwort zusammen und gibt sie JSON-serializable zurück (kein print)."""

    outfits = data.get("outfits", [])

    def name_for(item_id):
        if not item_id:  # behandelt auch 0 wie None
            return None
        item = items_by_id.get(int(item_id))
        return item.get("name") if item else None

    lines: list[str] = []
    lines.append(f"Nach deinen Angaben habe ich folgende {len(outfits)} Outfits erstellt:\n")

    slot_order = [
        ("Top", "top_id"),
        ("Bottom", "bottom_id"),
        ("Shoes", "shoes_id"),
        ("Outerwear", "outerwear_id"),
        ("Headwear", "headwear_id"),
        ("Socks", "socks_id"),
        ("Bag", "bag_id"),
        ("Accessory", "accessory_id"),
    ]

    for i, outfit in enumerate(outfits, start=1):
        slots = outfit.get("slots", {})

        lines.append(f"{i}) {outfit.get('name', 'Outfit')}")

        for label, key in slot_order:
            item_id = slots.get(key)
            item_name = name_for(item_id)

            if not item_id or item_name is None:
                lines.append(f"- {label}: None")
            else:
                lines.append(f"- {label}: {item_name}")

        lines.append("")
        lines.append(f"Wie trage ich das Outfit? {outfit.get('how_to_wear', '')}")
        lines.append(f"Warum passt das Outfit? {outfit.get('rationale', '')}")
        lines.append("-" * 40)

    text = "\n".join(lines)

    with open("extend_llm_answer.txt", "w") as f:
        f.write(text)


    return text
