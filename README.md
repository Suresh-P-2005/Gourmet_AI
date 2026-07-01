# Gourmet AI Recipe Generator 🍳

A modern, production-ready AI-powered recipe generation system built with FastAPI, Gemini AI, and a premium Glassmorphism UI.

## Features

- **🧠 Smart Recipe Generation**: Powered by Google's Gemini 2.0 Flash AI.
- **📷 Camera Ingredient Detection**: Automatically detect ingredients from camera photos using Gemini Vision API.
- **🎤 Voice Input**: Hands-free ingredient entry using the Web Speech API.
- **🎨 Premium UI**: Glassmorphism design, dark mode, smooth animations, and responsive layout.
- **💾 Recipe History**: Save and manage your favorite AI-generated recipes with local SQLite persistence.
- **⚡ Async FastAPI Backend**: High-performance asynchronous backend with Pydantic validation.

## Prerequisites

- Python 3.10+
- A Google Gemini API Key

## Setup & Installation

1. **Clone the repository** (if you haven't already):
    ```bash
    git clone <your-repo-url>
    cd receipe
    ```

2. **Set up a virtual environment** (recommended):
    ```bash
    python -m venv venv
    
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Environment Variables**:
    - Open the `.env` file in the root directory.
    - Replace `your_gemini_api_key_here` with your actual Gemini API key.
    ```env
    GEMINI_API_KEY=your_actual_api_key
    GEMINI_MODEL=gemini-2.0-flash
    DEBUG=true
    CORS_ORIGINS=*
    DATABASE_URL=sqlite:///./recipes.db
    ```

## Running the Application

Start the FastAPI development server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

- **Frontend App**: [http://localhost:8000/](http://localhost:8000/)
- **API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Project Architecture

```
receipe/
│
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── database.py              # SQLite setup with aiosqlite
│   │
│   ├── core/
│   │   ├── config.py            # Pydantic Settings (loads .env)
│   │   └── security.py          # Rate limiting
│   │
│   ├── api/routes/
│   │   ├── recipe.py            # Generate & Save Recipe APIs
│   │   ├── vision.py            # Camera Detection API
│   │   └── health.py            # System Health
│   │
│   ├── services/
│   │   ├── ai_service.py        # Gemini recipe text generation
│   │   ├── vision_service.py    # Gemini Vision processing
│   │   └── recipe_db_service.py # SQLite CRUD ops
│   │
│   ├── models/                  # Request/Response Pydantic schemas
│   └── utils/                   # JSON parsing & helpers
│
├── frontend/
│   ├── index.html               # Main UI
│   ├── style.css                # Glassmorphism & Dark Mode CSS
│   └── app.js                   # Client-side logic & camera capture
│
├── static/                      # Static assets folder
├── .env                         # Secrets
└── requirements.txt             # Python dependencies
```

## Technologies Used

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Google Generative AI SDK](https://github.com/google/generative-ai-python) - LLM integration
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [aiosqlite](https://github.com/omnilib/aiosqlite) - Async SQLite

**Frontend:**
- HTML5 / CSS3 / Vanilla JavaScript
- WebRTC (getUserMedia API) for Camera
- Web Speech API for Voice recognition

---
*Built with ❤️ using Antigravity AI Assistant.*
