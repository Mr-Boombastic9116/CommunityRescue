# Community Food Rescue Network with Hosted Gemma 4 & FSSAI Safety Standards

A complete, production-grade local web platform designed to eliminate surplus food waste and connect food donors (restaurants, college messes, banquet caterers) with verified NGO shelters and community volunteer couriers in real time.

Now upgraded with **Google Hosted Gemma 4 (`gemma-4-26b-a4b-it`)**, a **Curated FSSAI Food Safety & Statutory Expiry Engine**, **Partial Quantity Allocation (Multi-NGO Splitting)**, and a **Premium Food-Tech SaaS Interface**.

Built with a high-performance **FastAPI (Python 3.11)** backend, a modern **React + TypeScript + Tailwind CSS (Vite)** frontend, and a normalized **MySQL (XAMPP / MariaDB)** relational database.

---

## 1. System Architecture & Tech Stack

```text
+-----------------------------------------------------------------------------------------+
|                                      WEB FRONTEND                                       |
|             React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons                  |
|        Role-Specific Sidebar + Quantity Progress Bars + Gemma 4 AI Drawer               |
|        Port: http://localhost:3000 (Proxied /api -> :5000)                              |
+-----------------------------------------------------------------------------------------+
                                           |
                                   (HTTP REST / JSON)
                                           v
+-----------------------------------------------------------------------------------------+
|                                    FASTAPI BACKEND                                      |
|            Python 3.11 + Pydantic v2 + SQLAlchemy 2.x + Alembic Migrations              |
|   • Google Hosted Gemma 4 AI (`gemma-4-26b-a4b-it` via official `google-genai` SDK)     |
|   • Curated FSSAI Safety Validator (17 Statutory Rules with Automatic Capping)          |
|   • Partial Allocation Engine (Atomic Row Locking `with_for_update()`)                  |
|   • JWT Auth + Background Expiry Loop + Tamper-Evident Audit Delivery Logs             |
|   Port: http://127.0.0.1:5000 | Swagger Docs: http://127.0.0.1:5000/api/docs            |
+-----------------------------------------------------------------------------------------+
                                           |
                                  (PyMySQL / TCP 3306)
                                           v
+-----------------------------------------------------------------------------------------+
|                               MYSQL RELATIONAL DATABASE                                 |
|          Database: community_food_rescue (InnoDB, 3NF Normalization)                    |
|   `users`, `donors`, `ngo_partners`, `volunteers`, `food_batches`, `food_safety_rules`,  |
|   `pickup_requests`, `delivery_logs`, `notifications`                                   |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Core Upgrades & Innovations

### A. Hosted Gemma 4 Integration (`gemma-4-26b-a4b-it`)
- **SDK**: Official `google-genai` Python SDK connecting directly to hosted Gemma 4 models.
- **Auto-Categorization & Normalization**: Suggests food category, safe storage condition, shelf-life duration, and dietary tags based on food names and descriptions.
- **Contextual Chatbot**: Answers user inquiries with zero data leakage, strict RBAC isolation (donors cannot see other donors' private batches), and FSSAI statutory safety compliance.
- **Smart NGO Matching**: Ranks surplus meals according to distance, nutritional balance, and urgency.
- **Volunteer Task Prioritization**: Ranks pending pickups by bacterial proliferation risk and time-to-expiry.
- **Zero Hallucination & Deterministic Fallbacks**: If the AI API is unreachable or times out, the backend gracefully activates deterministic rule-based algorithms.

### B. Curated FSSAI Food Safety Standards Engine
- **Statutory Rules Matrix (`food_safety_rules` table)**:
  - **Cooked Meals (Ambient)**: Max 4 hours holding limit.
  - **Cooked Meals (Hot Holding >= 60°C)**: Max 6 hours.
  - **Cooked Meals (Refrigerated <= 5°C)**: Max 48 hours.
  - **Dairy & Paneer (Ambient)**: Max 2 hours.
  - **Dairy & Milk (Refrigerated)**: Max 24 hours.
  - **Meat / Seafood (Ambient)**: Max 2.5 hours.
  - **Bakery & Bread**: Max 72 hours.
  - **Packaged / Canned**: Strictly bounded by manufacturer printed expiry date.
- **Automated Statutory Capping**:
  ```python
  if user_expiry > statutory_maximum:
      effective_expiry = statutory_maximum
      validation_status = "adjusted"
      expiry_adjustment_reason = "Selected expiry exceeded certified safety limit..."
  ```

### C. Partial Quantity Allocation (Multi-NGO Splitting)
- A donor listing 50 kg of rice can now fulfill requests from multiple NGOs (e.g., NGO 1 requests 20 kg, NGO 2 requests 30 kg).
- **Concurrency Invariant**:
  ```python
  batch = db.query(FoodBatch).filter(FoodBatch.batch_id == batch_id).with_for_update().first()
  ```
  Row-level locking guarantees that two simultaneous requests cannot overbook the remaining quantity.
- **Derived Batch Statuses**:
  - `available` (100% quantity free)
  - `partially_reserved` (0 < remaining < total)
  - `reserved` (100% reserved across active claims)
  - `assigned` / `collected` / `delivered` / `expired` / `cancelled`

### D. Premium Food-Tech SaaS UI Redesign
- **Color Palette**: Forest Green (`#15803d`, `#166534`, `#14532d`), Emerald (`#10b981`), Mint, warm off-white background (`#f8fafc`).
- **Role-Specific Sidebar**:
  - **Donor**: Overview, List Food, My Donations, Quantity Allocation, Expiry Alerts, AI Assistant, Profile.
  - **NGO**: Overview, Explore Food, My Requests, Quantity Allocation, Expiry Alerts, AI Assistant, Profile.
  - **Volunteer**: Overview, Available Tasks, My Assignments, Delivery History, Expiry Alerts, AI Assistant, Duty Status Toggle (Online/Busy/Offline).
- **Animated Components**:
  - `QuantityProgressBar`: Multi-segment colored allocation track showing reserved vs available percentages.
  - `ExpiryAlertBanner`: Instant visual cues for FSSAI-capped donations and urgent expiries.
  - `AIAssistantDrawer`: Global slide-out interactive AI chat assistant powered by hosted Gemma 4.
  - Dedicated pages: `QuantityAllocationPage`, `ExpiryAlertsPage`, and full-screen `AIAssistantPage`.

---

## 3. Database Schema

1. **`users`**: Base credentials table (`user_id`, `name`, `email` [UNIQUE], `password_hash`, `role`, `is_active`, timestamps).
2. **`donors`**: 1-to-1 profile (`donor_id`, `user_id` [FK->users], `donor_name`, `phone`, `address`, `latitude`, `longitude`).
3. **`ngo_partners`**: 1-to-1 profile (`ngo_id`, `user_id` [FK->users], `ngo_name`, `phone`, `address`, `latitude`, `longitude`).
4. **`volunteers`**: 1-to-1 profile (`volunteer_id`, `user_id` [FK->users], `volunteer_name`, `phone`, `availability_status`).
5. **`food_safety_rules`**: Curated FSSAI standards (`rule_id`, `food_category`, `product_type`, `storage_condition`, `max_holding_hours`, `fssai_guideline_clause`, `source_name`).
6. **`food_batches`**: Listed surplus batches (`batch_id`, `donor_id`, `food_name`, `food_description`, `food_category`, `quantity`, `unit`, `storage_condition`, `storage_temperature`, `prepared_at`, `user_expiry_time`, `effective_expiry_time`, `packaging_expiry_time`, `expiry_validation_status`, `expiry_rule_applied`, `food_status`).
7. **`pickup_requests`**: Individual NGO portion claims (`request_id`, `batch_id`, `ngo_id`, `volunteer_id`, `requested_quantity`, `unit`, `request_status`, timestamps).
8. **`delivery_logs`**: Permanent tamper-evident delivery audit trail.
9. **`notifications`**: Real-time alerts for donors, NGOs, and couriers.

---

## 4. Quick Start (Windows Local)

### Prerequisites:
1. **XAMPP**: Ensure MySQL is started on port 3306.
2. **Python 3.11+** installed.
3. **Node.js 18+** installed.

### Launching the Application:

**1. Launch Backend:**
```cmd
run_backend.bat
```
*Backend runs on `http://127.0.0.1:5000` with Swagger documentation at `http://127.0.0.1:5000/api/docs`.*

**2. Launch Frontend:**
```cmd
run_frontend.bat
```
*Frontend runs on `http://localhost:3000` with instant proxy to backend.*

---

## 5. Automated Verification & Test Suite

Run the complete backend test suite:
```cmd
.\venv\Scripts\pytest.exe backend\tests -v
```

### Verified Test Suite (17 Tests Passing):
- `test_ai_service.py`:
  - `test_ai_status_endpoint` (Gemma 4 integration verified)
  - `test_ai_categorize_endpoint` (Live hosted Gemma 4 categorization)
  - `test_ai_fallback_resilience` (Deterministic fallback schema validation)
  - `test_ai_chat_endpoint` (Contextual zero-hallucination chat)
- `test_expiry_validation.py`:
  - `test_expiry_earlier_than_maximum` (Safe user expiry verified)
  - `test_expiry_exceeding_maximum_capped` (FSSAI statutory capping safely enforced)
  - `test_hot_holding_storage_condition` (Hot holding >= 60°C rules)
  - `test_refrigerated_storage_condition` (Cold chain <= 5°C rules)
  - `test_packaging_expiry_earlier_caps_effective` (Manufacturer label capping)
- `test_partial_allocation.py`:
  - `test_partial_quantity_splitting` (Multi-NGO partial splitting, remaining quantity tracking, 409 conflict overbooking prevention, and cancellation release)
- `test_concurrency.py`:
  - `test_prevent_concurrent_claim` (Row-level locking with `with_for_update()`)
- `test_donations.py`, `test_auth.py`, `test_expiry.py`, `test_requests.py`:
  - Full end-to-end authentication, listing, claiming, and delivery lifecycle.

---

## 6. Pre-Configured Demo Accounts

| Role | Email | Password |
|---|---|---|
| **Donor** | `donor1@gmail.com` | `password` |
| **Donor** | `donor2@gmail.com` | `password` |
| **NGO Partner** | `ngo1@gmail.com` | `password` |
| **NGO Partner** | `ngo2@gmail.com` | `password` |
| **Volunteer** | `volunteer1@gmail.com` | `password` |
| **Volunteer** | `volunteer2@gmail.com` | `password` |
