from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: List[str]
    cooking_time_minutes: int
    servings: Optional[int] = None
    tags: Optional[List[str]] = None

class RecipeCreate(RecipeBase):
    pass

class RecipeIngredientResponse(BaseModel):
    ingredient_name: str
    amount: float
    unit: str

    model_config = ConfigDict(from_attributes=True)

class NutritionResponse(BaseModel):
    calories: int
    proteins: float
    fats: float
    carbs: float
    nutri_score: str = Field(
        description="Simplified calorie-based estimate, NOT the official Nutri-Score algorithm (MVP placeholder)."
    )

    model_config = ConfigDict(from_attributes=True)

class RecipeResponse(RecipeBase):
    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime
    ingredients: List[RecipeIngredientResponse] = Field(default_factory=list)
    nutrition: Optional[NutritionResponse] = None

    model_config = ConfigDict(from_attributes=True)

class EnergyResponse(BaseModel):
    estimated_kwh: float
    co2_impact_grams: float
    energy_efficiency_label: str
    estimated_cost_eur: float

    model_config = ConfigDict(from_attributes=True)

class RecipeResponse(RecipeBase):
    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime
    ingredients: List[RecipeIngredientResponse] = Field(default_factory=list)
    nutrition: Optional[NutritionResponse] = None
    energy: Optional[EnergyResponse] = None

    model_config = ConfigDict(from_attributes=True)