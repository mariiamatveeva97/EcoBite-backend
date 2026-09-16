import uuid
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base

class EnergyMetrics(Base):
    __tablename__ = "energy_metrics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    estimated_kwh: Mapped[float] = mapped_column(Numeric, nullable=False)
    co2_impact_grams: Mapped[float] = mapped_column(Numeric, nullable=False)
    energy_efficiency_label: Mapped[str] = mapped_column(String(1), nullable=False)
    estimated_cost_eur: Mapped[float] = mapped_column(Numeric, nullable=False)

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="energy")