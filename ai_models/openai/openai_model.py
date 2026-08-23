import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import json
from typing import List, Optional
from ai_models.openai.similarity_search import (
    break_down_data_for_llm,
    convert_selected_data_into_list_of_dictionary,
    return_data_with_vector_similarity_search,
)
from ai_models.openai.data_into_vector import (
    input_to_vector,
)

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

class OutfitSlots(BaseModel):
    top_id: int
    bottom_id: Optional [int] = None
    shoes_id: int

    headwear_id: Optional[int] = None
    outerwear_id: Optional[int] = None
    socks_id: Optional[int] = None
    bag_id: Optional[int] = None
    accessory_id: Optional[int] = None

    all_ids: List[int]



class OutfitSuggestion(BaseModel):
    name: str
    how_to_wear: str
    rationale: str
    slots: OutfitSlots


class OutfitSuggestions(BaseModel):
    outfits: List[OutfitSuggestion]



SYSTEM_PROMPT = """
Du bist ein professioneller Mode-Berater und erstellst stylische Outfits.

HARTE REGELN:
- Ein Outfit besteht mindestens aus Top, Bottom und Shoes 
- Verwende ausschließlich Items aus der übergebenen CANDIDATES-Liste.
- Um Halluzinationen zu reduzieren, habe ich eine Liste mit allen erlaubten Outfit-IDs erstellt: allowed_ids
- Erfinde keine Items, keine IDs, keine Farben, keine Marken.
- Versuche deutlich unterschiedliche Outfits zu erstellen, sodass sich IDs nicht wiederholen
- Achte besonders auf Wettergerechte Kleidung
- Erstelle genau 3 Outfits.
- Gib die Antwort ausschließlich im vorgegebenen JSON-Format (Schema) zurück.
"""

def has_minimum_items(candidates: dict) -> bool:
    # candidates ist dein dict: {"item_1": {...}, "item_2": {...}}
    types = [it.get("type") for it in candidates.values()]

    # super simple: brauchst mindestens 1 "schuhe" und mindestens 2 "unten" und 2 "oben"
    shoes = sum(t in {"schuhe", "stiefel", "boots"} for t in types)

    bottoms = sum(t in {"hose", "jeans", "rock"} for t in types)
    tops = sum(t in {"shirt", "hoodie", "bluse", "hemd", "blazer", "sport"} for t in types)

    # kleid zählt als "top + bottom" (weil 1-teilig)
    dresses = sum(t == "kleid" for t in types)
    tops += dresses
    bottoms += dresses

    return shoes >= 1 and tops >= 2 and bottoms >= 2


class NotEnoughItemsForOutfitError(Exception):
    """Raised when the candidate pool doesn't contain enough items to build 3 outfits."""

    def __init__(self, message: str = "nicht genügend verschiedene Items zum Erstellen eines Outfits"):
        super().__init__(message)



def create_response(input_data, filtered_ids):
    query_vec = input_to_vector(input_data)
    raw_results = return_data_with_vector_similarity_search(query_vec, filtered_ids)

    with open("create_response_query_vec.json", "w", encoding="utf-8") as f:
        json.dump(query_vec, f, ensure_ascii=False, indent=2)

    with open("create_response_ids.json", "w", encoding="utf-8") as f:
        json.dump(filtered_ids, f, ensure_ascii=False, indent=2)

    items = convert_selected_data_into_list_of_dictionary(raw_results)
    items, allowed_ids = break_down_data_for_llm(items)

    with open("create_response_items_for_llm.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    if not has_minimum_items(items):
        raise NotEnoughItemsForOutfitError()


    payload = {
        "user_input": input_data,
        "candidates": items,
        "allowed_ids": allowed_ids,
    }
    with open("create_response_payload.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    response = client.responses.parse(
        model="gpt-4o-mini",
        temperature=0.3,
        max_output_tokens=1000,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        text_format=OutfitSuggestions

    )

    print("USAGE:", response.usage)

    return response, allowed_ids


def create_answer(response_and_ids):
    response, allowed_ids = response_and_ids
    data = response.output_parsed.model_dump()


    ids_from_answer = []
    for outfit in data["outfits"]:
        ids_from_answer.extend(outfit["slots"]["all_ids"])


    hallucinated = set(ids_from_answer) - set(allowed_ids)


    result = {
        "outfits": data["outfits"],
        "allowed_ids": allowed_ids,
        "ids_from_answer": sorted(set(ids_from_answer)),
        "hallucinated_ids": sorted(hallucinated),
        "is_valid": len(hallucinated) == 0,
    }


    with open("llm_answer.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


