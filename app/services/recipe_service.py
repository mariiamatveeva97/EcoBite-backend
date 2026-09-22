import logging
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.recipe import RecipeResponse
from app.repositories import recipe_repository, ingredient_repository, user_repository
from app.clients import groq_client, spoonacular_client, soap_client

logger = logging.getLogger(__name__)

def generate_recipe_for_user(db: Session, user: User) -> RecipeResponse:
    ingredients = ingredient_repository.get_all_for_user(db, user.id)
    if not ingredients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No ingredients found. Add some ingredients before generating a recipe."
        )

    profile = user_repository.get_profile_by_id(db, user.id)
    recipe_data = groq_client.generate_recipe(ingredients, profile)
    recipe = _save_recipe(db, user.id, recipe_data)

    try:
        nutrition_data = spoonacular_client.get_nutrition_for_recipe(recipe.ingredients, recipe.servings)
        recipe_repository.add_nutrition(db, recipe.id, nutrition_data)
    except HTTPException as e:
        logger.warning(f"Nutrition enrichment failed for recipe {recipe.id}: {e.detail}")

    appliance_type = recipe_data.get("appliance", "stove")
    try:
        energy_data = soap_client.calculate_energy_metrics(
            appliance=appliance_type,
            cooking_time_minutes=recipe.cooking_time_minutes,
            servings=recipe.servings or 1,
        )
        recipe_repository.add_energy_metrics(db, recipe.id, energy_data)
    except HTTPException as e:
        logger.warning(f"Energy metrics calculation failed for recipe {recipe.id}: {e.detail}")

    db.refresh(recipe)
    return RecipeResponse.model_validate(recipe)

def _save_recipe(db: Session, user_id: UUID, recipe_data: dict):
    return recipe_repository.create_recipe(
        db=db,
        user_id=user_id,
        title=recipe_data["title"],
        description=recipe_data.get("description"),
        instructions=recipe_data["instructions"],
        cooking_time_minutes=recipe_data["cooking_time_minutes"],
        servings=recipe_data.get("servings"),
        tags=recipe_data.get("tags"),
        ingredients=recipe_data.get("ingredients", []),
    )
