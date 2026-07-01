"""
Pydantic request models — strict validation for all API inputs.
"""

from pydantic import BaseModel, Field
from typing import Optional


class RecipeRequest(BaseModel):
    """Request body for recipe generation."""
    ingredients: str = Field(
        ...,
        min_length=2,
        max_length=2000,
        description="Comma-separated list of ingredients",
        examples=["chicken breast, bell peppers, garlic, olive oil"],
    )
    cuisine: Optional[str] = Field(
        default="",
        max_length=100,
        description="Desired cuisine style",
        examples=["Italian", "Thai", "Mediterranean"],
    )
    dietary: Optional[str] = Field(
        default="",
        max_length=200,
        description="Dietary preferences or restrictions",
        examples=["vegetarian", "keto", "gluten-free"],
    )


class VisionDetectRequest(BaseModel):
    """Request body for camera-based ingredient detection."""
    image: str = Field(
        ...,
        min_length=100,
        description="Base64-encoded image data (JPEG, PNG, or WebP)",
    )


class SaveRecipeRequest(BaseModel):
    """Request body for saving a generated recipe."""
    title: str = Field(..., min_length=1, max_length=500)
    cuisine: Optional[str] = ""
    dietary: Optional[str] = ""
    ingredients: list[str] = Field(..., min_length=1)
    instructions: list[str] = Field(..., min_length=1)
    notes: Optional[str] = ""
    nutrition: Optional[dict] = {}
    suggestions: Optional[str] = ""
