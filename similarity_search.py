import psycopg2
import os
from dotenv import load_dotenv
from db_filters import filter_db_dynamic, create_filter_input
import json


load_dotenv()
DB_KEY = os.getenv("POSTGRESQL_KEY_ONLY")



def return_data_with_vector_similarity_search(input_vector):
    get_filtered_ids = filter_db_dynamic(**create_filter_input()) #list with ids

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
        (get_filtered_ids,input_vector,)

    )

    results = cur.fetchall()
    conn.close()
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
    return clothing_items, allowed_ids




























def write_json_from_filtered_data():
    items = []
    allowed_ids_list = []
    for (item_id, name, description, color, condition, item_type, score) in return_data_with_vector_similarity_search():
        allowed_ids_list.append(item_id)
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

    clothing_items = {}
    for i, item in enumerate(items, start=1):
        clothing_items[f"item_{i}"] = {
            "id": item["id"],
            "name": item["name"],
            "color": item["color"],
            "type": item["type"],
        }


    with open("filtered_data.json", "w", encoding="utf-8") as f:
        json.dump(clothing_items, f, indent=2, ensure_ascii=False)

    with open("allowed_ids.json", "w", encoding="utf-8") as f:
        json.dump(allowed_ids_list, f, indent=2, ensure_ascii=False)








