import json
import httpx
from typing import List, Optional
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.ingredient import Ingredient
from app.models.user import UserProfile

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

_SYSTEM_PROMPT = (
    "You are a recipe generator. Given available ingredients and a user profile, "
    "generate ONE recipe as valid JSON with exactly this structure: "
    '{"title": str, "description": str, "instructions": [str, ...], '
    '"cooking_time_minutes": int, "servings": int, "tags": [str, ...], '
    '"ingredients": [{"name": str, "amount": number, "unit": str}, ...]}. '
    "Only use ingredients from the list (plus basic staples like salt, pepper, oil). "
    "Respect dietary preferences and allergies. Respond with ONLY the JSON object."
)

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
        return json.loads(raw_content)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Groq API returned invalid JSON"
        )