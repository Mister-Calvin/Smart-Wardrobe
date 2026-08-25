from sqlalchemy import text
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
from models import Session, Wardrobe

# 1) API Key laden
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 2) Embeddings Client
emb = OpenAIEmbeddings(model="text-embedding-3-small")

# 3) DB Session
session = Session()


def create_embedding_column_and_seed_data(batch_size: int = 50):
    """Erstellt fehlende Embeddings in Batches (Standard: 50)."""
    try:
        # 4) Spalte anlegen (falls nicht vorhanden)
        session.execute(text("""
            ALTER TABLE wardrobe
            ADD COLUMN IF NOT EXISTS embedding vector(1536);
        """))
        session.commit()

        total_done = 0

        while True:
            # 5) Immer nur die nächsten N Items holen, denen noch ein Embedding fehlt
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
                # Item -> Text (String!)
                text_for_embedding = (
                    f"name: {item.name}\n"
                    f"description: {item.description}\n"
                    f"color: {item.color}\n"
                    f"condition: {item.condition}\n"
                    f"type: {item.type}\n"
                    f"score: {item.score}"
                )

                # Text -> Vector
                vector = emb.embed_query(text_for_embedding)

                # In DB schreiben
                item.embedding = vector

            session.commit()
            total_done += len(items)
            print(f"✅ Batch gespeichert: {len(items)} | Insgesamt: {total_done}")

    finally:
        session.close()


#create_embedding_column_and_seed_data(batch_size=50)