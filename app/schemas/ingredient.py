from uuid import UUID
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class IngredientBase(BaseModel):
    name: str
    quantity: float
    unit: str
    category: Optional[str] = None
    expiration_date: Optional[date] = None


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)