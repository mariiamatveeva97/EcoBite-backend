from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.recipe import RecipeResponse
from app.api.deps import get_current_user
from app.services import recipe_service

router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.post("/generate", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def generate_recipe(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return recipe_service.generate_recipe_for_user(db, current_user)