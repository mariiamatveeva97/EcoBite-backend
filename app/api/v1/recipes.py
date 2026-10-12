from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.recipe import RecipeResponse
from app.api.deps import get_current_user
from app.services import recipe_service
from app.models.recipe import Recipe

router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.post("/generate", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def generate_recipe(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return recipe_service.generate_recipe_for_user(db, current_user)


@router.get("", response_model=list[RecipeResponse])
def get_recipes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return recipe_service.get_recipes_for_user(db, current_user)

@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return recipe_service.get_recipe_by_id(db, current_user, recipe_id)

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
        recipe_id: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id, Recipe.user_id == current_user.id).first()
    if not recipe:
        raise HTTPException(
            status_code=404,
            detail="Recept niet gevonden"
        )
    db.delete(recipe)
    db.commit()

    return None