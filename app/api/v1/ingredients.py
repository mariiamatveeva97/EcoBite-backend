from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.ingredient import IngredientCreate, IngredientResponse, IngredientUpdate
from app.api.deps import get_current_user
from app.services import ingredient_service

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])

@router.get("", response_model=list[IngredientResponse])
def get_ingredients(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ingredient_service.get_all_ingredients(db, current_user)

@router.post("", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    ingredient_in: IngredientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ingredient_service.create_ingredient(db, current_user, ingredient_in)

@router.put("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    ingredient_id: UUID,
    ingredient_in: IngredientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ingredient_service.update_ingredient(db, current_user, ingredient_id, ingredient_in)

@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(
    ingredient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ingredient_service.delete_ingredient(db, current_user, ingredient_id)