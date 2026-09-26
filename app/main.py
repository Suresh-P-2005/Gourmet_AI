"""
Gourmet AI Recipe Generator — FastAPI Application Entry Point.

A modern, production-ready AI-powered recipe generation system with:
- Gemini AI recipe generation
- Camera-based ingredient detection via Gemini Vision
- Voice input support
- Recipe history with SQLite persistence
- Premium glassmorphism UI with dark mode

Run with:  uvicorn app.main:app --reload
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.database import init_db

# ── Import route modules ──────────────────────────────────────────────────────
from app.api.routes import health, recipe, vision

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent  # project root
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = BASE_DIR / "static"


# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    settings = get_settings()
    logger.info(f"🚀 Starting {settings.APP_TITLE} v{settings.APP_VERSION}")
    logger.info(f"📦 Gemini model: {settings.GEMINI_MODEL}")
    logger.info(f"🔑 API Key configured: {settings.GEMINI_API_KEY != 'your_gemini_api_key_here'}")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Ensure static directory exists
    STATIC_DIR.mkdir(exist_ok=True)

    yield

    logger.info("👋 Shutting down Gourmet AI")


# ── FastAPI App ────────────────────────────────────────────────────────────────
settings = get_settings()

app = FastAPI(
    title=settings.APP_TITLE,
    description=(
        "AI-powered recipe generation with camera-based ingredient detection, "
        "voice input, and recipe history. Built with FastAPI + Gemini AI."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware ────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount Static Files ─────────────────────────────────────────────────────────
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── Register API Routes ───────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(recipe.router)
app.include_router(vision.router)


# ── Serve Frontend ─────────────────────────────────────────────────────────────
@app.get("/app.js", include_in_schema=False)
async def serve_js():
    """Serve the frontend JavaScript file."""
    return FileResponse(
        str(FRONTEND_DIR / "app.js"),
        media_type="application/javascript",
    )


@app.get("/style.css", include_in_schema=False)
async def serve_css():
    """Serve the frontend CSS file."""
    return FileResponse(
        str(FRONTEND_DIR / "style.css"),
        media_type="text/css",
    )

@app.get("/preview.png", include_in_schema=False)
async def serve_preview():
    """Serve the Open Graph preview image."""
    return FileResponse(
        str(FRONTEND_DIR / "preview.png"),
        media_type="image/png",
    )


@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the main frontend HTML page."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    return HTMLResponse(
        content="<h1>Frontend not found</h1><p>Place index.html in the frontend/ directory.</p>",
        status_code=404,
    )
