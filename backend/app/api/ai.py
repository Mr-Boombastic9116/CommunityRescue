from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.api.deps import get_current_user, require_roles
from app.services.ai_service import AIService, FoodCategorizationAIResponse
from app.core.config import settings

router = APIRouter(prefix="/ai", tags=["Hosted Gemma AI"])

class FoodCategorizeRequest(BaseModel):
    food_name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    reply: str
    role: str
    user_name: str
    ai_powered: bool

@router.get("/status")
def get_ai_status():
    """
    Returns the operational status of the hosted Gemma 4 AI integration.
    """
    available = AIService.is_available()
    return {
        "status": "online" if available else "offline_fallback",
        "model": settings.GEMMA_MODEL,
        "provider": "Google Gemma 4 Hosted (Gemini API)",
        "sdk": "google-genai",
        "ai_available": available,
    }

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

@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Role-aware AI chatbot for Donors, NGOs, and Volunteers.
    Supplies authorized user-specific data into the prompt context.
    Never exposes another user's private data or invents records.
    """
    reply = AIService.chat_with_assistant(
        db=db,
        user=current_user,
        user_message=payload.message,
    )
    return ChatResponse(
        reply=reply,
        role=current_user.role,
        user_name=current_user.name,
        ai_powered=AIService.is_available(),
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

