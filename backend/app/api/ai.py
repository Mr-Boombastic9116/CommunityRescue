import os
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.api.deps import get_current_user, require_roles
from app.services.ai_service import AIService
from app.core.config import settings
from app.schemas.ai import (
    FoodCategorizeRequest,
    FoodCategorizationAIResponse,
    ChatbotParsedIntent,
    IntentChatRequest,
    IntentChatResponse,
)

router = APIRouter(prefix="/ai", tags=["Hosted Gemma AI"])

@router.get("/status")
def get_ai_status():
    """
    Returns operational status of the hosted Gemma 4 AI integration.
    """
    available = AIService.is_available()
    return {
        "status": "online" if available else "offline_fallback",
        "model": settings.GEMMA_MODEL or "gemma-4-26b-a4b-it",
        "provider": "Google Gemma 4 Hosted (Gemini API)",
        "sdk": "google-genai",
        "ai_available": available,
    }

# -----------------------------------------------------------------------------
# TEXT CATEGORIZATION & NORMALIZATION
# -----------------------------------------------------------------------------
@router.post("/categorize-food", response_model=FoodCategorizationAIResponse)
def categorize_food(
    payload: FoodCategorizeRequest,
    current_user: User = Depends(require_roles(["donor"])),
):
    """
    Hosted Gemma 4 service that analyzes a food donation, normalizes the title,
    suggests appropriate category, storage conditions, and generates a concise description.
    """
    return AIService.categorize_food(
        food_name=payload.food_name,
        raw_description=payload.description,
    )

# -----------------------------------------------------------------------------
# INTENT-AWARE CHATBOT & TOOL ROUTING (Requirement D)
# -----------------------------------------------------------------------------
@router.post("/chat", response_model=IntentChatResponse)
def chat_with_assistant(
    payload: IntentChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Intent-aware Gemma 4 chatbot: parses intent, extracts entities and quantities,
    executes authenticated backend tools against real MySQL data,
    resolves conversational history references, and enforces confirmation for actions.
    """
    return AIService.intent_aware_chat(
        db=db,
        user=current_user,
        message=payload.message,
        history=payload.history,
        confirmed_action=payload.confirmed_action,
        pending_action_data=payload.pending_action_data,
    )

@router.get("/match-food")
def match_food_for_ngo(
    current_user: User = Depends(require_roles(["ngo"])),
    db: Session = Depends(get_db),
):
    """
    Smart NGO-food matching: deterministically filters real available surplus batches
    and uses Gemma to explain recommendations and rank candidates.
    """
    return AIService.match_food_for_ngo(db=db, ngo_user=current_user)

@router.get("/prioritize-tasks")
def prioritize_tasks(
    current_user: User = Depends(require_roles(["volunteer"])),
    db: Session = Depends(get_db),
):
    """
    Pickup prioritization for volunteers: calculates expiry urgency deterministically
    and provides clear explanations why tasks are prioritized.
    """
    return AIService.prioritize_volunteer_tasks(db=db, volunteer=current_user)
