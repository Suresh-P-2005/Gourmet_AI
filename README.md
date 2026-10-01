# Gourmet AI Recipe Generator 🍳

A modern, production-ready AI-powered recipe generation system built with FastAPI, Gemini AI, and a premium Glassmorphism UI.

## Features

- **🧠 Smart Recipe Generation**: Powered by Google's Gemini AI with an automatic multi-provider fallback to Groq (`openai/gpt-oss-20b`) for high resilience.
- **📷 Camera Ingredient Detection**: Automatically detect ingredients from camera photos using Gemini Vision API, gracefully falling back to Groq (`qwen/qwen3.8-27b`) when quotas are exhausted.
- **🎤 Voice Input**: Hands-free ingredient entry using the Web Speech API.
- **🎨 Premium UI**: Glassmorphism design, dark mode, smooth animations, and responsive layout.
- **💾 Recipe History**: Save and manage your favorite AI-generated recipes with PostgreSQL persistence and atomic database transactions.
- **⚡ Async FastAPI Backend**: High-performance asynchronous backend with Pydantic validation and rate-limit handling (Exponential Backoff).
- **✅ Automated Testing**: Comprehensive asynchronous unit testing suite using `pytest` and `httpx`.

## Prerequisites

- Python 3.10+
- A Google Gemini API Key
- A Groq API Key (for failover models)

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
    - Replace the placeholder API keys with your actual keys.
    ```env
    GEMINI_API_KEY=your_gemini_api_key
    GEMINI_MODEL=gemini-flash-latest
    GROQ_API_KEY=your_groq_api_key
    DEBUG=true
    CORS_ORIGINS=*
    DATABASE_URL=postgresql://user:password@localhost:5432/recipes
    ```

    > **Render Deployment Note**: When deploying on Render, you must use the **Internal Database URL** if your FastAPI service and PostgreSQL instance are in the same Render environment. If they are in different environments or you are connecting locally, use the **External Database URL**. Our application is automatically configured to handle Render's SSL requirements for external connections!

## Running the Application

Start the FastAPI development server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

- **Frontend App**: [http://localhost:8000/](http://localhost:8000/)
- **API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Running Tests

Execute the asynchronous test suite locally:
```bash
pytest tests/ -v
```

## Project Architecture

```
receipe/
│
├── alembic/                 # Alembic migrations folder
├── alembic.ini              # Alembic config file
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── database.py              # PostgreSQL pool & setup with asyncpg
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
│   │   └── recipe_db_service.py # PostgreSQL CRUD ops
│   │
│   ├── models/                  # Request/Response Pydantic schemas
│   └── utils/                   # JSON parsing & helpers
│
├── frontend/
│   ├── index.html               # Main UI
│   ├── style.css                # Glassmorphism & Dark Mode CSS
│   └── app.js                   # Client-side logic, camera, throttle/debounce
│
├── tests/
│   └── test_recipe_api.py       # Asynchronous pytest cases
│
├── static/                      # Static assets folder
├── .env                         # Secrets
└── requirements.txt             # Python dependencies
```

## Technologies Used

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Google Generative AI SDK](https://github.com/google/generative-ai-python) - LLM integration
- [Groq SDK](https://github.com/groq/groq-python) - Ultra-fast LLM fallback APIs
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [asyncpg](https://magicstack.github.io/asyncpg/current/) - High-performance async PostgreSQL driver
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [Pytest](https://docs.pytest.org/) & [HTTPX](https://www.python-httpx.org/) - Async Testing

**Frontend:**
- HTML5 / CSS3 / Vanilla JavaScript
- WebRTC (getUserMedia API) for Camera
- Web Speech API for Voice recognition

---
*Built with ❤️ using Antigravity AI Assistant.*
