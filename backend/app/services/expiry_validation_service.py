from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.food_safety_rule import FoodSafetyRule
from app.utils.dates import to_naive_utc, utc_now

class ExpiryValidationResult:
    def __init__(
        self,
        effective_expiry: datetime,
        user_expiry: datetime,
        validation_status: str,  # 'verified', 'adjusted', 'manual_verification_required'
        rule_applied: Optional[str],
        max_permitted_hours: Optional[float],
        adjustment_reason: Optional[str] = None,
        source_name: Optional[str] = None,
        source_url: Optional[str] = None,
        requires_manual_verification: bool = False,
    ):
        self.effective_expiry = effective_expiry
        self.user_expiry = user_expiry
        self.validation_status = validation_status
        self.rule_applied = rule_applied
        self.max_permitted_hours = max_permitted_hours
        self.adjustment_reason = adjustment_reason
        self.source_name = source_name
        self.source_url = source_url
        self.requires_manual_verification = requires_manual_verification

    def to_dict(self) -> Dict[str, Any]:
        return {
            "effective_expiry": self.effective_expiry.isoformat(),
            "user_expiry": self.user_expiry.isoformat(),
            "validation_status": self.validation_status,
            "rule_applied": self.rule_applied,
            "max_permitted_hours": self.max_permitted_hours,
            "adjustment_reason": self.adjustment_reason,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "requires_manual_verification": self.requires_manual_verification,
        }

class ExpiryValidationService:
    @staticmethod
    def find_matching_rule(
        db: Session,
        food_category: str,
        storage_condition: str,
        food_name: Optional[str] = None,
    ) -> Optional[FoodSafetyRule]:
        """
        Looks up the best matching curated safety rule from the database.
        Prefers specific keyword matching on product_type if food_name is provided,
        otherwise falls back to category + storage condition.
        """
        # Normalize input
        cat_norm = food_category.strip()
        storage_norm = storage_condition.strip().lower()

        # Try to find specific keyword matches in food_name
        query = db.query(FoodSafetyRule).filter(
            FoodSafetyRule.storage_condition == storage_norm
        )

        rules_for_storage = query.all()
        if not rules_for_storage:
            # Fallback to ambient if unknown condition
            rules_for_storage = db.query(FoodSafetyRule).filter(
                FoodSafetyRule.storage_condition == "ambient"
            ).all()

        # If food_name provided, test keywords (e.g. fish, meat, dairy, paneer, cake, pastry)
        if food_name:
            fn_lower = food_name.lower()
            if any(k in fn_lower for k in ["meat", "chicken", "fish", "prawn", "seafood", "mutton", "egg"]):
                for r in rules_for_storage:
                    if any(k in r.product_type.lower() for k in ["meat", "poultry", "fish", "seafood"]):
                        return r
            if any(k in fn_lower for k in ["paneer", "milk", "cheese", "kheer", "dairy"]):
                for r in rules_for_storage:
                    if any(k in r.product_type.lower() for k in ["paneer", "dairy", "milk"]):
                        return r
            if any(k in fn_lower for k in ["cake", "pastry", "cream", "custard"]):
                for r in rules_for_storage:
                    if any(k in r.product_type.lower() for k in ["cream", "pastry", "cake"]):
                        return r
            if any(k in fn_lower for k in ["bread", "poee", "roll", "bun", "baguette"]):
                for r in rules_for_storage:
                    if any(k in r.product_type.lower() for k in ["bread", "poee", "roll", "bun"]):
                        return r
            if any(k in fn_lower for k in ["cut fruit", "sliced", "salad"]):
                for r in rules_for_storage:
                    if any(k in r.product_type.lower() for k in ["cut fruit", "salad", "pre-cut"]):
                        return r

        # Fallback to category matching
        for r in rules_for_storage:
            if r.food_category.lower() == cat_norm.lower():
                return r

        return None

    @classmethod
    def validate_food_expiry(
        cls,
        db: Session,
        food_name: str,
        food_category: str,
        prepared_at: datetime,
        user_expiry: datetime,
        storage_condition: str = "ambient",
        packaging_expiry: Optional[datetime] = None,
    ) -> ExpiryValidationResult:
        """
        Validates the food donation's expiry against curated FSSAI/scientific rules.
        Enforces:
        If user_expiry > maximum_allowed_expiry:
            effective_expiry = maximum_allowed_expiry
        Otherwise:
            effective_expiry = user_expiry
        """
        prep_utc = to_naive_utc(prepared_at)
        user_exp_utc = to_naive_utc(user_expiry)

        rule = cls.find_matching_rule(
            db=db,
            food_category=food_category,
            storage_condition=storage_condition,
            food_name=food_name,
        )

        if not rule:
            # No matching curated safety rule found
            return ExpiryValidationResult(
                effective_expiry=user_exp_utc,
                user_expiry=user_exp_utc,
                validation_status="manual_verification_required",
                rule_applied="None (Unrecognized category/storage combination)",
                max_permitted_hours=None,
                adjustment_reason=(
                    f"No certified safety rule found for '{food_category}' under '{storage_condition}' storage. "
                    "Manual verification required before surplus redistribution."
                ),
                requires_manual_verification=True,
            )

        max_hours = float(rule.max_holding_hours)
        max_allowed_expiry = prep_utc + timedelta(hours=max_hours)

        # Also account for printed label expiry if earlier
        is_capped_by_packaging = False
        if packaging_expiry:
            pkg_utc = to_naive_utc(packaging_expiry)
            if pkg_utc < max_allowed_expiry:
                max_allowed_expiry = pkg_utc
                is_capped_by_packaging = True

        if user_exp_utc > max_allowed_expiry:
            # Rule adjustment applied
            if is_capped_by_packaging and max_allowed_expiry == to_naive_utc(packaging_expiry):
                reason = (
                    f"Selected expiry exceeded printed packaging expiry ({to_naive_utc(packaging_expiry).isoformat()}). "
                    f"Effective expiry safely capped by manufacturer packaging printed expiry date."
                )
            else:
                reason = (
                    f"Selected expiry exceeded the certified safety limit of {max_hours} hours for "
                    f"'{rule.product_type}' under '{storage_condition}' storage. "
                    f"Effective expiry safely capped by {rule.source_name}."
                )
            return ExpiryValidationResult(
                effective_expiry=max_allowed_expiry,
                user_expiry=user_exp_utc,
                validation_status="adjusted",
                rule_applied=f"{rule.source_name} ({rule.product_type})",
                max_permitted_hours=max_hours,
                adjustment_reason=reason,
                source_name=rule.source_name,
                source_url=rule.source_url,
                requires_manual_verification=False,
            )
        else:
            # User expiry is within safe limits
            return ExpiryValidationResult(
                effective_expiry=user_exp_utc,
                user_expiry=user_exp_utc,
                validation_status="verified",
                rule_applied=f"{rule.source_name} ({rule.product_type})",
                max_permitted_hours=max_hours,
                adjustment_reason=None,
                source_name=rule.source_name,
                source_url=rule.source_url,
                requires_manual_verification=False,
            )
