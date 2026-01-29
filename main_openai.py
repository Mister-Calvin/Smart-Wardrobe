import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from data_manager import DataManager
import json


manager = DataManager()
all_items = manager.get_all_items()

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)


class OutfitSuggestion(BaseModel):
    title: str                          # z. B. "Elegantes Büro-Outfit"
    summary: str                        # Beschreibung + Begründung
    items: list[str]                    # Liste der empfohlenen Kleidungsstücke
    items_ids: list[int]

class OutfitSuggestions(BaseModel):
    outfits: list[OutfitSuggestion]


def get_input():
    with open("input_data.json", "r", encoding="utf-8") as file:
        input_text = json.load(file)
        return input_text



def context_input():

    context = {
        "event": get_input()["context"]["event_input"],
        "location": get_input()["context"]["location_input"],
        "season": get_input()["context"]["season_input"],
        "weather": get_input()["context"]["weather_input"],
        "mood": get_input()["context"]["mood_input"],
    }
    return context

def create_response():
    response = client.responses.parse(                                         #client.chat.completions.create
        input=[
            {
                "role": "system",
                "content": (
                    "Du bist SmartWardrobe AI – ein professioneller Mode-Experte.\n"
                    "Du benutzt AUSSCHLIESSLICH Kleidungsstücke aus folgender Liste:\n"
                    f"{all_items} - Wenn diese Liste leer ist kannst du keine Outfits erstellen, das ist die grundlage"
                    "Erstelle standartmäßig 3 unterschiedliche Outfit-Vorschläge.\n"
                    "Jedes Outfit muss sinnvoll, vollständig und realistisch sein.\n"
                    "Macht es sinn mehr als 3 Outfits vorzuschlagen mach das"
                    "Outfits für eine ganze Woche ein neues Outfit pro Tag, also 7 verschiedene Outfit-Vorschläge"
                    "Gib das Ergebnis AUSSCHLIESSLICH im vorgegebenen JSON-Format zurück."
                    "Du darfst NIEMALS Haluzinieren! Du musst dann die felder mit unbekannt ausfüllen"
                )
            },
            {
                "role": "user",
                "content": f"""
                {get_input()}
                Hier sind zusätzliche Kontextdaten (JSON): {context_input()}
                """
            }
        ],
        model="gpt-4o-mini",
        temperature=0.7,
        max_output_tokens=500,
        text_format=OutfitSuggestions

    )
    return response

def create_answer():
    answer = create_response().output_parsed
    outfits_dict = {}
    for i, outfit in enumerate(answer.outfits, start=1):
        outfits_dict[f"outfit_{i}"] = {
            "user_input": get_input(),
            "title": outfit.title,
            "summary": outfit.summary,
            "items": outfit.items,
            "items_ids": outfit.items_ids,
            "items_with_ids": [
                {"name": name, "id": item_id}
                for name, item_id in zip(outfit.items, outfit.items_ids)
            ]
        }
        print(f"\nOutfit {i}: {outfit.title}")
        print(outfit.summary)
        print(f"Clothes : {outfit.items} - {outfit.items_ids}")


    with open("outfits.json", "w", encoding="utf-8") as f:
        json.dump(outfits_dict, f, indent=2, ensure_ascii=False)
    return

#create_answer()