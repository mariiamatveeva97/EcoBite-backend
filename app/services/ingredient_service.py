from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.ingredient import IngredientCreate, IngredientResponse, IngredientUpdate
from app.repositories import ingredient_repository

def get_all_ingredients(db: Session, user: User) -> List[IngredientResponse]:
    ingredients = ingredient_repository.get_all_for_user(db, user.id)
    return [IngredientResponse.model_validate(i) for i in ingredients]

def create_ingredient(db: Session, user: User, ingredient_in: IngredientCreate) -> IngredientResponse:
    ingredient = ingredient_repository.create(db, user.id, ingredient_in)
    return IngredientResponse.model_validate(ingredient)

def update_ingredient(db: Session, user: User, ingredient_id: UUID, ingredient_in: IngredientUpdate) -> IngredientResponse:
    ingredient = _get_owned_ingredient(db, user, ingredient_id)
    update_data = ingredient_in.model_dump(exclude_unset=True)
    ingredient = ingredient_repository.update(db, ingredient, update_data)
    return IngredientResponse.model_validate(ingredient)

def delete_ingredient(db: Session, user: User, ingredient_id: UUID) -> None:
    ingredient = _get_owned_ingredient(db, user, ingredient_id)
    ingredient_repository.delete(db, ingredient)

def _get_owned_ingredient(db: Session, user: User, ingredient_id: UUID):
    ingredient = ingredient_repository.get_by_id(db, ingredient_id)
    if not ingredient or ingredient.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found"
        )
    return ingredient