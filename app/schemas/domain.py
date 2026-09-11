from uuid import UUID
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

# INGREDIENT SCHEMAS

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

# RECIPE SCHEMAS

class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: List[str]
    cooking_time_minutes: int
    servings: Optional[int] = None
    tags: Optional[List[str]] = None

class RecipeCreate(RecipeBase):
    pass

class RecipeResponse(RecipeBase):
    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)