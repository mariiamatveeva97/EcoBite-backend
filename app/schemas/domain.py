from uuid import UUID
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


# USER SCHEMAS
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# INGREDIENT SCHEMAS
class IngredientBase(BaseModel):
    name: str
    category: Optional[str] = None
    fodmap_category: Optional[str] = None


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


# PANTRY SCHEMAS
class UserPantryBase(BaseModel):
    ingredient_id: UUID
    quantity: float = 1.0
    unit: Optional[str] = None
    expiration_date: Optional[date] = None


class UserPantryCreate(UserPantryBase):
    pass


class UserPantryResponse(UserPantryBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    ingredient: Optional[IngredientResponse] = None

    model_config = ConfigDict(from_attributes=True)


# RECIPE SCHEMAS
class RecipeBase(BaseModel):
    title: str
    instructions: str
    prep_time_minutes: Optional[int] = None


class RecipeCreate(RecipeBase):
    pass


class RecipeResponse(RecipeBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)