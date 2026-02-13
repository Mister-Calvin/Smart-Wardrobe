from openai_model import create_response, create_answer
from extend_llm_answer import get_all_ids_list, get_db_by_id, extended_answer

payload = {
  "user_input": "Was kann ich am besten zur Party anziehen? ",
  "context": {
    "event_input": "Alltag",
    "location_input": "Outdoor",
    "season_input": "Sommer",
    "weather_input": "kalt",
    "mood_input": "euphorisch"
  }
}

def build_outfit(payload):
    llm_answer = create_answer(create_response(payload))
    ids = get_all_ids_list(llm_answer)        # 2) IDs daraus ziehen
    items_by_id = get_db_by_id(ids)     # 3) DB-Daten zu den IDs holen
    extended_answer(llm_answer, items_by_id)  # 4) Extended Ausgabe bauen


if __name__ == "__main__":
    answer = build_outfit(payload)
    print(answer)

