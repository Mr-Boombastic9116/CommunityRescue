from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# 1. FOOD CATEGORIZATION SCHEMAS
# -----------------------------------------------------------------------------
class FoodCategorizeRequest(BaseModel):
    food_name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

class FoodCategorizationAIResponse(BaseModel):
    normalized_name: str = Field(..., description="Cleaned, normalized food name")
    suggested_category: str = Field(..., description="Suggested food category")
    suggested_storage: str = Field("ambient", description="Recommended storage condition: ambient, refrigerated, frozen, hot_holding")
    food_state: str = Field("cooked", description="Type: cooked, raw, packaged, bakery, beverage")
    concise_description: str = Field(..., description="Appetizing, clear 1-2 sentence description")
    allergens: List[str] = Field(default_factory=list, description="Potential food allergens identified")
    ai_powered: bool = True

# -----------------------------------------------------------------------------
# 2. MULTIMODAL IMAGE RECOGNITION SCHEMAS
# -----------------------------------------------------------------------------
class DetectedFoodItem(BaseModel):
    item_index: int = Field(1, description="Sequential index of detected food item")
    food_name: str = Field(..., description="Identified food item name")
    food_category: str = Field(..., description="Category: Cooked Meals, Raw Food/Produce, Bakery & Bread, Packaged & Canned, Dairy & Refrigerated, Beverages")
    short_description: str = Field(..., description="Concise visual description based only on the image")
    visible_ingredients: List[str] = Field(default_factory=list, description="Clearly visible ingredients only")
    food_type: str = Field("cooked", description="Type: cooked, raw, packaged, bakery, beverage")
    suggested_storage: str = Field("ambient", description="Suggested storage condition: ambient, refrigerated, frozen, hot_holding")
    confidence_score: float = Field(0.9, ge=0.0, le=1.0)
    confidence_level: str = Field("high", description="'high', 'medium', or 'low'")
    review_warning: Optional[str] = Field(None, description="Warning if lighting is poor, blurry, or food is ambiguous")

class MultiFoodRecognitionResponse(BaseModel):
    image_url: Optional[str] = None
    detected_items: List[DetectedFoodItem]
    total_items_detected: int
    overall_notes: Optional[str] = None
    ai_powered: bool = True

# -----------------------------------------------------------------------------
# 3. AUTOMATIC DESCRIPTION GENERATION SCHEMAS
# -----------------------------------------------------------------------------
class FoodDescriptionRequest(BaseModel):
    food_name: str = Field(..., min_length=2, max_length=255)
    food_category: Optional[str] = Field("Cooked Meals")
    confirmed_ingredients: Optional[List[str]] = Field(default_factory=list)
    storage_condition: Optional[str] = Field("ambient")
    donor_notes: Optional[str] = Field(None, max_length=1000)
    image_context: Optional[str] = Field(None, max_length=1000)

class FoodDescriptionResponse(BaseModel):
    professional_title: str
    detailed_description: str
    category: str
    listing_summary: str
    handling_notes: Optional[str] = None
    ai_powered: bool = True

# -----------------------------------------------------------------------------
# 4. INTENT-AWARE CHATBOT SCHEMAS
# -----------------------------------------------------------------------------
class ChatbotParsedIntent(BaseModel):
    intent: str = Field(..., description="Identified intent: explain_donation_workflow, search_food, list_my_requests, list_my_donations, cancel_request, list_expiring_donations, find_eligible_pickups, view_profile, general_query")
    question_type: str = Field("informational", description="informational, action_request, clarification, greeting")
    action: Optional[str] = Field(None, description="search, cancel, list, prioritize, claim")
    main_entity: Optional[str] = Field(None, description="Main entity/noun mentioned, e.g. rice, request, donation")
    extracted_entities: Dict[str, Any] = Field(default_factory=dict, description="Parsed entities")
    quantity: Optional[float] = Field(None, description="Numerical quantity if mentioned")
    unit: Optional[str] = Field(None, description="Unit of measurement if mentioned")
    relevant_ids: List[int] = Field(default_factory=list, description="IDs referenced or resolved from history")
    missing_information: List[str] = Field(default_factory=list, description="Fields required to fulfill request")
    backend_action_needed: bool = Field(False, description="True if backend tool execution is needed")
    confirmation_required: bool = Field(False, description="True if dangerous action like cancel or claim requires confirmation")
    confirmation_prompt: Optional[str] = Field(None, description="Question to ask user for confirmation")

class IntentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    history: List[Dict[str, str]] = Field(default_factory=list, description="Past messages with role and content")
    confirmed_action: Optional[bool] = Field(None, description="True if user is confirming a pending action")
    pending_action_data: Optional[Dict[str, Any]] = Field(None, description="Data of action being confirmed")

class IntentChatResponse(BaseModel):
    reply: str
    parsed_intent: ChatbotParsedIntent
    tool_executed: Optional[str] = None
    tool_results_count: Optional[int] = None
    role: str
    user_name: str
    ai_powered: bool = True

# -----------------------------------------------------------------------------
# 5. EXPIRY AUTOFILL & CALCULATION SCHEMAS
# -----------------------------------------------------------------------------
class CalculateExpiryRequest(BaseModel):
    food_name: str
    food_category: str
    storage_condition: str = "ambient"
    prepared_at: str  # ISO datetime string
    storage_temperature: Optional[float] = None
    packaging_expiry: Optional[str] = None  # ISO datetime string

class CalculateExpiryResponse(BaseModel):
    food_category: str
    storage_condition: str
    max_holding_hours: Optional[float]
    approved_maximum_expiry: Optional[str]
    rule_applied: Optional[str]
    rule_source: Optional[str]
    rule_clause: Optional[str]
    requires_manual_verification: bool
    verification_reason: Optional[str] = None
