from uuid import UUID
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class IngredientBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=50)
    category: Optional[str] = Field(default=None, max_length=100)
    expiration_date: Optional[date] = None

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    quantity: Optional[float] = Field(default=None, gt=0)
    unit: Optional[str] = Field(default=None, min_length=1, max_length=50)
    category: Optional[str] = Field(default=None, max_length=100)
    expiration_date: Optional[date] = None

class IngredientResponse(IngredientBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)