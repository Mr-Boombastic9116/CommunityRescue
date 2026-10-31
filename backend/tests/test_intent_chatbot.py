import uuid
from datetime import datetime, timedelta
import pytest
from app.services.ai_service import ai_service

def register_user(client, role="ngo"):
    unique_email = f"{role}_{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "name": f"Test {role.upper()}",
        "email": unique_email,
        "password": "Password123!",
        "role": role,
        "phone": "+91 9988776655",
        "address": "City Square",
    }
    res = client.post("/api/auth/register", json=payload)
    return res.json()["access_token"], unique_email

def test_intent_parsing_rules():
    # Test general or safety question
    intent1 = ai_service.parse_intent("What is the maximum holding time for hot cooked sambar?")
    assert intent1.intent in ["food_safety_question", "general_query", "general_question"]

    # Test search intent
    intent2 = ai_service.parse_intent("Are there any rice or bread donations available?")
    assert intent2.intent in ["search_food", "general_query"]

    # Test list expiring donations intent
    intent3 = ai_service.parse_intent("Show me donations expiring soon")
    assert intent3.intent in ["list_expiring_donations", "general_query"]

    # Test volunteer pickups intent
    intent4 = ai_service.parse_intent("What pickup tasks can I claim today?")
    assert intent4.intent in ["find_eligible_pickups", "general_query"]

    # Test sensitive action requiring confirmation
    intent5 = ai_service.parse_intent("Cancel request 101 immediately")
    assert intent5.confirmation_required is True
    assert intent5.intent == "cancel_request"

def test_chat_endpoint_with_intent_routing(client):
    token, email = register_user(client, "ngo")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "message": "Which food batches are expiring soonest?",
        "history": [],
    }
    res = client.post("/api/ai/chat", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert "parsed_intent" in data
    assert "intent" in data["parsed_intent"]

def test_chat_confirmation_workflow(client):
    token, email = register_user(client, "ngo")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "message": "Cancel my donation claim #999",
        "history": [],
    }
    res = client.post("/api/ai/chat", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["parsed_intent"]["confirmation_required"] is True
    assert "confirm" in data["reply"].lower() or "cancel" in data["reply"].lower()
