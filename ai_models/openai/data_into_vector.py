import json
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
from json_manager import wirte_json



# 1) API Key laden
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


# 2) Embeddings Client
emb = OpenAIEmbeddings(model="text-embedding-3-small")




def input_to_vector(payload: dict) -> list[float]:
    """
    Nimmt den Payload vom Endpoint entgegen und baut daraus den Query-Text
    für das Embedding. Gibt den Query-Vektor (list[float]) zurück.
    """
    question = payload.get("user_input", "")
    context = payload.get("context", {}) or {}


    wirte_json("vector_payload",context)


    query_text = (
        f"question: {question} - suche passende Schuhe, Tops und Bottoms\n"
        f"event: {context.get('event_input')}\n"
        f"location: {context.get('location_input')}\n"
        f"season: {context.get('season_input')}\n"
        f"weather: {context.get('weather_input')}\n"
        f"mood: {context.get('mood_input')}\n"
        f"styling_hints: {context.get('styling_hints')}"

    )

    query_vec = emb.embed_query(query_text)  # -> list[float] (1536)
    return query_vec