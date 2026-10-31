import os
import json
import logging
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.config import settings
from app.models.user import User
from app.models.food_batch import FoodBatch
from app.models.pickup_request import PickupRequest
from app.models.ngo import NGOPartner
from app.models.donor import Donor
from app.models.volunteer import Volunteer
from app.utils.dates import utc_now, to_naive_utc

from app.schemas.ai import (
    FoodCategorizationAIResponse,
    ChatbotParsedIntent,
    IntentChatResponse,
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# PYDANTIC HELPER SCHEMAS
# -----------------------------------------------------------------------------
class MatchExplanation(BaseModel):
    batch_id: int
    food_name: str
    match_score: int = Field(..., ge=1, le=100)
    recommendation_reason: str
    urgency_level: str

class TaskPrioritizationItem(BaseModel):
    request_id: int
    food_name: str
    priority_level: str
    dispatch_order: int
    rationale: str

# -----------------------------------------------------------------------------
# AI SERVICE IMPLEMENTATION WITH GEMMA 4
# -----------------------------------------------------------------------------
class AIService:
    _client = None

    @classmethod
    def get_client(cls):
        api_key = settings.ai_api_key
        if not api_key:
            return None
        if cls._client is None:
            try:
                from google import genai
                cls._client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.warning(f"[AIService] Failed to initialize google-genai Client: {e}")
                return None
        return cls._client

    @classmethod
    def is_available(cls) -> bool:
        return bool(settings.ai_api_key)

    @classmethod
    def call_gemma(
        cls,
        prompt: str,
        system_instruction: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = "image/jpeg",
        json_mode: bool = False,
    ) -> Optional[str]:
        client = cls.get_client()
        if not client:
            return None

        model_id = settings.GEMMA_MODEL or "gemma-4-26b-a4b-it"
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1500,
            )
            if system_instruction:
                config.system_instruction = system_instruction
            if json_mode:
                config.response_mime_type = "application/json"

            contents: List[Any] = []
            if image_bytes:
                part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type or "image/jpeg")
                contents.append(part)
            contents.append(prompt)

            response = client.models.generate_content(
                model=model_id,
                contents=contents,
                config=config,
            )
            return response.text
        except Exception as e:
            logger.error(f"[AIService] Gemma API call failed: {e}")
            return None

    # -------------------------------------------------------------------------
    # TEXT CATEGORIZATION & NORMALIZATION
    # -------------------------------------------------------------------------
    @classmethod
    def categorize_food(cls, food_name: str, raw_description: Optional[str] = None) -> FoodCategorizationAIResponse:
        system_prompt = (
            "You are an expert food logistics and safety assistant. "
            "Given a food donation title and optional description, return valid JSON with: "
            "normalized_name (str), suggested_category (one of: 'Cooked Meals', 'Bakery & Bread', 'Fresh Produce', 'Beverages', 'Packaged Foods', 'Dairy & Refrigerated', 'Raw Food/Produce'), "
            "suggested_storage (one of: 'ambient', 'refrigerated', 'frozen', 'hot_holding'), "
            "food_state (one of: 'cooked', 'raw', 'packaged', 'bakery', 'beverage'), "
            "concise_description (str, 1-2 sentences), "
            "allergens (list of strings). "
            "Respond ONLY with valid JSON."
        )

        user_content = f"Food Name: {food_name}\nDescription: {raw_description or 'No extra details provided'}"
        raw_json = cls.call_gemma(prompt=user_content, system_instruction=system_prompt, json_mode=True)
        if raw_json:
            try:
                clean_json = raw_json.strip()
                if clean_json.startswith("```"):
                    clean_json = clean_json.split("\n", 1)[1]
                    if clean_json.endswith("```"):
                        clean_json = clean_json.rsplit("\n", 1)[0]
                data = json.loads(clean_json)
                data["ai_powered"] = True
                return FoodCategorizationAIResponse(**data)
            except Exception as e:
                logger.warning(f"[AIService] Gemma output parsing error: {e}. Using deterministic fallback.")

        return cls._fallback_categorize(food_name, raw_description)

    @staticmethod
    def _fallback_categorize(food_name: str, raw_description: Optional[str] = None) -> FoodCategorizationAIResponse:
        name_lower = food_name.lower()
        category = "Cooked Meals"
        storage = "ambient"
        food_state = "cooked"

        if any(w in name_lower for w in ["bread", "cake", "pastry", "bun", "croissant", "poee"]):
            category = "Bakery & Bread"
            food_state = "bakery"
            storage = "ambient"
        elif any(w in name_lower for w in ["fruit", "apple", "banana", "vegetable", "greens", "spinach", "salad"]):
            category = "Fresh Produce"
            food_state = "raw"
            storage = "refrigerated" if "salad" in name_lower or "cut" in name_lower else "ambient"
        elif any(w in name_lower for w in ["juice", "shake", "drink", "beverage", "tea", "coffee"]):
            category = "Beverages"
            food_state = "beverage"
            storage = "ambient"
        elif any(w in name_lower for w in ["milk", "paneer", "cheese", "curd", "yogurt", "kheer"]):
            category = "Dairy & Refrigerated"
            food_state = "cooked"
            storage = "refrigerated"
        elif any(w in name_lower for w in ["canned", "biscuit", "packaged", "packet", "box", "noodle"]):
            category = "Packaged Foods"
            food_state = "packaged"
            storage = "ambient"

        desc = raw_description if raw_description else f"Fresh surplus of {food_name.strip()}."
        return FoodCategorizationAIResponse(
            normalized_name=food_name.strip(),
            suggested_category=category,
            suggested_storage=storage,
            food_state=food_state,
            concise_description=desc[:200],
            allergens=[],
            ai_powered=False,
        )

    # -------------------------------------------------------------------------
    # 4. INTENT-AWARE CHATBOT & TOOL ROUTING LAYER (Section D)
    # -------------------------------------------------------------------------
    @classmethod
    def parse_intent(
        cls,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        user_role: str = "general",
        user_context_summary: str = "",
    ) -> ChatbotParsedIntent:
        """
        Uses Gemma 4 to parse intent, extracted entities, quantities, unit,
        relevant IDs, and determine if an action or confirmation is required.
        """
        if history is None:
            history = []
        system_instruction = (
            "You are an intent-classification engine for a Food Rescue application. "
            "Analyze the user message and conversation history in the context of the user's role.\n"
            "Intents supported:\n"
            "- explain_donation_workflow: user asks how donations/pickups work\n"
            "- search_food: user searches for available food (e.g. 'find 5 kg rice', 'any bread available?')\n"
            "- list_my_requests: NGO asks to view their placed requests\n"
            "- list_my_donations: Donor asks to view their listed food batches\n"
            "- cancel_request: NGO wants to cancel a pending request (requires confirmation)\n"
            "- list_expiring_donations: user asks which food is expiring first / soonest\n"
            "- find_eligible_pickups: Volunteer asks for tasks to pick up (requires confirmation before claiming)\n"
            "- view_profile: user asks about their own account / status\n"
            "- general_query: general greetings, inquiries, or food safety questions\n\n"
            "Return valid JSON matching:\n"
            "{\n"
            "  'intent': str,\n"
            "  'question_type': 'informational' | 'action_request' | 'clarification' | 'greeting',\n"
            "  'action': 'search' | 'cancel' | 'list' | 'prioritize' | 'claim' | null,\n"
            "  'main_entity': str | null,\n"
            "  'extracted_entities': object,\n"
            "  'quantity': float | null,\n"
            "  'unit': str | null,\n"
            "  'relevant_ids': list of integers (resolve from history if user says 'that one', 'cancel it'),\n"
            "  'missing_information': list of strings,\n"
            "  'backend_action_needed': bool,\n"
            "  'confirmation_required': bool,\n"
            "  'confirmation_prompt': str | null\n"
            "}"
        )

        history_snippet = "\n".join([f"{h.get('role', 'user')}: {h.get('content', '')}" for h in history[-4:]])
        prompt = (
            f"User Role: {user_role}\n"
            f"Recent Context / Records: {user_context_summary}\n"
            f"Recent Conversation History:\n{history_snippet}\n\n"
            f"Current Message: '{message}'\n"
            f"Parse intent into JSON:"
        )

        raw_json = cls.call_gemma(prompt=prompt, system_instruction=system_instruction, json_mode=True)
        if raw_json:
            try:
                clean_json = raw_json.strip()
                if clean_json.startswith("```"):
                    clean_json = clean_json.split("\n", 1)[1]
                    if clean_json.endswith("```"):
                        clean_json = clean_json.rsplit("\n", 1)[0]
                data = json.loads(clean_json)
                return ChatbotParsedIntent(**data)
            except Exception as e:
                logger.warning(f"[AIService] Intent parsing failed: {e}. Using rule fallback.")

        # Deterministic fallback intent parsing
        msg_l = message.lower()
        if any(k in msg_l for k in ["find", "search", "available", "look for", "need"]):
            return ChatbotParsedIntent(
                intent="search_food",
                question_type="action_request",
                action="search",
                main_entity=msg_l.replace("find", "").replace("search", "").strip(),
                backend_action_needed=True,
            )
        elif "cancel" in msg_l:
            return ChatbotParsedIntent(
                intent="cancel_request",
                question_type="action_request",
                action="cancel",
                backend_action_needed=True,
                confirmation_required=True,
                confirmation_prompt="Please specify which request ID you would like to cancel.",
            )
        elif any(k in msg_l for k in ["expir", "best before", "urgent"]):
            return ChatbotParsedIntent(
                intent="list_expiring_donations",
                question_type="informational",
                backend_action_needed=True,
            )
        elif any(k in msg_l for k in ["my request", "requests"]):
            return ChatbotParsedIntent(
                intent="list_my_requests",
                question_type="informational",
                backend_action_needed=True,
            )
        elif any(k in msg_l for k in ["pickup", "task", "assign"]):
            return ChatbotParsedIntent(
                intent="find_eligible_pickups",
                question_type="informational",
                backend_action_needed=True,
            )
        return ChatbotParsedIntent(
            intent="general_query",
            question_type="informational",
            backend_action_needed=False,
        )

    @classmethod
    def execute_intent_tool(
        cls,
        db: Session,
        user: User,
        parsed_intent: ChatbotParsedIntent,
    ) -> Tuple[Optional[str], Optional[int], Any]:
        """
        Executes authenticated backend functions against actual MySQL database.
        Never executes arbitrary SQL. Enforces strict RBAC and validation.
        Returns: (tool_name, results_count, raw_results)
        """
        intent = parsed_intent.intent

        if intent == "search_food":
            # Public / NGO food search
            q = db.query(FoodBatch).filter(
                FoodBatch.food_status.in_(["available", "partially_reserved"])
            )
            entity = parsed_intent.main_entity
            if entity:
                q = q.filter(
                    or_(
                        FoodBatch.food_name.ilike(f"%{entity}%"),
                        FoodBatch.food_category.ilike(f"%{entity}%"),
                    )
                )
            results = q.order_by(FoodBatch.expiry_time.asc()).limit(5).all()
            from app.services.allocation_service import AllocationService
            output = []
            for b in results:
                _, _, rem = AllocationService.calculate_remaining_quantity(db, b.batch_id)
                output.append({
                    "batch_id": b.batch_id,
                    "food_name": b.food_name,
                    "category": b.food_category,
                    "remaining_quantity": float(rem),
                    "unit": b.unit,
                    "expiry_time": b.effective_expiry_time.isoformat() if b.effective_expiry_time else b.expiry_time.isoformat(),
                    "pickup_address": b.pickup_address,
                })
            return "search_food", len(output), output

        elif intent == "list_my_requests" and user.role == "ngo" and user.ngo:
            reqs = (
                db.query(PickupRequest)
                .filter(PickupRequest.ngo_id == user.ngo.ngo_id)
                .order_by(PickupRequest.requested_at.desc())
                .limit(5)
                .all()
            )
            output = [
                {
                    "request_id": r.request_id,
                    "food_name": r.food_batch.food_name if r.food_batch else "Donation",
                    "quantity": float(r.requested_quantity),
                    "unit": r.unit,
                    "status": r.request_status,
                    "requested_at": r.requested_at.isoformat(),
                }
                for r in reqs
            ]
            return "list_my_requests", len(output), output

        elif intent == "list_my_donations" and user.role == "donor" and user.donor:
            batches = (
                db.query(FoodBatch)
                .filter(FoodBatch.donor_id == user.donor.donor_id)
                .order_by(FoodBatch.created_at.desc())
                .limit(5)
                .all()
            )
            from app.services.allocation_service import AllocationService
            output = []
            for b in batches:
                _, alloc, rem = AllocationService.calculate_remaining_quantity(db, b.batch_id)
                output.append({
                    "batch_id": b.batch_id,
                    "food_name": b.food_name,
                    "total_quantity": float(b.quantity),
                    "remaining_quantity": float(rem),
                    "unit": b.unit,
                    "status": b.food_status,
                })
            return "list_my_donations", len(output), output

        elif intent == "list_expiring_donations":
            now = utc_now()
            batches = (
                db.query(FoodBatch)
                .filter(FoodBatch.food_status.in_(["available", "partially_reserved"]))
                .order_by(FoodBatch.expiry_time.asc())
                .limit(5)
                .all()
            )
            from app.services.allocation_service import AllocationService
            output = []
            for b in batches:
                exp = to_naive_utc(b.expiry_time)
                hrs_left = max(0.0, round((exp - now).total_seconds() / 3600.0, 1))
                _, _, rem = AllocationService.calculate_remaining_quantity(db, b.batch_id)
                output.append({
                    "batch_id": b.batch_id,
                    "food_name": b.food_name,
                    "remaining_quantity": float(rem),
                    "unit": b.unit,
                    "hours_left": hrs_left,
                    "pickup_address": b.pickup_address,
                })
            return "list_expiring_donations", len(output), output

        elif intent == "find_eligible_pickups" and user.role == "volunteer":
            tasks = (
                db.query(PickupRequest)
                .filter(
                    PickupRequest.request_status == "requested",
                    PickupRequest.volunteer_id.is_(None),
                )
                .order_by(PickupRequest.requested_at.asc())
                .limit(5)
                .all()
            )
            output = [
                {
                    "request_id": t.request_id,
                    "food_name": t.food_batch.food_name if t.food_batch else "Donation",
                    "quantity": float(t.requested_quantity),
                    "unit": t.unit,
                    "donor_address": t.food_batch.pickup_address if t.food_batch else "Donor",
                    "ngo_name": t.ngo.ngo_name if t.ngo else "Shelter",
                    "ngo_address": t.ngo.address if t.ngo else "Shelter address",
                }
                for t in tasks
            ]
            return "find_eligible_pickups", len(output), output

        return None, None, None

    @classmethod
    def intent_aware_chat(
        cls,
        db: Session,
        user: User,
        message: str,
        history: List[Dict[str, str]] = [],
        confirmed_action: Optional[bool] = None,
        pending_action_data: Optional[Dict[str, Any]] = None,
    ) -> IntentChatResponse:
        """
        Orchestrates intent parsing, backend tool execution, confirmation checks,
        and natural synthesis via Gemma 4.
        """
        # User Context Summary
        now = utc_now()
        role = user.role
        context_parts = [f"User: {user.name} ({role.upper()})"]

        if role == "donor" and user.donor:
            context_parts.append(f"Org: {user.donor.donor_name}, Address: {user.donor.address}")
        elif role == "ngo" and user.ngo:
            context_parts.append(f"Org: {user.ngo.ngo_name}, Address: {user.ngo.address}")
        elif role == "volunteer" and user.volunteer:
            context_parts.append(f"Status: {user.volunteer.availability_status}")

        user_context_summary = " | ".join(context_parts)

        # Step 1: Parse Intent
        parsed_intent = cls.parse_intent(
            message=message,
            history=history,
            user_role=role,
            user_context_summary=user_context_summary,
        )

        # Step 2: Tool execution
        tool_name, tool_count, tool_results = cls.execute_intent_tool(db, user, parsed_intent)

        # Step 3: Response Synthesis with Gemma 4
        system_instruction = (
            "You are the Community Food Rescue Network AI Assistant powered by Hosted Gemma 4. "
            "You provide accurate, courteous, and actionable answers using real system data.\n"
            "Guidelines:\n"
            "1. ONLY reference real data provided in the Tool Results and User Context. Never invent IDs or records.\n"
            "2. If the user wants to cancel or claim an item, clearly explain confirmation is needed before committing.\n"
            "3. If tool results are empty, advise the user clearly without fabricating alternatives.\n"
            "4. Keep responses concise, warm, structured with bullet points where helpful."
        )

        tool_data_snippet = json.dumps(tool_results, default=str) if tool_results else "No backend records queried."
        prompt = (
            f"### CONTEXT:\n{user_context_summary}\n"
            f"### INTENT PARSED: {parsed_intent.intent} (Action: {parsed_intent.action})\n"
            f"### REAL DATABASE TOOL RESULTS:\n{tool_data_snippet}\n\n"
            f"### USER QUERY: {message}\n"
            f"Respond to user:"
        )

        ai_reply = cls.call_gemma(prompt=prompt, system_instruction=system_instruction)
        if not ai_reply:
            # Deterministic fallback response synthesis
            if parsed_intent.confirmation_required:
                ai_reply = f"Please confirm if you would like to proceed with {parsed_intent.action or 'cancelling this request'}. This action cannot be undone."
            elif tool_name == "search_food":
                if tool_count and tool_count > 0:
                    items_str = "\n".join([f"- **{i['food_name']}**: {i['remaining_quantity']} {i['unit']} at {i['pickup_address']}" for i in tool_results[:3]])
                    ai_reply = f"Here are available food items matching your request:\n{items_str}\n\nYou can request any portion directly from the Explore Food page."
                else:
                    ai_reply = "I couldn't find any surplus donations matching your criteria at this moment. Please check back shortly as new batches are listed regularly."
            elif tool_name == "list_expiring_donations":
                if tool_count and tool_count > 0:
                    items_str = "\n".join([f"- **{i['food_name']}**: ~{i['hours_left']}h left ({i['remaining_quantity']} {i['unit']} at {i['pickup_address']})" for i in tool_results[:3]])
                    ai_reply = f"These donations require priority rescue before expiry:\n{items_str}"
                else:
                    ai_reply = "All active donations currently have comfortable remaining shelf life."
            elif tool_name == "list_my_requests":
                ai_reply = f"You have {tool_count or 0} active request(s) on your dashboard. View 'My Requests' for complete tracking."
            elif tool_name == "find_eligible_pickups":
                ai_reply = f"Found {tool_count or 0} pending pickup assignment(s) ready for courier claim on the Available Tasks tab."
            else:
                ai_reply = f"Hello {user.name}! I am Gemma 4. I can assist you with searching surplus meals, tracking your requests, verifying FSSAI holding hours, or prioritizing pickups."

        return IntentChatResponse(
            reply=ai_reply.strip(),
            parsed_intent=parsed_intent,
            tool_executed=tool_name,
            tool_results_count=tool_count,
            role=role,
            user_name=user.name,
            ai_powered=bool(settings.ai_api_key),
        )

    # -------------------------------------------------------------------------
    # 5. LEGACY HELPER COMPATIBILITY
    # -------------------------------------------------------------------------
    @classmethod
    def chat_with_assistant(cls, db: Session, user: User, user_message: str) -> str:
        res = cls.intent_aware_chat(db=db, user=user, message=user_message)
        return res.reply

    # -------------------------------------------------------------------------
    # 6. SMART NGO-FOOD MATCHING (Deterministic filtering + Gemma explanation)
    # -------------------------------------------------------------------------
    @classmethod
    def match_food_for_ngo(
        cls,
        db: Session,
        ngo_user: User,
        preferred_category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        ngo = ngo_user.ngo
        now = utc_now()

        query = db.query(FoodBatch).filter(
            FoodBatch.food_status.in_(["available", "partially_reserved"])
        )
        if preferred_category and preferred_category != "All":
            query = query.filter(FoodBatch.food_category == preferred_category)

        available_batches = query.all()
        from app.services.allocation_service import AllocationService

        candidates = []
        for b in available_batches:
            exp = to_naive_utc(b.expiry_time)
            if exp <= now:
                continue

            total, allocated, remaining = AllocationService.calculate_remaining_quantity(db, b.batch_id)
            if remaining <= 0:
                continue

            hrs_left = max(0.1, (exp - now).total_seconds() / 3600.0)
            urgency = "critical" if hrs_left <= 2.0 else "high" if hrs_left <= 6.0 else "medium"
            score = 90 if urgency == "critical" else 75 if urgency == "high" else 60

            candidates.append({
                "batch_id": b.batch_id,
                "food_name": b.food_name,
                "category": b.food_category,
                "remaining_quantity": float(remaining),
                "unit": b.unit,
                "storage_condition": b.storage_condition or "ambient",
                "pickup_address": b.pickup_address,
                "hours_left": round(hrs_left, 1),
                "urgency": urgency,
                "score": score,
                "reason": f"Redistribute before {round(hrs_left, 1)}h expiry cutoff to avoid surplus waste.",
            })

        candidates.sort(key=lambda x: (x["score"], -x["hours_left"]), reverse=True)
        return candidates[:6]

    # -------------------------------------------------------------------------
    # 7. VOLUNTEER PICKUP TASK PRIORITIZATION
    # -------------------------------------------------------------------------
    @classmethod
    def prioritize_volunteer_tasks(
        cls,
        db: Session,
        volunteer: User,
    ) -> List[Dict[str, Any]]:
        now = utc_now()
        pending_requests = (
            db.query(PickupRequest)
            .filter(
                PickupRequest.request_status == "requested",
                PickupRequest.volunteer_id == None,
            )
            .all()
        )

        items = []
        for pr in pending_requests:
            if not pr.food_batch:
                continue
            b = pr.food_batch
            exp = to_naive_utc(b.expiry_time)
            if exp <= now:
                continue

            rem_mins = max(0, int((exp - now).total_seconds() / 60))
            rem_hours = round(rem_mins / 60.0, 1)

            if rem_mins <= 120:
                priority_badge = "URGENT (<2h)"
                base_score = 100 - (rem_mins // 2)
            elif rem_mins <= 360:
                priority_badge = "TODAY (<6h)"
                base_score = 60 - (rem_mins // 10)
            else:
                priority_badge = "STANDARD"
                base_score = 30

            items.append({
                "request_id": pr.request_id,
                "batch_id": b.batch_id,
                "food_name": b.food_name,
                "category": b.food_category,
                "quantity": float(pr.requested_quantity),
                "unit": pr.unit,
                "pickup_address": b.pickup_address,
                "ngo_name": pr.ngo.ngo_name if pr.ngo else "Shelter",
                "ngo_address": pr.ngo.address if pr.ngo else "Shelter address",
                "remaining_minutes": rem_mins,
                "remaining_hours": rem_hours,
                "urgency_badge": priority_badge,
                "score": base_score,
                "priority_reason": f"Expires in ~{rem_hours}h. Prioritized to redistribute {pr.requested_quantity} {pr.unit} safely.",
            })

        items.sort(key=lambda x: x["score"], reverse=True)
        for idx, item in enumerate(items, 1):
            item["priority_rank"] = idx

        return items


ai_service = AIService

