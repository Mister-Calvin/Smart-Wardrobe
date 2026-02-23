import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

from models import Wardrobe, Session

load_dotenv()


class DataManager():

    def __init__(self):
        self._emb = OpenAIEmbeddings(model="text-embedding-3-small")

    def _build_embedding_text(self, item: Wardrobe) -> str:
        """Baut den Text, aus dem das Embedding berechnet wird."""
        return (
            f"name: {item.name}\n"
            f"description: {item.description}\n"
            f"color: {item.color}\n"
            f"condition: {item.condition}\n"
            f"type: {item.type}\n"
            f"score: {item.score}"
        )

    def _compute_embedding(self, item: Wardrobe):
        """Berechnet das Embedding (list[float]) für ein Wardrobe-Item."""
        text_for_embedding = self._build_embedding_text(item)
        return self._emb.embed_query(text_for_embedding)

    def get_all_items(self):
        session = Session()
        try:
            return session.query(Wardrobe).all()
        finally:
            session.close()

    def get_item_by_id(self, id):
        session = Session()
        try:
            return session.query(Wardrobe).filter(Wardrobe.id == id).first()
        finally:
            session.close()

    def get_items_by_ids(self, ids):
        session = Session()
        try:
            ids_list = list(ids) if ids is not None else []
            if not ids_list:
                return []

            return session.query(Wardrobe).filter(Wardrobe.id.in_(ids_list)).all()
        finally:
            session.close()

    def create_item(self, name, description, color, condition, type, score):
        session = Session()
        new_item = Wardrobe(
            name=name,
            description=description,
            color=color,
            condition=condition,
            type=type,
            score=score,
        )
        try:
            # Embedding direkt berechnen und speichern
            new_item.embedding = self._compute_embedding(new_item)

            session.add(new_item)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"failed to create item:{e}")
            return False
        finally:
            session.close()

    def delete_item(self, id):
        session = Session()
        try:
            item = session.query(Wardrobe).filter(Wardrobe.id == id).first()
            if item:
                session.delete(item)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"failed to delete item:{e}")
            return False
        finally:
            session.close()

    def delete_all_items(self):
        session = Session()
        try:
            session.query(Wardrobe).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"failed to delete all items:{e}")
            return False
        finally:
            session.close()

    def update_item(self, id, name, description, color, condition, type, score):
        session = Session()
        try:
            item = session.query(Wardrobe).filter(Wardrobe.id == id).first()
            if item:
                item.name = name
                item.description = description
                item.color = color
                item.condition = condition
                item.type = type
                item.score = score


                item.embedding = self._compute_embedding(item)

                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"failed to update item:{e}")
            return False
        finally:
            session.close()