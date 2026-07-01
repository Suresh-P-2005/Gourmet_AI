"""
AI Service — Gemini integration for recipe generation.
Clean prompt engineering, retry mechanism, and response validation.
"""

import asyncio
import logging
from typing import Optional

import google.generativeai as genai

from app.core.config import get_settings
from app.utils.parser import extract_json, validate_recipe_structure

logger = logging.getLogger(__name__)

# ── Prompt Template ────────────────────────────────────────────────────────────
RECIPE_PROMPT = """You are a world-class professional chef and nutritionist.
Generate a detailed, creative recipe using these ingredients: {ingredients}.
{cuisine_line}
{dietary_line}

You MUST respond with ONLY a valid JSON object (no markdown, no extra text) in this exact structure:
{{
    "title": "Creative and appetizing recipe name",
    "cuisine": "{cuisine}",
    "dietary": "{dietary}",
    "prep_time": "estimated prep time (e.g. 15 minutes)",
    "cook_time": "estimated cooking time (e.g. 30 minutes)",
    "servings": "number of servings (e.g. 4 servings)",
    "ingredients": [
        "ingredient 1 with exact quantity",
        "ingredient 2 with exact quantity"
    ],
    "instructions": [
        "Detailed step 1 with temperatures and timing",
        "Detailed step 2 with technique tips"
    ],
    "notes": "Professional chef's tips, variations, and serving suggestions",
    "nutrition": {{
        "calories": "estimated calories per serving",
        "protein": "protein in grams",
        "carbs": "carbs in grams",
        "fat": "fat in grams",
        "fiber": "fiber in grams"
    }},
    "suggestions": "Ingredient substitutions if some items are missing, and complementary side dishes"
}}

Rules:
- Include precise quantities for ALL ingredients
- Steps should be detailed with exact temperatures and timing
- Nutrition values should be realistic estimates per serving
- Suggestions should mention possible substitutions and pairings
- Make the recipe creative, restaurant-quality, and achievable at home
"""


async def generate_recipe(
    ingredients: str,
    cuisine: str = "",
    dietary: str = "",
    max_retries: int = 3,
) -> dict:
    """
    Generate a recipe using Gemini AI with retry mechanism.
    
    Args:
        ingredients: Comma-separated ingredient list
        cuisine: Optional cuisine style
        dietary: Optional dietary preferences
        max_retries: Number of retry attempts on failure
    
    Returns:
        Parsed recipe dictionary
    
    Raises:
        ValueError: If recipe generation fails after all retries
    """
    settings = get_settings()
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)

    # Build dynamic prompt sections
    cuisine_line = f"Make it {cuisine} cuisine style." if cuisine else ""
    dietary_line = f"Ensure it is {dietary} friendly." if dietary else ""

    prompt = RECIPE_PROMPT.format(
        ingredients=ingredients,
        cuisine_line=cuisine_line,
        dietary_line=dietary_line,
        cuisine=cuisine or "Not specified",
        dietary=dietary or "No restrictions",
    )

    last_error: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Recipe generation attempt {attempt}/{max_retries}")

            # Generate content (run sync call in executor to keep async)
            response = await asyncio.to_thread(model.generate_content, prompt)
            response_text = response.text.strip()

            # Parse JSON from response
            recipe_data = extract_json(response_text)

            if recipe_data is None:
                raise ValueError(f"Could not extract JSON from response: {response_text[:200]}")

            if not validate_recipe_structure(recipe_data):
                raise ValueError(f"Missing required fields in recipe: {list(recipe_data.keys())}")

            logger.info(f"Recipe generated successfully: {recipe_data.get('title', 'Unknown')}")
            return recipe_data

        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt} failed: {e}")

            if attempt < max_retries:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** (attempt - 1)
                await asyncio.sleep(wait_time)

    # All retries exhausted
    raise ValueError(
        f"Failed to generate recipe after {max_retries} attempts. "
        f"Last error: {last_error}"
    )
