import math
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.food_batch import FoodBatch
from app.models.ngo import NGOPartner
from app.utils.dates import utc_now, to_naive_utc

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two geographic coordinates in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class SmartMatchingService:
    DEFAULT_WEIGHTS = {
        "distance": 0.30,
        "category": 0.25,
        "quantity": 0.20,
        "expiry": 0.15,
        "availability": 0.10,
    }

    @classmethod
    def match_ngos_for_donation(
        cls,
        db: Session,
        batch_id: int,
        weights: Optional[Dict[str, float]] = None,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Ranks verified NGO partners for a specific food batch using weighted multi-factor scoring.
        """
        batch = db.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).first()
        if not batch:
            return []

        w = weights or cls.DEFAULT_WEIGHTS
        ngos = db.query(NGOPartner).all()
        scored_recommendations = []
        now = utc_now()
        effective_expiry = to_naive_utc(batch.effective_expiry_time or batch.expiry_time)
        hours_to_expiry = max(0.1, (effective_expiry - now).total_seconds() / 3600.0)

        donor_lat = float(batch.latitude) if batch.latitude is not None else (
            float(batch.donor.latitude) if batch.donor and batch.donor.latitude is not None else None
        )
        donor_lon = float(batch.longitude) if batch.longitude is not None else (
            float(batch.donor.longitude) if batch.donor and batch.donor.longitude is not None else None
        )

        for ngo in ngos:
            # 1. Distance suitability (30%)
            distance_km = None
            dist_score = 50.0  # Default if coordinates missing
            if donor_lat is not None and donor_lon is not None and ngo.latitude is not None and ngo.longitude is not None:
                distance_km = round(haversine_distance_km(donor_lat, donor_lon, float(ngo.latitude), float(ngo.longitude)), 1)
                if distance_km <= 5.0:
                    dist_score = 100.0
                elif distance_km <= 15.0:
                    dist_score = 75.0
                elif distance_km <= 30.0:
                    dist_score = 45.0
                else:
                    dist_score = max(10.0, 100.0 - (distance_km * 2))

            # 2. Food category compatibility (25%)
            cat_pref = (ngo.preferred_categories or "").lower()
            if not cat_pref or batch.food_category.lower() in cat_pref or "all" in cat_pref:
                cat_score = 100.0
            else:
                cat_score = 35.0

            # 3. Quantity suitability (20%)
            capacity = ngo.capacity_servings or 100
            batch_qty = float(batch.quantity)
            if batch_qty <= capacity:
                qty_score = 100.0
            else:
                # Scaled ratio if batch is larger than NGO's single-trip capacity
                qty_score = max(30.0, (capacity / batch_qty) * 100.0)

            # 4. Expiry urgency & collection feasibility (15%)
            if hours_to_expiry < 3.0:
                # Urgent: prioritize close NGOs
                if distance_km is not None and distance_km <= 10.0:
                    expiry_score = 100.0
                else:
                    expiry_score = 60.0
            elif hours_to_expiry <= 8.0:
                expiry_score = 85.0
            else:
                expiry_score = 70.0

            # 5. Availability & operating hours (10%)
            avail_score = 100.0 if ngo.is_active else 20.0

            # Weighted Total
            total_score = round(
                (dist_score * w["distance"])
                + (cat_score * w["category"])
                + (qty_score * w["quantity"])
                + (expiry_score * w["expiry"])
                + (avail_score * w["availability"]),
                1
            )

            # Rationale explanation
            reasons = []
            if distance_km is not None:
                reasons.append(f"Located {distance_km} km away")
            if cat_score >= 90.0:
                reasons.append(f"Specializes in {batch.food_category}")
            if qty_score >= 90.0:
                reasons.append(f"Adequate intake capacity ({capacity} servings)")
            if hours_to_expiry < 3.0 and (distance_km is None or distance_km <= 10.0):
                reasons.append("Fast turnaround for imminent expiry")

            scored_recommendations.append({
                "ngo_id": ngo.ngo_id,
                "ngo_name": ngo.ngo_name,
                "phone": ngo.phone,
                "address": ngo.address,
                "distance_km": distance_km,
                "capacity_servings": capacity,
                "operating_hours": ngo.operating_hours or "09:00 - 21:00",
                "match_score": total_score,
                "score_breakdown": {
                    "distance": round(dist_score, 1),
                    "category_compatibility": round(cat_score, 1),
                    "quantity_suitability": round(qty_score, 1),
                    "expiry_urgency": round(expiry_score, 1),
                    "availability": round(avail_score, 1),
                },
                "explanation": " • ".join(reasons) if reasons else "Eligible registered community partner.",
            })

        scored_recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_recommendations[:max_results]

