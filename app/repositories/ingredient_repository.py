from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate

def get_all_for_user(db: Session, user_id: UUID) -> List[Ingredient]:
    return db.query(Ingredient).filter(Ingredient.user_id == user_id).all()

def get_by_id(db: Session, ingredient_id: UUID) -> Optional[Ingredient]:
    return db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

def create(db: Session, user_id: UUID, ingredient_in: IngredientCreate) -> Ingredient:
    ingredient = Ingredient(user_id=user_id, **ingredient_in.model_dump())
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient

def update(db: Session, ingredient: Ingredient, update_data: dict) -> Ingredient:
    for field, value in update_data.items():
        setattr(ingredient, field, value)
    db.commit()
    db.refresh(ingredient)
    return ingredient

def delete(db: Session, ingredient: Ingredient) -> None:
    db.delete(ingredient)
    db.commit()