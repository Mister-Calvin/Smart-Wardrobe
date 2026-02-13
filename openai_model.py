import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import json
from typing import List, Optional
from similarity_search import break_down_data_for_llm, convert_selected_data_into_list_of_dictionary, return_data_with_vector_similarity_search
from data_into_vector import input_to_vector

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

class OutfitSlots(BaseModel):
    top_id: int
    bottom_id: int
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
- Verwende ausschließlich Items aus der übergebenen CANDIDATES-Liste.
- Um Halluzinationen zu reduzieren, habe ich eine Liste mit allen erlaubten Outfit-IDs erstellt: allowed_ids
- Erfinde keine Items, keine IDs, keine Farben, keine Marken.
- Versuche deutlich unterschiedliche Outfits zu erstellen, sodass sich IDs nicht wiederholen
- Achte besonders auf Wettergerechte Kleidung
- Erstelle genau 3 Outfits.
- Gib die Antwort ausschließlich im vorgegebenen JSON-Format (Schema) zurück.
"""


def create_response(input_data):
    query_vec = input_to_vector(input_data)
    raw_results = return_data_with_vector_similarity_search(query_vec)
    items = convert_selected_data_into_list_of_dictionary(raw_results)
    items, allowed_ids = break_down_data_for_llm(items)

    payload = {
        "user_input": input_data,
        "candidates": items,
        "allowed_ids": allowed_ids,
    }

    response = client.responses.parse(
        model="gpt-4o-mini",
        temperature=0.3,
        max_output_tokens=500,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        text_format=OutfitSuggestions
    )
    #print("USAGE:", response.usage)
    return response, allowed_ids


def create_answer(response_and_ids):
    response, allowed_ids = response_and_ids
    data = response.output_parsed.model_dump()


    ids_from_answer = []
    for outfit in data["outfits"]:
        ids_from_answer.extend(outfit["slots"]["all_ids"])


    hallucinated = set(ids_from_answer) - set(allowed_ids)

    #print("allowed_ids:", sorted(set(allowed_ids)))
    #print("ids_from_answer:", sorted(set(ids_from_answer)))
    #print("hallucinated:", sorted(hallucinated))

    return data

