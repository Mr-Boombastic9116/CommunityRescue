from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.food_safety_rule import FoodSafetyRule
from app.utils.dates import to_naive_utc, utc_now

CATEGORY_ALIASES = {
    "raw food/produce": ["raw food/produce", "fresh produce", "raw food", "produce", "fruits & vegetables"],
    "fresh produce": ["fresh produce", "raw food/produce", "raw food", "produce", "fruits & vegetables"],
    "packaged & canned": ["packaged & canned", "packaged foods", "packaged food", "canned"],
    "packaged foods": ["packaged foods", "packaged & canned", "packaged food", "canned"],
    "dairy & refrigerated": ["dairy & refrigerated", "dairy"],
    "cooked meals": ["cooked meals", "cooked food"],
    "bakery & bread": ["bakery & bread", "bakery", "bread"],
    "beverages": ["beverages", "beverage", "drinks"],
}

class ExpiryValidationResult:
    def __init__(
        self,
        effective_expiry: datetime,
        user_expiry: datetime,
        max_allowed_expiry: Optional[datetime],
        validation_status: str,  # 'verified', 'exceeded_max', 'manual_verification_required'
        rule_applied: Optional[str],
        max_permitted_hours: Optional[float],
        is_exceeded: bool = False,
        error_message: Optional[str] = None,
        source_name: Optional[str] = None,
        source_url: Optional[str] = None,
        requires_manual_verification: bool = False,
    ):
        self.effective_expiry = effective_expiry
        self.user_expiry = user_expiry
        self.max_allowed_expiry = max_allowed_expiry
        self.validation_status = validation_status
        self.rule_applied = rule_applied
        self.max_permitted_hours = max_permitted_hours
        self.is_exceeded = is_exceeded
        self.error_message = error_message
        self.source_name = source_name
        self.source_url = source_url
        self.requires_manual_verification = requires_manual_verification

    @property
    def adjustment_reason(self) -> Optional[str]:
        return self.error_message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "effective_expiry": self.effective_expiry.isoformat() if self.effective_expiry else None,
            "user_expiry": self.user_expiry.isoformat() if self.user_expiry else None,
            "max_allowed_expiry": self.max_allowed_expiry.isoformat() if self.max_allowed_expiry else None,
            "validation_status": self.validation_status,
            "rule_applied": self.rule_applied,
            "max_permitted_hours": self.max_permitted_hours,
            "is_exceeded": self.is_exceeded,
            "error_message": self.error_message,
            "adjustment_reason": self.error_message,
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
        Matches category synonyms and storage condition.
        Never assumes an arbitrary default duration if no rule exists.
        """
        cat_norm = (food_category or "").strip().lower()
        storage_norm = (storage_condition or "").strip().lower()

        # Query rules for the specific storage condition
        rules_for_storage = (
            db.query(FoodSafetyRule)
            .filter(FoodSafetyRule.storage_condition == storage_norm)
            .all()
        )

        if not rules_for_storage:
            # If no rule exists for this storage condition, do not assume default
            return None

        # Refined subcategory matching within applicable food categories
        if food_name:
            fn_lower = food_name.lower()
            if cat_norm in ["cooked meals", "prepared foods"]:
                if any(k in fn_lower for k in ["meat", "chicken", "fish", "prawn", "seafood", "mutton", "egg"]):
                    for r in rules_for_storage:
                        if any(k in r.product_type.lower() for k in ["meat", "poultry", "fish", "seafood"]):
                            return r
                if any(k in fn_lower for k in ["paneer", "milk", "cheese", "kheer", "dairy", "yogurt", "curd"]):
                    for r in rules_for_storage:
                        if any(k in r.product_type.lower() for k in ["paneer", "dairy", "milk"]):
                            return r
            elif cat_norm in ["bakery & bread", "bakery"]:
                if any(k in fn_lower for k in ["cake", "pastry", "cream", "custard"]):
                    for r in rules_for_storage:
                        if any(k in r.product_type.lower() for k in ["cream", "pastry", "cake"]):
                            return r
            elif cat_norm in ["raw food/produce", "fresh produce"]:
                if any(k in fn_lower for k in ["cut fruit", "sliced", "salad", "diced", "pre-cut"]):
                    for r in rules_for_storage:
                        if any(k in r.product_type.lower() for k in ["cut fruit", "salad", "pre-cut"]):
                            return r

        # 1. Exact match on food_category
        for r in rules_for_storage:
            if r.food_category.strip().lower() == cat_norm:
                return r

        # 2. Category matching with synonym resolution
        aliases = CATEGORY_ALIASES.get(cat_norm, [cat_norm])
        for r in rules_for_storage:
            if r.food_category.strip().lower() in aliases:
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
        Validates the food donation's expiry against curated FSSAI rules:
        maximum_expiry = preparation_time + maximum_allowed_hours
        effective_expiry = min(user_selected_expiry, maximum_expiry, manufacturer_use_by_date_if_applicable)
        If user_expiry > maximum_expiry, returns is_exceeded=True and detailed error message.
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
            # No matching verified safety rule found
            return ExpiryValidationResult(
                effective_expiry=user_exp_utc,
                user_expiry=user_exp_utc,
                max_allowed_expiry=None,
                validation_status="manual_verification_required",
                rule_applied=None,
                max_permitted_hours=None,
                is_exceeded=False,
                error_message=(
                    f"No certified food safety rule found for category '{food_category}' under '{storage_condition}' storage. "
                    "Manual administrator verification required before redistribution."
                ),
                source_name=None,
                source_url=None,
                requires_manual_verification=True,
            )

        max_hours = float(rule.max_holding_hours)
        max_allowed_expiry = prep_utc + timedelta(hours=max_hours)

        # Account for printed label expiry if earlier
        is_capped_by_packaging = False
        if packaging_expiry:
            pkg_utc = to_naive_utc(packaging_expiry)
            if pkg_utc < max_allowed_expiry:
                max_allowed_expiry = pkg_utc
                is_capped_by_packaging = True

        if user_exp_utc > max_allowed_expiry:
            if is_capped_by_packaging:
                error_msg = (
                    f"Selected expiry ({user_exp_utc.strftime('%Y-%m-%d %H:%M UTC')}) exceeds the manufacturer printed use-by date "
                    f"({max_allowed_expiry.strftime('%Y-%m-%d %H:%M UTC')}). You can select an earlier expiry time, but not a later one."
                )
            else:
                error_msg = (
                    f"Selected expiry ({user_exp_utc.strftime('%Y-%m-%d %H:%M UTC')}) exceeds the maximum permitted holding duration of "
                    f"{max_hours} hours from preparation ({max_allowed_expiry.strftime('%Y-%m-%d %H:%M UTC')}) under {rule.source_name} "
                    f"for '{rule.product_type}' ({storage_condition} storage). You can select an earlier expiry time, but you cannot select a time later than {max_allowed_expiry.strftime('%Y-%m-%d %H:%M UTC')}."
                )
            return ExpiryValidationResult(
                effective_expiry=max_allowed_expiry,
                user_expiry=user_exp_utc,
                max_allowed_expiry=max_allowed_expiry,
                validation_status="exceeded_max",
                rule_applied=f"{rule.source_name} ({rule.product_type})",
                max_permitted_hours=max_hours,
                is_exceeded=True,
                error_message=error_msg,
                source_name=rule.source_name,
                source_url=rule.source_url,
                requires_manual_verification=False,
            )
        else:
            return ExpiryValidationResult(
                effective_expiry=user_exp_utc,
                user_expiry=user_exp_utc,
                max_allowed_expiry=max_allowed_expiry,
                validation_status="verified",
                rule_applied=f"{rule.source_name} ({rule.product_type})",
                max_permitted_hours=max_hours,
                is_exceeded=False,
                error_message=None,
                source_name=rule.source_name,
                source_url=rule.source_url,
                requires_manual_verification=False,
            )
