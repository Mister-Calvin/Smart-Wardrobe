"""Retrieve wardrobe candidates with OpenAI vector similarity."""

import psycopg2
import os
from dotenv import load_dotenv
from db_filters import filter_db_dynamic
from typing import Optional, Sequence



load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL fehlt in der .env."
    )



def return_data_with_vector_similarity_search(
    input_vector,
    filtered_ids: Optional[Sequence[int]] = None,
):


    """Return wardrobe rows ranked by OpenAI vector distance."""
    get_filtered_ids = list(filtered_ids) if filtered_ids else filter_db_dynamic()

    if not get_filtered_ids:
        return []

    conn = psycopg2.connect(
    DATABASE_URL
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

    results = cur.fetchall()
    conn.close()

    return results

def convert_selected_data_into_list_of_dictionary(results):
    """Convert database rows into wardrobe item dictionaries."""
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
    """Reduce wardrobe items to compact candidates and allowed IDs."""
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
    return clothing_items, allowed_ids












