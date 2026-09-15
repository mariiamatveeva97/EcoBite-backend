import uuid
from sqlalchemy import String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base

class RecipeNutritionalData(Base):
    __tablename__ = "recipe_nutritional_data"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    calories: Mapped[int] = mapped_column(Integer, nullable=False)
    proteins: Mapped[float] = mapped_column(Numeric, nullable=False)
    fats: Mapped[float] = mapped_column(Numeric, nullable=False)
    carbs: Mapped[float] = mapped_column(Numeric, nullable=False)
    nutri_score: Mapped[str] = mapped_column(String(1), nullable=False)

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="nutrition")