import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

# Import your FastAPI app instance
from app.main import app 

# Ensure pytest uses asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
async def async_client():
    """Provides an async HTTP client for FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@patch("app.api.routes.recipe.ai_service.generate_recipe")
async def test_generate_recipe_success(mock_generate, async_client):
    """Test successful recipe generation with mocked Gemini/Groq response."""
    
    # 1. Mock the AI service to return a predictable dictionary
    mock_generate.return_value = {
        "title": "Mocked Garlic Chicken",
        "cuisine": "Italian",
        "dietary": "",
        "ingredients": ["1 lb chicken", "2 cloves garlic"],
        "instructions": ["Cook chicken", "Add garlic"],
        "token_usage": {"input": 10, "output": 20, "total": 30, "provider": "gemini"}
    }

    # 2. Make the request
    payload = {"ingredients": "chicken, garlic", "cuisine": "Italian"}
    response = await async_client.post("/api/recipe/generate", json=payload)

    # 3. Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["recipe"]["title"] == "Mocked Garlic Chicken"
    assert data["recipe"]["token_usage"]["provider"] == "gemini"
    
    # Ensure our mock was called with sanitized inputs
    mock_generate.assert_called_once_with(
        ingredients="chicken, garlic", 
        cuisine="Italian", 
        dietary=""
    )

@patch("app.api.routes.recipe.ai_service.generate_recipe")
async def test_generate_recipe_ai_failure(mock_generate, async_client):
    """Test endpoint behavior when the AI service completely fails."""
    
    # 1. Mock the AI service to raise an exception (simulating exhausted retries)
    mock_generate.side_effect = ValueError("Failed to generate recipe after 3 attempts.")

    # 2. Make the request
    payload = {"ingredients": "rocks, dirt"}
    response = await async_client.post("/api/recipe/generate", json=payload)

    # 3. Assertions
    assert response.status_code == 500
    data = response.json()
    assert "Failed to generate recipe" in data["detail"]

@patch("app.api.routes.recipe.recipe_db_service.save_recipe")
async def test_save_recipe_success(mock_save_db, async_client):
    """Test saving a recipe with a mocked database layer."""
    
    # 1. Mock the DB service to return a fake primary key ID
    mock_save_db.return_value = 42

    # 2. Payload matches SaveRecipeRequest Pydantic model
    payload = {
        "title": "Delicious Pasta",
        "ingredients": ["Pasta", "Sauce"],
        "instructions": ["Boil water", "Eat"]
    }
    
    response = await async_client.post("/api/recipe/save", json=payload)

    # 3. Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["id"] == 42
    mock_save_db.assert_called_once()
