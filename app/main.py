from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.auth import router as auth_router
from app.api.v1.profile import router as profile_router
from app.api.v1.ingredients import router as ingredient_router
from app.api.v1.recipes import router as recipe_router

from app.models.ingredient import Ingredient # noqa: F401 — required to register model with SQLAlchemy
from app.models.recipe import Recipe # noqa: F401 — required to register model with SQLAlchemy
from app.models.recipe_ingredient import RecipeIngredient # noqa: F401 — required to register model with SQLAlchemy
from app.models.recipe_nutritional_data import RecipeNutritionalData  # noqa: F401 — required to register model with SQLAlchemy
from app.models.energy_metrics import EnergyMetrics # noqa: F401 — required to register model with SQLAlchemy
app = FastAPI(title="EcoBite API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(ingredient_router)
app.include_router(recipe_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}