"""
Vision API routes — camera-based ingredient detection.
"""

import logging
from fastapi import APIRouter, HTTPException, Request
from app.models.request_models import VisionDetectRequest
from app.models.response_models import VisionDetectResponse, ErrorResponse
from app.services import vision_service
from app.core.security import rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vision", tags=["Vision"])


@router.post(
    "/detect",
    response_model=VisionDetectResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Detect Ingredients from Image",
    description="Upload a camera-captured image (base64) and get a list of detected food ingredients using Gemini Vision.",
)
async def detect_ingredients(request: Request, body: VisionDetectRequest):
    """Detect food ingredients from a camera-captured image."""
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check(client_ip)

    if not body.image:
        raise HTTPException(status_code=400, detail="No image data provided.")

    try:
        result = await vision_service.detect_ingredients(image_base64=body.image)

        return VisionDetectResponse(
            success=True,
            detected_ingredients=result.get("detected_ingredients", []),
            confidence=result.get("confidence", "medium"),
            message=result.get("message", ""),
        )

    except ValueError as e:
        logger.error(f"Vision detection error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected vision error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze the image. Please try again with a clearer photo.",
        )
