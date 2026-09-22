import json
import httpx
from typing import List, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings
from app.models.ingredient import Ingredient
from app.models.user import UserProfile

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class IngredientSchema(BaseModel):
    name: str
    amount: float
    unit: str

class GroqRecipeResponse(BaseModel):
    title: str
    description: Optional[str] = ""
    ingredients: List[IngredientSchema] = []
    instructions: List[str] = []
    cooking_time_minutes: int = Field(default=15, ge=1)
    servings: int = Field(default=1, ge=1)
    appliance: str = Field(default="stove")

_SYSTEM_PROMPT = """
You are a professional chef assistant. Generate a structured JSON recipe based on user input.
The JSON response MUST include the following fields:
- title (string)
- description (string)
- ingredients (list of objects with name, amount, unit)
- instructions (list of strings)
- cooking_time_minutes (integer)
- servings (integer)
- appliance (string: main cooking appliance used, e.g., "stove", "oven", "airfryer", "microwave", "blender")
"""

def generate_recipe(ingredients: List[Ingredient], profile: Optional[UserProfile]) -> dict:
    prompt = _build_prompt(ingredients, profile)

    try:
        response = httpx.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7,
            },
            timeout=30.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq API request failed: {str(e)}"
        )

    raw_content = response.json()["choices"][0]["message"]["content"]
    return _parse_recipe_json(raw_content)

def _build_prompt(ingredients: List[Ingredient], profile: Optional[UserProfile]) -> str:
    ingredients_text = ", ".join(
        f"{i.quantity} {i.unit} {i.name}" for i in ingredients
    ) or "no ingredients provided"

    lines = []
    if profile:
        if profile.dietary_preferences:
            lines.append(f"Dietary preferences: {', '.join(profile.dietary_preferences)}")
        if profile.allergies:
            lines.append(f"Allergies (avoid): {', '.join(profile.allergies)}")
        if profile.cooking_experience_level:
            lines.append(f"Cooking level: {profile.cooking_experience_level}")
        if profile.preferred_cooking_time_minutes:
            lines.append(f"Max cooking time: {profile.preferred_cooking_time_minutes} min")

    profile_text = "\n".join(lines) if lines else "No specific preferences."
    return f"Available ingredients: {ingredients_text}\n\nUser profile:\n{profile_text}"

def _parse_recipe_json(raw_content: str) -> dict:
    try:
        validated_recipe = GroqRecipeResponse.model_validate_json(raw_content)
        return validated_recipe.model_dump()
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq API returned invalid recipe structure: {str(e)}"
        )