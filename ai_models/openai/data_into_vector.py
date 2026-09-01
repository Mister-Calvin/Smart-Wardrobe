"""Create OpenAI query embeddings for wardrobe similarity searches."""

from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

emb = OpenAIEmbeddings(model="text-embedding-3-small")


def input_to_vector(payload: dict) -> list[float]:
    """Create an embedding vector from an outfit request payload.

    Args:
        payload: Request data containing a user prompt and optional
            outfit context.

    Returns:
        The 1,536-dimensional embedding used for similarity search.
    """
    question = payload.get("user_input", "")
    context = payload.get("context", {}) or {}

    query_text = (
        f"question: {question} - suche passende Schuhe, Tops und Bottoms\n"
        f"event: {context.get('event_input')}\n"
        f"location: {context.get('location_input')}\n"
        f"season: {context.get('season_input')}\n"
        f"weather: {context.get('weather_input')}\n"
        f"mood: {context.get('mood_input')}\n"
        f"styling_hints: {context.get('styling_hints')}"
    )

    query_vec = emb.embed_query(query_text)
    return query_vec
