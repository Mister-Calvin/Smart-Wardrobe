"""Provide wardrobe operations with provider-specific embedding writes."""

from ai_models.embedding_writer_router import (
    normalize_embedding_provider,
    upsert_item_embedding,
)
from models import Wardrobe, Session

class EmbeddingProviderNotConfiguredError(
    RuntimeError
):
    """Indicate that an embedding write has no selected provider."""
    pass


class DataManager:

    """Manage wardrobe records and their selected-provider embeddings."""
    def __init__(
        self,
        embedding_provider: str | None = None,
    ):
        """Initialize the manager with an optional embedding provider."""
        if embedding_provider is None:
            self._embedding_provider = None

        else:
            self._embedding_provider = (
                normalize_embedding_provider(
                    embedding_provider
                )
            )

    def _require_embedding_provider(
        self,
    ) -> str:
        """Return the provider or raise when none is configured."""
        if self._embedding_provider is None:
            raise (
                EmbeddingProviderNotConfiguredError(
                    "Für Create oder Update "
                    "muss ein Embedding-Provider "
                    "angegeben werden."
                )
            )

        return self._embedding_provider

    def get_all_items(self):
        """Return all stored wardrobe items."""
        session = Session()

        try:
            return session.query(
                Wardrobe
            ).all()

        finally:
            session.close()

    def get_item_by_id(
        self,
        id,
    ):
        """Return one wardrobe item by ID or None when it is absent."""
        session = Session()

        try:
            return (
                session.query(Wardrobe)
                .filter(Wardrobe.id == id)
                .first()
            )

        finally:
            session.close()

    def get_items_by_ids(
        self,
        ids,
    ):
        """Return wardrobe items matching the supplied IDs."""
        session = Session()

        try:
            ids_list = (
                list(ids)
                if ids is not None
                else []
            )

            if not ids_list:
                return []

            return (
                session.query(Wardrobe)
                .filter(
                    Wardrobe.id.in_(
                        ids_list
                    )
                )
                .all()
            )

        finally:
            session.close()

    def create_item(
        self,
        name,
        description,
        color,
        condition,
        type,
        score,
    ):
        """Create an item and its embedding in one transaction."""
        embedding_provider = (
            self._require_embedding_provider()
        )
        session = Session()

        try:
            new_item = Wardrobe(
                name=name,
                description=description,
                color=color,
                condition=condition,
                type=type,
                score=score,
            )

            session.add(new_item)



            session.flush()

            upsert_item_embedding(
                session=session,
                item=new_item,
                provider=(
                    embedding_provider
                ),
            )

            session.commit()
            return True

        except Exception as error:
            session.rollback()

            print(
                "failed to create item: "
                f"{error}"
            )

            return False

        finally:
            session.close()

    def delete_item(
        self,
        id,
    ):
        """Delete one wardrobe item and report whether it succeeded."""
        session = Session()

        try:
            item = (
                session.query(Wardrobe)
                .filter(Wardrobe.id == id)
                .first()
            )

            if item is None:
                return False

            session.delete(item)
            session.commit()

            return True

        except Exception as error:
            session.rollback()

            print(
                "failed to delete item: "
                f"{error}"
            )

            return False

        finally:
            session.close()

    def delete_all_items(self):
        """Delete every wardrobe item and report whether it succeeded."""
        session = Session()

        try:
            session.query(
                Wardrobe
            ).delete()

            session.commit()
            return True

        except Exception as error:
            session.rollback()

            print(
                "failed to delete all items: "
                f"{error}"
            )

            return False

        finally:
            session.close()

    def update_item(
        self,
        id,
        name,
        description,
        color,
        condition,
        type,
        score,
    ):
        """Update an item and refresh its provider-specific embedding."""
        embedding_provider = (
            self._require_embedding_provider()
        )


        session = Session()

        try:
            item = (
                session.query(Wardrobe)
                .filter(Wardrobe.id == id)
                .first()
            )

            if item is None:
                return False

            item.name = name
            item.description = description
            item.color = color
            item.condition = condition
            item.type = type
            item.score = score

            session.flush()

            upsert_item_embedding(
                session=session,
                item=item,
                provider=(
                    embedding_provider
                ),
            )

            session.commit()
            return True

        except Exception as error:
            session.rollback()

            print(
                "failed to update item: "
                f"{error}"
            )

            return False

        finally:
            session.close()
