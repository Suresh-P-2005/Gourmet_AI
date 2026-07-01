"""
Vision Service — Gemini Vision API for camera-based ingredient detection.
Accepts images and returns a list of detected food ingredients.
"""

import asyncio
import logging
from typing import Optional

import google.generativeai as genai
from PIL import Image
import io

from app.core.config import get_settings
from app.utils.parser import extract_json
from app.utils.helpers import decode_base64_image, get_image_mime_type

logger = logging.getLogger(__name__)

# ── Vision Prompt ──────────────────────────────────────────────────────────────
DETECTION_PROMPT = """You are a food ingredient identification expert.
Analyze this image carefully and identify ALL visible food ingredients, produce, proteins, spices, and pantry items.

You MUST respond with ONLY a valid JSON object (no markdown, no extra text) in this exact structure:
{
    "detected_ingredients": [
        "ingredient 1",
        "ingredient 2",
        "ingredient 3"
    ],
    "confidence": "high, medium, or low",
    "message": "Brief description of what you see in the image"
}

Rules:
- List every individual ingredient you can identify
- Use common English names (e.g., "tomato" not "Solanum lycopersicum")
- Be specific where possible (e.g., "red bell pepper" not just "vegetable")
- If the image is unclear or not food-related, set confidence to "low" and explain in message
- Include at least the most prominent items even if unsure
"""


async def detect_ingredients(
    image_base64: str,
    max_retries: int = 2,
) -> dict:
    """
    Detect food ingredients from a base64-encoded image using Gemini Vision.
    
    Args:
        image_base64: Base64-encoded image (with or without data URI prefix)
        max_retries: Number of retry attempts on failure
    
    Returns:
        Dict with detected_ingredients list, confidence, and message
    
    Raises:
        ValueError: If detection fails after all retries
    """
    settings = get_settings()
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)

    # Decode the image
    try:
        image_bytes = decode_base64_image(image_base64)
        mime_type = get_image_mime_type(image_base64)
    except Exception as e:
        raise ValueError(f"Invalid image data: {e}")

    # Validate image by attempting to open with Pillow
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
    except Exception as e:
        raise ValueError(f"Corrupted or unsupported image format: {e}")

    last_error: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Ingredient detection attempt {attempt}/{max_retries}")

            # Build the image part for Gemini
            image_part = {
                "mime_type": mime_type,
                "data": image_bytes,
            }

            # Send image + prompt to Gemini Vision
            response = await asyncio.to_thread(
                model.generate_content, [DETECTION_PROMPT, image_part]
            )
            response_text = response.text.strip()

            # Parse JSON from response
            result = extract_json(response_text)

            if result is None:
                raise ValueError(f"Could not parse detection results: {response_text[:200]}")

            if "detected_ingredients" not in result:
                raise ValueError("Response missing 'detected_ingredients' field")

            # Ensure we have a list
            ingredients = result["detected_ingredients"]
            if isinstance(ingredients, str):
                ingredients = [i.strip() for i in ingredients.split(",") if i.strip()]
                result["detected_ingredients"] = ingredients

            logger.info(f"Detected {len(ingredients)} ingredients: {ingredients}")
            return result

        except Exception as e:
            last_error = e
            logger.warning(f"Detection attempt {attempt} failed: {e}")

            if attempt < max_retries:
                await asyncio.sleep(1)

    raise ValueError(
        f"Failed to detect ingredients after {max_retries} attempts. "
        f"Last error: {last_error}"
    )
