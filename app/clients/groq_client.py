import json
import httpx
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError
from fastapi import HTTPException, status
import random

from app.core.config import settings
from app.models.ingredient import Ingredient
from app.models.user import UserProfile

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class _GroqRecipeIngredient(BaseModel):
    name: str
    amount: float
    unit: str

class _GroqRecipeContract(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: List[str]
    cooking_time_minutes: int
    servings: Optional[int] = None
    tags: Optional[List[str]] = None
    ingredients: List[_GroqRecipeIngredient]
    appliance: str = Field(default="stove")

_SYSTEM_PROMPT = """
You are a creative professional chef assistant who specializes in turning
ordinary pantry ingredients into surprising, delicious dishes. Avoid the
most obvious or generic preparation — think about different cuisines,
cooking techniques, and flavor combinations each time.

Generate a structured JSON recipe based on user input.

The JSON response MUST include the following fields:
- title (string) — make it specific and appetizing, not generic
- description (string) — 1-2 sentences, mention what makes this dish special
- ingredients (list of objects with name, amount, unit)
- instructions (list of strings) — clear, step-by-step
- cooking_time_minutes (integer)
- servings (integer)
- appliance (string: main cooking appliance used, e.g., "stove", "oven", "airfryer", "microwave", "blender")
"""

_CUISINE_HINTS = [
    "Mediterranean", "Asian-inspired", "Mexican-inspired", "French",
    "Middle Eastern", "Italian", "Indian-inspired", "comfort food",
]

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
                "temperature": 0.9,
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
    style_hint = random.choice(_CUISINE_HINTS)
    return (
        f"Available ingredients: {ingredients_text}\n\n"
        f"User profile:\n{profile_text}\n\n"
        f"Try a {style_hint} take on this dish, if it fits the ingredients well."
    )

def _parse_recipe_json(raw_content: str) -> dict:
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Groq API returned invalid JSON"
        )
    try:
        validated = _GroqRecipeContract.model_validate(data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq response did not match expected recipe contract: {e}"
        )

    return validated.model_dump()
