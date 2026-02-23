import psycopg2
import os
from dotenv import load_dotenv
from db_filters import filter_db_dynamic
from typing import Optional, Sequence
import json



load_dotenv()
DB_KEY = os.getenv("POSTGRESQL_KEY_ONLY")



def return_data_with_vector_similarity_search(
    input_vector,
    filtered_ids: Optional[Sequence[int]] = None,
):
    # If FastAPI already computed filtered IDs, use them.
    # Otherwise fall back to a default DB filter.
    get_filtered_ids = list(filtered_ids) if filtered_ids else filter_db_dynamic()

    if not get_filtered_ids:
        return []

    conn = psycopg2.connect(
        f"dbname=wardrobe user=postgres password={DB_KEY}"
    )
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, description, color, condition, type, score
        FROM wardrobe
        WHERE id = ANY (%s)
        ORDER BY embedding <-> %s::vector
        LIMIT 30;
        """,
        (get_filtered_ids, input_vector,)
    )

    with open("similarity_serach_filtered_ids.json", "w", encoding="utf-8") as f:
        json.dump(get_filtered_ids, f, ensure_ascii=False, indent=2)

    results = cur.fetchall()
    conn.close()

    with open("similarity_search_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results

def convert_selected_data_into_list_of_dictionary(results):
    items = []
    for (item_id, name, description, color, condition, item_type, score) in results:
        items.append(
            {
                "id": item_id,
                "name": name,
                "description": description,
                "color": color,
                "condition": condition,
                "type": item_type,
                "score": score,
            }
        )
    return items


def break_down_data_for_llm(items):
    clothing_items = {}
    allowed_ids = []
    for i, item in enumerate(items, start=1):
        allowed_ids.append(item["id"])
        clothing_items[f"item_{i}"] = {
            "id": item["id"],
            "name": item["name"],
            "color": item["color"],
            "type": item["type"],
        }
    with open("items_for_llm.json", "w", encoding="utf-8") as f:
        json.dump(clothing_items, f, ensure_ascii=False, indent=2)

    return clothing_items, allowed_ids













