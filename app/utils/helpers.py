"""
Helper utilities — base64 handling, input normalization, and formatting.
"""

import base64
import re
from typing import Optional


def decode_base64_image(data: str) -> bytes:
    """
    Decode a base64 image string to raw bytes.
    Handles both plain base64 and data-URI format (data:image/jpeg;base64,...).
    """
    # Strip data URI prefix if present
    if "," in data and data.startswith("data:"):
        data = data.split(",", 1)[1]

    # Remove any whitespace / newlines
    data = data.strip().replace("\n", "").replace("\r", "")

    return base64.b64decode(data)


def get_image_mime_type(data: str) -> str:
    """
    Detect MIME type from a base64 data URI or raw base64 bytes.
    Defaults to 'image/jpeg' if detection fails.
    """
    if data.startswith("data:"):
        # Extract from data URI
        match = re.match(r"data:(image/\w+);base64,", data)
        if match:
            return match.group(1)

    # Try to detect from magic bytes
    try:
        raw = base64.b64decode(data[:32] if "," not in data else data.split(",")[1][:32])
        if raw[:4] == b"\x89PNG":
            return "image/png"
        if raw[:2] == b"\xff\xd8":
            return "image/jpeg"
        if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
            return "image/webp"
    except Exception:
        pass

    return "image/jpeg"


def sanitize_ingredients(text: str) -> str:
    """
    Normalize an ingredient input string.
    Strips excess whitespace and ensures clean comma separation.
    """
    if not text:
        return ""

    # Split by commas or newlines, clean each part
    parts = re.split(r"[,\n]+", text)
    cleaned = [part.strip() for part in parts if part.strip()]
    return ", ".join(cleaned)


def format_duration(seconds: float) -> str:
    """Format seconds into a human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}m"
    hours = minutes / 60
    return f"{hours:.1f}h"
