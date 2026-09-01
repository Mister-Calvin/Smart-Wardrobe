"""Configure Gemini API clients from environment variables."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from google import genai


load_dotenv()


GENERATION_MODEL = os.getenv(
    "GEMINI_GENERATION_MODEL",
    "gemini-3.7-flash",
)

EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-2",
)

EMBEDDING_DIMENSIONS = int(
    os.getenv("GEMINI_EMBEDDING_DIMENSIONS", "1536")
)


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    """Return the cached Gemini client configured with the API key."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY fehlt. Bitte in der .env konfigurieren."
        )

    return genai.Client(api_key=api_key)


def test_connection() -> str:
    """Send a fixed Gemini request and return its response text."""
    client = get_gemini_client()

    interaction = client.interactions.create(
        model=GENERATION_MODEL,
        input="Antworte ausschließlich mit: Verbindung funktioniert",
    )

    return interaction.output_text.strip()


if __name__ == "__main__":
    print(test_connection())