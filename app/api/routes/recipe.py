"""
Recipe API routes — generation, save, and history endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Request
from app.models.request_models import RecipeRequest, SaveRecipeRequest
from app.models.response_models import (
    RecipeResponse,
    RecipeData,
    NutritionInfo,
    SavedRecipeResponse,
    RecipeHistoryResponse,
    RecipeHistoryItem,
    ErrorResponse,
)
from app.services import ai_service, recipe_db_service
from app.core.security import rate_limiter, sanitize_input

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recipe", tags=["Recipes"])


@router.post(
    "/generate",
    response_model=RecipeResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Generate Recipe",
    description="Generate a detailed AI-powered recipe from ingredients, cuisine style, and dietary preferences.",
)
async def generate_recipe(request: Request, body: RecipeRequest):
    """Generate a recipe using Gemini AI."""
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check(client_ip)

    # Sanitize inputs
    ingredients = sanitize_input(body.ingredients)
    cuisine = sanitize_input(body.cuisine or "")
    dietary = sanitize_input(body.dietary or "")

    if not ingredients:
        raise HTTPException(status_code=400, detail="Please enter at least one ingredient.")

    try:
        recipe_data = await ai_service.generate_recipe(
            ingredients=ingredients,
            cuisine=cuisine,
            dietary=dietary,
        )

        # Build structured response with nutrition info
        nutrition = None
        if "nutrition" in recipe_data and isinstance(recipe_data["nutrition"], dict):
            nutrition = NutritionInfo(**recipe_data["nutrition"])

        recipe = RecipeData(
            title=recipe_data.get("title", "Untitled Recipe"),
            cuisine=recipe_data.get("cuisine", cuisine),
            dietary=recipe_data.get("dietary", dietary),
            ingredients=recipe_data.get("ingredients", []),
            instructions=recipe_data.get("instructions", []),
            notes=recipe_data.get("notes", ""),
            nutrition=nutrition,
            suggestions=recipe_data.get("suggestions", ""),
            prep_time=recipe_data.get("prep_time", ""),
            cook_time=recipe_data.get("cook_time", ""),
            servings=recipe_data.get("servings", ""),
        )

        return RecipeResponse(success=True, recipe=recipe)

    except ValueError as e:
        logger.error(f"Recipe generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error in recipe generation: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating your recipe. Please try again.",
        )


@router.post(
    "/save",
    response_model=SavedRecipeResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Save Recipe",
    description="Save a generated recipe to the database for future reference.",
)
async def save_recipe(body: SaveRecipeRequest):
    """Save a recipe to the database."""
    try:
        recipe_dict = body.model_dump()
        recipe_id = await recipe_db_service.save_recipe(recipe_dict)
        return SavedRecipeResponse(
            success=True,
            id=recipe_id,
            message="Recipe saved successfully!",
        )
    except Exception as e:
        logger.error(f"Failed to save recipe: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save recipe: {e}",
        )


@router.get(
    "/history",
    response_model=RecipeHistoryResponse,
    summary="Recipe History",
    description="Retrieve saved recipes with pagination.",
)
async def get_recipe_history(limit: int = 20, offset: int = 0):
    """Get saved recipe history."""
    try:
        recipes, total = await recipe_db_service.get_recipes(limit=limit, offset=offset)
        items = [RecipeHistoryItem(**r) for r in recipes]
        return RecipeHistoryResponse(success=True, recipes=items, total=total)
    except Exception as e:
        logger.error(f"Failed to fetch recipe history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recipe history: {e}",
        )


@router.delete(
    "/{recipe_id}",
    summary="Delete Recipe",
    description="Delete a saved recipe by its ID.",
)
async def delete_recipe(recipe_id: int):
    """Delete a saved recipe."""
    try:
        deleted = await recipe_db_service.delete_recipe(recipe_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Recipe not found.")
        return {"success": True, "message": "Recipe deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete recipe: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete recipe: {e}",
        )
