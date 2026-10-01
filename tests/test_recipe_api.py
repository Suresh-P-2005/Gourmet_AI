import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

# Import your FastAPI app instance
from app.main import app 
from app.api.routes.auth import get_current_user
from app.models.response_models import UserResponse

# Ensure pytest uses anyio (compatible with FastAPI)
pytestmark = pytest.mark.anyio

@pytest.fixture
def anyio_backend():
    return 'asyncio'

async def override_get_current_user():
    return UserResponse(id=1, username="testuser", email="test@example.com")

# Override auth dependency globally for these tests
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture
async def async_client():
    """Provides an async HTTP client for FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@patch("app.api.routes.recipe.ai_service.generate_recipe")
async def test_generate_recipe_success(mock_generate, async_client):
    """Test successful recipe generation with mocked AI response."""
    mock_generate.return_value = {
        "title": "Mocked Garlic Chicken",
        "cuisine": "Italian",
        "dietary": "",
        "ingredients": ["1 lb chicken", "2 cloves garlic"],
        "instructions": ["Cook chicken", "Add garlic"],
        "token_usage": {"input": 10, "output": 20, "total": 30, "provider": "gemini"}
    }

    payload = {"ingredients": "chicken, garlic", "cuisine": "Italian"}
    response = await async_client.post("/api/recipe/generate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["recipe"]["title"] == "Mocked Garlic Chicken"
    
    mock_generate.assert_called_once_with(
        ingredients="chicken, garlic", 
        cuisine="Italian", 
        dietary=""
    )

@patch("app.api.routes.recipe.ai_service.generate_recipe")
async def test_generate_recipe_ai_failure(mock_generate, async_client):
    """Test endpoint behavior when the AI service completely fails."""
    mock_generate.side_effect = ValueError("Failed to generate recipe after 3 attempts.")

    payload = {"ingredients": "rocks, dirt"}
    response = await async_client.post("/api/recipe/generate", json=payload)

    assert response.status_code == 500
    data = response.json()
    assert "Failed to generate recipe" in data["detail"]

@patch("app.api.routes.recipe.recipe_db_service.save_recipe")
async def test_save_recipe_success(mock_save_db, async_client):
    """Test saving a recipe with authenticated user."""
    mock_save_db.return_value = 42

    payload = {
        "title": "Delicious Pasta",
        "ingredients": ["Pasta", "Sauce"],
        "instructions": ["Boil water", "Eat"]
    }
    
    response = await async_client.post("/api/recipe/save", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["id"] == 42
    # Check that it called save_recipe with user_id = 1
    mock_save_db.assert_called_once()
    assert mock_save_db.call_args[0][1] == 1

@patch("app.api.routes.recipe.recipe_db_service.get_user_vault_recipes")
async def test_get_personal_vault(mock_get_vault, async_client):
    """Test retrieving personal vault recipes."""
    mock_get_vault.return_value = ([{
        "id": 1, 
        "title": "My Recipe",
        "ingredients": ["item1"],
        "instructions": ["step1"]
    }], 1)

    response = await async_client.get("/api/recipe/vault")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["recipes"]) == 1
    assert data["total"] == 1
    mock_get_vault.assert_called_once_with(1, limit=20, offset=0)

@patch("app.api.routes.recipe.recipe_db_service.get_community_recipes")
async def test_get_community_feed(mock_get_community, async_client):
    """Test retrieving community feed recipes."""
    mock_get_community.return_value = ([{
        "id": 2, 
        "title": "Community Recipe",
        "ingredients": ["item1"],
        "instructions": ["step1"]
    }], 1)

    response = await async_client.get("/api/recipe/community?cuisine=Italian")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["recipes"]) == 1
    mock_get_community.assert_called_once_with(20, 0, "Italian", None)

@patch("app.api.routes.recipe.recipe_db_service.bookmark_recipe")
async def test_bookmark_recipe(mock_bookmark, async_client):
    """Test bookmarking a community recipe."""
    mock_bookmark.return_value = True

    response = await async_client.post("/api/recipe/99/save")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    mock_bookmark.assert_called_once_with(99, 1)

@patch("app.api.routes.recipe.recipe_db_service.toggle_recipe_visibility")
async def test_toggle_visibility(mock_toggle, async_client):
    """Test toggling public/private visibility."""
    mock_toggle.return_value = True

    response = await async_client.put("/api/recipe/99/visibility?is_public=true")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    mock_toggle.assert_called_once_with(99, 1, True)

@patch("app.api.routes.recipe.recipe_db_service.delete_recipe")
async def test_delete_recipe(mock_delete, async_client):
    """Test deleting a recipe."""
    mock_delete.return_value = True

    response = await async_client.delete("/api/recipe/99")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    mock_delete.assert_called_once_with(99, 1)
