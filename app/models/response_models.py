"""
Pydantic response models — structured output for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NutritionInfo(BaseModel):
    """Estimated nutrition information per serving."""
    calories: Optional[str] = ""
    protein: Optional[str] = ""
    carbs: Optional[str] = ""
    fat: Optional[str] = ""
    fiber: Optional[str] = ""


class RecipeData(BaseModel):
    """Core recipe data returned by AI generation."""
    title: str
    cuisine: Optional[str] = ""
    cuisine_type: Optional[str] = "Other"
    dietary: Optional[str] = ""
    ingredients: list[str]
    instructions: list[str]
    notes: Optional[str] = ""
    nutrition: Optional[NutritionInfo] = None
    suggestions: Optional[str] = ""
    prep_time: Optional[str] = ""
    cook_time: Optional[str] = ""
    servings: Optional[str] = ""
    token_usage: Optional[dict] = None


class RecipeResponse(BaseModel):
    """Successful recipe generation response."""
    success: bool = True
    recipe: RecipeData


class VisionDetectResponse(BaseModel):
    """Response from ingredient detection via camera image."""
    success: bool = True
    detected_ingredients: list[str]
    confidence: Optional[str] = "high"
    message: Optional[str] = ""


class SavedRecipeResponse(BaseModel):
    """Response after saving a recipe."""
    success: bool = True
    id: int
    message: str = "Recipe saved successfully"


class RecipeHistoryItem(BaseModel):
    """Single recipe in the history list."""
    id: int
    title: str
    cuisine: Optional[str] = ""
    cuisine_type: Optional[str] = "Other"
    dietary: Optional[str] = ""
    ingredients: list[str]
    instructions: list[str]
    notes: Optional[str] = ""
    personal_notes: Optional[str] = ""
    is_public: Optional[bool] = False
    nutrition: Optional[dict] = {}
    suggestions: Optional[str] = ""
    created_at: Optional[str] = ""


class RecipeHistoryResponse(BaseModel):
    """Paginated list of saved recipes."""
    success: bool = True
    recipes: list[RecipeHistoryItem]
    total: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    uptime_seconds: float
    gemini_configured: bool


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    details: Optional[str] = ""
    solution: Optional[str] = ""

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
