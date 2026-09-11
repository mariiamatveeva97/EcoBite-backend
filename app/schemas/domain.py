from uuid import UUID
from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, ConfigDict


# USER SCHEMAS
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    display_name: str


class RegistrationResponse(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserLogin(UserBase):
    password: str


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


# PROFILE SCHEMAS
class ProfileBase(BaseModel):
    display_name: Optional[str] = None
    daily_calorie_target: Optional[int] = None
    dietary_preferences: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    cooking_experience_level: Optional[str] = None
    preferred_cooking_time_minutes: Optional[int] = None


class ProfileResponse(ProfileBase):
    id: UUID
    email: EmailStr
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(ProfileBase):
    pass


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