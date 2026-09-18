import httpx
from typing import List, Optional
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.recipe_ingredient import RecipeIngredient

SPOONACULAR_URL = "https://api.spoonacular.com/recipes/parseIngredients"

def get_nutrition_for_recipe(recipe_ingredients: List[RecipeIngredient], servings: Optional[int]) -> dict:
    ingredient_lines = "\n".join(
        f"{ri.amount} {ri.unit} {ri.ingredient_name}" for ri in recipe_ingredients
    )

    try:
        response = httpx.post(
            SPOONACULAR_URL,
            headers={"x-api-key": settings.SPOONACULAR_API_KEY},
            params={"includeNutrition": "true"},
            data={"ingredientList": ingredient_lines, "servings": servings or 1},
            timeout=20.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Spoonacular API request failed: {str(e)}"
        )

    parsed = response.json()
    return _aggregate_nutrition(parsed)

def _aggregate_nutrition(parsed_ingredients: list) -> dict:
    totals = {"calories": 0.0, "proteins": 0.0, "fats": 0.0, "carbs": 0.0}

    for item in parsed_ingredients:
        nutrients = item.get("nutrition", {}).get("nutrients", [])
        for n in nutrients:
            name = n.get("name", "").lower()
            amount = n.get("amount", 0)
            if name == "calories":
                totals["calories"] += amount
            elif name == "protein":
                totals["proteins"] += amount
            elif name == "fat":
                totals["fats"] += amount
            elif name == "carbohydrates":
                totals["carbs"] += amount

    totals["calories"] = round(totals["calories"])
    totals["nutri_score"] = _estimate_nutri_score(totals)
    return totals

def _estimate_nutri_score(totals: dict) -> str:
    # SIMPLIFIED MVP PLACEHOLDER — NOT the official Nutri-Score algorithm.
    # This function only considers total calories as a rough proxy.
    calories = totals["calories"]
    if calories < 400:
        return "A"
    elif calories < 600:
        return "B"
    elif calories < 800:
        return "C"
    elif calories < 1000:
        return "D"
    return "E"