"""Define the database model for Gemini wardrobe embeddings."""

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from pgvector.sqlalchemy import Vector

from models import Base
from ai_models.gemini.gemini_client import (
    EMBEDDING_DIMENSIONS,
)


class GeminiWardrobeEmbedding(Base):
    """Store a Gemini embedding for one wardrobe item and model setup."""
    __tablename__ = "wardrobe_gemini_embeddings"

    __table_args__ = (
        UniqueConstraint(
            "wardrobe_id",
            "model",
            "dimensions",
            name="uq_gemini_wardrobe_model_dimensions",
        ),
    )

    id = Column(Integer, primary_key=True)

    wardrobe_id = Column(
        Integer,
        ForeignKey(
            "wardrobe.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    model = Column(
        String(100),
        nullable=False,
    )

    dimensions = Column(
        Integer,
        nullable=False,
        default=EMBEDDING_DIMENSIONS,
    )

    embedding = Column(
        Vector(EMBEDDING_DIMENSIONS),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return a concise representation of the embedding record."""
        return (
            f"GeminiWardrobeEmbedding("
            f"wardrobe_id={self.wardrobe_id}, "
            f"model={self.model}, "
            f"dimensions={self.dimensions})"
        )
