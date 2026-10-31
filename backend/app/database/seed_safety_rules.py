"""
Curated Food Safety Rules Seeder.
Standards based on FSSAI (Food Safety and Standards Authority of India)
Guidance for Surplus Food Distribution & Hygienic Handling.
"""
import os
import sys
from datetime import datetime

# Ensure backend directory is in path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.food_safety_rule import FoodSafetyRule

CURATED_RULES = [
    # 1. Cooked Meals - Ambient
    {
        "food_category": "Cooked Meals",
        "product_type": "Cooked Grain, Rice, Dal & Vegetable Curries",
        "storage_condition": "ambient",
        "temperature_min_c": 18.0,
        "temperature_max_c": 32.0,
        "max_holding_hours": 4.0,
        "source_name": "FSSAI Guidance Document for Surplus Food Distribution (2020), Sec. 4.2",
        "source_url": "https://www.fssai.gov.in/upload/uploadfiles/files/Guidance_Document_Surplus_Food.pdf",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 2. Cooked Meals - Hot Holding
    {
        "food_category": "Cooked Meals",
        "product_type": "Cooked Hot Meals & Warm Stews",
        "storage_condition": "hot_holding",
        "temperature_min_c": 60.0,
        "temperature_max_c": 80.0,
        "max_holding_hours": 6.0,
        "source_name": "FSSAI Food Safety and Standards (Recovery of Surplus Food) Regulations, Regulation 4",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 3. Cooked Meals - Refrigerated
    {
        "food_category": "Cooked Meals",
        "product_type": "Cooked Meals (Rapid Chilled)",
        "storage_condition": "refrigerated",
        "temperature_min_c": 1.0,
        "temperature_max_c": 4.0,
        "max_holding_hours": 48.0,
        "source_name": "FSSAI Surplus Food Cold Chain Guidelines",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 4. Cooked Meat & Seafood - Ambient
    {
        "food_category": "Cooked Meals",
        "product_type": "Cooked Poultry, Fish, Seafood & Meat Dishes",
        "storage_condition": "ambient",
        "temperature_min_c": 18.0,
        "temperature_max_c": 32.0,
        "max_holding_hours": 2.5,
        "source_name": "FSSAI Schedule 4 Meat & High-Protein Prepared Food Protocols",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 5. Cooked Meat & Seafood - Refrigerated
    {
        "food_category": "Cooked Meals",
        "product_type": "Cooked Poultry, Fish & Meat (Chilled)",
        "storage_condition": "refrigerated",
        "temperature_min_c": 0.0,
        "temperature_max_c": 4.0,
        "max_holding_hours": 24.0,
        "source_name": "FSSAI / Codex Alimentarius Prepared Meat Cold Retention",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 6. Dairy & Paneer - Ambient
    {
        "food_category": "Cooked Meals",
        "product_type": "Paneer, Milk Sweets & Dairy Gravies",
        "storage_condition": "ambient",
        "temperature_min_c": 18.0,
        "temperature_max_c": 30.0,
        "max_holding_hours": 2.0,
        "source_name": "FSSAI Dairy Products Handling Standard for Donation",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 7. Dairy & Paneer - Refrigerated
    {
        "food_category": "Cooked Meals",
        "product_type": "Paneer & Dairy Dishes (Chilled)",
        "storage_condition": "refrigerated",
        "temperature_min_c": 1.0,
        "temperature_max_c": 4.0,
        "max_holding_hours": 24.0,
        "source_name": "FSSAI Dairy Products Handling Standard",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 8. Bakery & Bread - Ambient
    {
        "food_category": "Bakery & Bread",
        "product_type": "Dry Breads, Poee, Rolls, Baguettes & Buns",
        "storage_condition": "ambient",
        "temperature_min_c": 15.0,
        "temperature_max_c": 30.0,
        "max_holding_hours": 48.0,
        "source_name": "FSSAI Bakery Guidelines for Commercial Bread Redistribution",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 9. Bakery with Cream / Custard - Ambient
    {
        "food_category": "Bakery & Bread",
        "product_type": "Cakes, Pastries & Cream-Filled Bakery",
        "storage_condition": "ambient",
        "temperature_min_c": 18.0,
        "temperature_max_c": 30.0,
        "max_holding_hours": 3.0,
        "source_name": "FSSAI Guidelines for Perishable Bakery Confectionery",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 10. Bakery with Cream / Custard - Refrigerated
    {
        "food_category": "Bakery & Bread",
        "product_type": "Cakes, Pastries & Cream-Filled Bakery (Chilled)",
        "storage_condition": "refrigerated",
        "temperature_min_c": 1.0,
        "temperature_max_c": 4.0,
        "max_holding_hours": 24.0,
        "source_name": "FSSAI Guidelines for Perishable Bakery Confectionery",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 11. Fresh Cut Produce & Salads - Ambient
    {
        "food_category": "Fresh Produce",
        "product_type": "Cut Fruits, Diced Salads & Pre-Cut Vegetables",
        "storage_condition": "ambient",
        "temperature_min_c": 18.0,
        "temperature_max_c": 30.0,
        "max_holding_hours": 2.0,
        "source_name": "FSSAI Fresh Produce Safe Cut Protocols",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 12. Fresh Cut Produce & Salads - Refrigerated
    {
        "food_category": "Fresh Produce",
        "product_type": "Cut Fruits, Diced Salads & Pre-Cut Vegetables (Chilled)",
        "storage_condition": "refrigerated",
        "temperature_min_c": 1.0,
        "temperature_max_c": 4.0,
        "max_holding_hours": 14.0,
        "source_name": "FSSAI Fresh Produce Safe Cut Protocols",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 13. Whole Fresh Produce - Ambient
    {
        "food_category": "Fresh Produce",
        "product_type": "Whole Uncut Raw Fruits and Vegetables",
        "storage_condition": "ambient",
        "temperature_min_c": 15.0,
        "temperature_max_c": 30.0,
        "max_holding_hours": 72.0,
        "source_name": "FSSAI Post-Harvest Surplus Handling Guidelines",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 14. Beverages & Fresh Juices - Ambient
    {
        "food_category": "Beverages",
        "product_type": "Fresh Pressed Unpasteurized Juices & Shakes",
        "storage_condition": "ambient",
        "temperature_min_c": 18.0,
        "temperature_max_c": 30.0,
        "max_holding_hours": 2.0,
        "source_name": "FSSAI Raw Beverage Safety Regulations",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 15. Beverages & Fresh Juices - Refrigerated
    {
        "food_category": "Beverages",
        "product_type": "Fresh Juices & Milk Beverages (Chilled)",
        "storage_condition": "refrigerated",
        "temperature_min_c": 1.0,
        "temperature_max_c": 4.0,
        "max_holding_hours": 12.0,
        "source_name": "FSSAI Raw Beverage Safety Regulations",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 16. Packaged Foods - Ambient
    {
        "food_category": "Packaged Foods",
        "product_type": "Sealed Shelf-Stable Packaged Food & Canned Goods",
        "storage_condition": "ambient",
        "temperature_min_c": 10.0,
        "temperature_max_c": 35.0,
        "max_holding_hours": 720.0,  # 30 days default or manufacturer best-before
        "source_name": "FSSAI (Packaging and Labelling) Regulations, 2011",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 17. Frozen Food - Frozen (-18C)
    {
        "food_category": "Cooked Meals",
        "product_type": "Deep Frozen Cooked Meals & Batches",
        "storage_condition": "frozen",
        "temperature_min_c": -24.0,
        "temperature_max_c": -18.0,
        "max_holding_hours": 720.0,  # 30 days
        "source_name": "FSSAI Cold Chain Standards for Frozen Foods",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 18. Dairy & Refrigerated - Ambient
    {
        "food_category": "Dairy & Refrigerated",
        "product_type": "Milk, Paneer, Curd, Dairy Desserts & Sweets",
        "storage_condition": "ambient",
        "temperature_min_c": 18.0,
        "temperature_max_c": 30.0,
        "max_holding_hours": 2.0,
        "source_name": "FSSAI Dairy Products Handling Standard for Donation",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 19. Dairy & Refrigerated - Refrigerated
    {
        "food_category": "Dairy & Refrigerated",
        "product_type": "Chilled Dairy Products, Pasteurized Milk, Paneer & Yogurt",
        "storage_condition": "refrigerated",
        "temperature_min_c": 1.0,
        "temperature_max_c": 4.0,
        "max_holding_hours": 24.0,
        "source_name": "FSSAI Dairy Products Handling Standard (Cold Retention)",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 20. Raw Food/Produce - Ambient
    {
        "food_category": "Raw Food/Produce",
        "product_type": "Whole Raw Fruits, Roots and Vegetables",
        "storage_condition": "ambient",
        "temperature_min_c": 15.0,
        "temperature_max_c": 30.0,
        "max_holding_hours": 72.0,
        "source_name": "FSSAI Post-Harvest Surplus Handling Guidelines",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 21. Raw Food/Produce - Refrigerated
    {
        "food_category": "Raw Food/Produce",
        "product_type": "Chilled Fresh Produce, Cut Fruits & Washed Greens",
        "storage_condition": "refrigerated",
        "temperature_min_c": 1.0,
        "temperature_max_c": 4.0,
        "max_holding_hours": 14.0,
        "source_name": "FSSAI Fresh Produce Safe Cut & Cold Chain Protocols",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 22. Packaged & Canned - Ambient
    {
        "food_category": "Packaged & Canned",
        "product_type": "Sealed Shelf-Stable Packaged Food & Canned Goods",
        "storage_condition": "ambient",
        "temperature_min_c": 10.0,
        "temperature_max_c": 35.0,
        "max_holding_hours": 720.0,
        "source_name": "FSSAI (Packaging and Labelling) Regulations, 2011",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
    # 23. Packaged & Canned - Refrigerated
    {
        "food_category": "Packaged & Canned",
        "product_type": "Refrigerated Packaged Ready-to-Eat Goods",
        "storage_condition": "refrigerated",
        "temperature_min_c": 1.0,
        "temperature_max_c": 4.0,
        "max_holding_hours": 720.0,
        "source_name": "FSSAI (Packaging and Labelling) Regulations, 2011",
        "source_url": "https://www.fssai.gov.in",
        "rule_version": "FSSAI-2023-V1",
        "requires_manual_verification": False,
    },
]

def seed_safety_rules(db: Session = None) -> int:
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        inserted = 0
        for r_data in CURATED_RULES:
            existing = (
                db.query(FoodSafetyRule)
                .filter(
                    FoodSafetyRule.food_category == r_data["food_category"],
                    FoodSafetyRule.product_type == r_data["product_type"],
                    FoodSafetyRule.storage_condition == r_data["storage_condition"],
                )
                .first()
            )
            if not existing:
                rule = FoodSafetyRule(**r_data, created_at=datetime.utcnow())
                db.add(rule)
                inserted += 1
            else:
                # Update attributes
                existing.max_holding_hours = r_data["max_holding_hours"]
                existing.source_name = r_data["source_name"]
                existing.source_url = r_data["source_url"]
                existing.temperature_min_c = r_data["temperature_min_c"]
                existing.temperature_max_c = r_data["temperature_max_c"]

        db.commit()
        print(f"[FoodSafetyRules] Seeded {inserted} new rules, total active rules: {len(CURATED_RULES)}.")
        return inserted
    except Exception as e:
        db.rollback()
        print(f"[FoodSafetyRules] Error seeding rules: {e}")
        return 0
    finally:
        if own_session:
            db.close()

if __name__ == "__main__":
    seed_safety_rules()
