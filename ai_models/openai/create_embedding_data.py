"""Backfill missing OpenAI embeddings for wardrobe items."""

from sqlalchemy import text
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
from models import Session, Wardrobe


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


emb = OpenAIEmbeddings(model="text-embedding-3-small")


session = Session()


def create_embedding_column_and_seed_data(batch_size: int = 50):
    """Erstellt fehlende Embeddings in Batches (Standard: 50)."""
    try:

        session.execute(text("""
            ALTER TABLE wardrobe
            ADD COLUMN IF NOT EXISTS embedding vector(1536);
        """))
        session.commit()

        total_done = 0

        while True:

            items = (
                session.query(Wardrobe)
                .filter(Wardrobe.embedding.is_(None))
                .order_by(Wardrobe.id.asc())
                .limit(batch_size)
                .all()
            )

            if not items:
                if total_done == 0:
                    print("✅ Alle Items haben bereits ein Embedding.")
                else:
                    print(f"✅ Fertig. Insgesamt neu erstellt: {total_done}")
                break

            for item in items:

                text_for_embedding = (
                    f"name: {item.name}\n"
                    f"description: {item.description}\n"
                    f"color: {item.color}\n"
                    f"condition: {item.condition}\n"
                    f"type: {item.type}\n"
                    f"score: {item.score}"
                )


                vector = emb.embed_query(text_for_embedding)


                item.embedding = vector

            session.commit()
            total_done += len(items)
            print(f"✅ Batch gespeichert: {len(items)} | Insgesamt: {total_done}")

    finally:
        session.close()
