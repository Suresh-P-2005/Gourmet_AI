"""
JSON parser — robust extraction of structured data from AI responses.
Handles markdown code fences, partial JSON, and malformed output.
"""

import json
import re
from typing import Any, Optional


def extract_json(text: str) -> Optional[dict[str, Any]]:
    """
    Extract a JSON object from AI response text.
    
    Handles common cases:
    - Clean JSON
    - JSON wrapped in ```json ... ``` code fences
    - JSON wrapped in ``` ... ``` code fences
    - JSON embedded in surrounding text
    """
    if not text or not text.strip():
        return None

    cleaned = text.strip()

    # Strategy 1: Remove markdown code fences
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

    # Strategy 2: Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Find the first { ... } block via regex
    try:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass

    # Strategy 4: Try to find JSON array and wrap it
    try:
        match = re.search(r"\[[\s\S]*\]", cleaned)
        if match:
            return {"items": json.loads(match.group())}
    except json.JSONDecodeError:
        pass

    return None


def validate_recipe_structure(data: dict) -> bool:
    """
    Validate that a parsed JSON object has the required recipe fields.
    Returns True if valid, False otherwise.
    """
    required_keys = ["title", "ingredients", "instructions"]
    return all(key in data for key in required_keys)


def safe_get_list(data: dict, key: str, default: list = None) -> list:
    """Safely extract a list value from a dict, handling string values."""
    if default is None:
        default = []
    value = data.get(key, default)
    if isinstance(value, str):
        # Try to split comma-separated string
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, list):
        return value
    return default
