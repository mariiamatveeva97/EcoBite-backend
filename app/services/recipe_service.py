from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.recipe import RecipeResponse
from app.repositories import recipe_repository, ingredient_repository, user_repository
from app.clients import groq_client

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