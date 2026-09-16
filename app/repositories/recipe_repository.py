from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.recipe_nutritional_data import RecipeNutritionalData
from app.models.energy_metrics import EnergyMetrics

def create_recipe(
    db: Session,
    user_id: Optional[UUID],
    title: str,
    description: Optional[str],
    instructions: list,
    cooking_time_minutes: int,
    servings: Optional[int],
    tags: Optional[list],
    ingredients: List[dict],
) -> Recipe:
    recipe = Recipe(
        user_id=user_id,
        title=title,
        description=description,
        instructions=instructions,
        cooking_time_minutes=cooking_time_minutes,
        servings=servings,
        tags=tags,
    )
    db.add(recipe)
    db.flush()

    for ing in ingredients:
        db.add(RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_name=ing["name"],
            amount=ing["amount"],
            unit=ing["unit"],
        ))

    db.commit()
    db.refresh(recipe)
    return recipe

def get_by_id(db: Session, recipe_id: UUID) -> Optional[Recipe]:
    return db.query(Recipe).filter(Recipe.id == recipe_id).first()

def get_all_for_user(db: Session, user_id: UUID) -> List[Recipe]:
    return db.query(Recipe).filter(Recipe.user_id == user_id).all()

def add_nutrition(db: Session, recipe_id: UUID, nutrition_data: dict) -> RecipeNutritionalData:
    nutrition = RecipeNutritionalData(
        recipe_id=recipe_id,
        calories=nutrition_data["calories"],
        proteins=nutrition_data["proteins"],
        fats=nutrition_data["fats"],
        carbs=nutrition_data["carbs"],
        nutri_score=nutrition_data["nutri_score"],
    )
    db.add(nutrition)
    db.commit()
    db.refresh(nutrition)
    return nutrition

def add_energy_metrics(db: Session, recipe_id: UUID, energy_data: dict) -> EnergyMetrics:
    energy = EnergyMetrics(
        recipe_id=recipe_id,
        estimated_kwh=energy_data["estimated_kwh"],
        co2_impact_grams=energy_data["co2_impact_grams"],
        energy_efficiency_label=energy_data["energy_efficiency_label"],
        estimated_cost_eur=energy_data["estimated_cost_eur"],
    )
    db.add(energy)
    db.commit()
    db.refresh(energy)
    return energy