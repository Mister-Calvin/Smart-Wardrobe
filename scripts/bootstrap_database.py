"""Initialize the vector extension and Smart Wardrobe database tables."""

from sqlalchemy import text

from models import Base, engine


from ai_models.gemini.gemini_embedding_model import (
    GeminiWardrobeEmbedding,
)


def bootstrap_database() -> None:
    """Enable pgvector and create missing tables without deleting data."""
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE EXTENSION "
                "IF NOT EXISTS vector"
            )
        )

        Base.metadata.create_all(
            bind=connection,
            checkfirst=True,
        )

    print(
        "Smart-Wardrobe-Datenbank ist bereit."
    )


if __name__ == "__main__":
    bootstrap_database()