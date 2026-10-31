import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.services.expiry_validation_service import ExpiryValidationService
from app.utils.dates import utc_now

def test_expiry_earlier_than_maximum(db_session):
    now = utc_now()
    prep_time = now
    # 2 hours from prep (FSSAI rule for Cooked Meals Ambient is 4 hours)
    user_expiry = prep_time + timedelta(hours=2)

    result = ExpiryValidationService.validate_food_expiry(
        db=db_session,
        food_name="Cooked Rice",
        food_category="Cooked Meals",
        prepared_at=prep_time,
        user_expiry=user_expiry,
        storage_condition="ambient",
    )

    assert result.validation_status == "verified"
    assert result.effective_expiry == user_expiry
    assert result.rule_applied is not None
    assert result.adjustment_reason is None

def test_expiry_exceeding_maximum_capped(db_session):
    now = utc_now()
    prep_time = now
    # 10 hours from prep (Cooked Meals Ambient max is 4 hours)
    user_expiry = prep_time + timedelta(hours=10)

    result = ExpiryValidationService.validate_food_expiry(
        db=db_session,
        food_name="Vegetable Pulao",
        food_category="Cooked Meals",
        prepared_at=prep_time,
        user_expiry=user_expiry,
        storage_condition="ambient",
    )

    assert result.validation_status == "exceeded_max"
    assert result.is_exceeded is True
    expected_max = prep_time + timedelta(hours=4)
    assert result.effective_expiry == expected_max
    assert "FSSAI" in result.rule_applied
    assert "exceeds the maximum permitted holding duration" in result.adjustment_reason

def test_hot_holding_storage_condition(db_session):
    now = utc_now()
    prep_time = now
    # 5 hours with hot holding (max is 6 hours)
    user_expiry = prep_time + timedelta(hours=5)

    result = ExpiryValidationService.validate_food_expiry(
        db=db_session,
        food_name="Hot Sambhar",
        food_category="Cooked Meals",
        prepared_at=prep_time,
        user_expiry=user_expiry,
        storage_condition="hot_holding",
    )

    assert result.validation_status == "verified"
    assert result.effective_expiry == user_expiry
    assert "FSSAI" in result.rule_applied

def test_refrigerated_storage_condition(db_session):
    now = utc_now()
    prep_time = now
    # 30 hours with refrigeration (max is 48 hours)
    user_expiry = prep_time + timedelta(hours=30)

    result = ExpiryValidationService.validate_food_expiry(
        db=db_session,
        food_name="Chilled Stew",
        food_category="Cooked Meals",
        prepared_at=prep_time,
        user_expiry=user_expiry,
        storage_condition="refrigerated",
    )

    assert result.validation_status == "verified"
    assert result.effective_expiry == user_expiry
    assert "FSSAI" in result.rule_applied

def test_packaging_expiry_earlier_caps_effective(db_session):
    now = utc_now()
    prep_time = now
    # User expiry is 3 hours away
    user_expiry = prep_time + timedelta(hours=3)
    # But packaging printed expiry is 1 hour away
    packaging_expiry = prep_time + timedelta(hours=1)

    result = ExpiryValidationService.validate_food_expiry(
        db=db_session,
        food_name="Canned Beans",
        food_category="Cooked Meals",
        prepared_at=prep_time,
        user_expiry=user_expiry,
        storage_condition="ambient",
        packaging_expiry=packaging_expiry,
    )

    assert result.validation_status == "exceeded_max"
    assert result.is_exceeded is True
    assert result.effective_expiry == packaging_expiry
    assert "exceeds the manufacturer printed use-by date" in result.adjustment_reason
