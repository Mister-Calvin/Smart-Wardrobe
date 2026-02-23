import json
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv



# 1) API Key laden
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
DB_KEY = os.getenv("POSTGRESQL_KEY_ONLY")


# 2) Embeddings Client
emb = OpenAIEmbeddings(model="text-embedding-3-small")




def input_to_vector(payload: dict) -> list[float]:
    """
    Nimmt den Payload vom Endpoint entgegen und baut daraus den Query-Text
    für das Embedding. Gibt den Query-Vektor (list[float]) zurück.
    """
    question = payload.get("user_input", "")
    context = payload.get("context", {}) or {}

    query_text = (
        f"question: {question} - mit passenden schuhen, top und bottom\n"
        f"event: {context.get('event_input')}\n"
        f"location: {context.get('location_input')}\n"
        f"season: {context.get('season_input')}\n"
        f"weather: {context.get('weather_input')}\n"
        f"mood: {context.get('mood_input')}"
    )

    query_vec = emb.embed_query(query_text)  # -> list[float] (1536)
    return query_vec
