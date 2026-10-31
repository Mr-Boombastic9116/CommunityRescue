import pytest
import uuid
from app.services.ai_service import AIService, FoodCategorizationAIResponse

def create_user(client, role, name):
    email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "name": name,
        "email": email,
        "password": "Password123!",
        "role": role,
        "phone": "+91 9123456789",
        "address": "Test Address",
        "organization_name": name,
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201, res.text
    return res.json()["access_token"]

def test_ai_status_endpoint(client):
    res = client.get("/api/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "model" in data
    assert "gemma-4" in data["model"]

def test_ai_categorize_endpoint(client):
    token = create_user(client, "donor", "AI Test Donor")
    res = client.post(
        "/api/ai/categorize-food",
        json={
            "food_name": "Vegetable Biryani with Raita",
            "description": "Cooked 50 portions of mixed vegetable biryani with fresh yogurt raita.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert "suggested_category" in data
    assert "suggested_storage" in data
    assert "normalized_name" in data
    assert "concise_description" in data

def test_ai_fallback_resilience():
    fallback = AIService._fallback_categorize("Hot Paneer Gravy", "Contains dairy")
    assert isinstance(fallback, FoodCategorizationAIResponse)
    assert fallback.suggested_category in [
        "Cooked Meals",
        "Raw Food/Produce",
        "Bakery & Bread",
        "Packaged & Canned",
        "Dairy & Refrigerated",
        "Beverages",
        "Fresh Produce",
        "Packaged Foods",
    ]
    assert fallback.suggested_storage in ["ambient", "refrigerated", "frozen", "hot_holding"]
    assert fallback.normalized_name is not None
    assert fallback.concise_description is not None

def test_ai_chat_endpoint(client):
    token = create_user(client, "donor", "Chat Donor")
    res = client.post(
        "/api/ai/chat",
        json={
            "message": "What is the maximum allowed room temperature storage time for cooked rice?",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
