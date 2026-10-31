# Community Food Rescue Network with Hosted Gemma 4 & FSSAI Safety Standards

A complete, production-grade local web platform designed to eliminate surplus food waste and connect food donors (restaurants, college messes, banquet caterers) with verified NGO shelters and community volunteer couriers in real time.

Now upgraded with **Google Hosted Gemma 4 (`gemma-4-26b-a4b-it`)**, a **Curated FSSAI Food Safety & Statutory Expiry Engine**, **Two-Stage Handover Verification (OTP/QR)**, **Smart Weighted NGO Matching**, **9-Stage Lifecycle Timeline**, **Partial Quantity Allocation (Multi-NGO Splitting)**, and a **Vibrant SaaS Interface**.

Built with a high-performance **FastAPI (Python 3.11)** backend, a modern **React + TypeScript + Tailwind CSS (Vite)** frontend, and a normalized **MariaDB/MySQL (XAMPP)** relational database.

---

## 1. System Architecture & Tech Stack

```text
+-----------------------------------------------------------------------------------------+
|                                      WEB FRONTEND                                       |
|             React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons                  |
|        Role-Specific Sidebar + Quantity Progress Bars + 9-Stage Lifecycle Timelines     |
|        Two-Stage OTP/QR Handover Modals + Smart Matching Cards + Expiry Callouts        |
|        Port: http://localhost:3000 (Proxied /api -> :5000)                              |
+-----------------------------------------------------------------------------------------+
                                           |
                                   (HTTP REST / JSON)
                                           v
+-----------------------------------------------------------------------------------------+
|                                    FASTAPI BACKEND                                      |
|            Python 3.11 + Pydantic v2 + SQLAlchemy 2.x + Alembic Migrations              |
|   • Google Hosted Gemma 4 AI (`gemma-4-26b-a4b-it` via official `google-genai` SDK)     |
|   • Curated FSSAI Safety Validator (17 Statutory Rules with Automatic Expiry Capping)   |
|   • Two-Stage Handover Verification (SHA-256 Salted OTP & QR Tokens, 5 Attempts Lockout)|
|   • Smart Weighted NGO Matching Engine (Distance 30%, Category 25%, Capacity 20%...)    |
|   • Partial Allocation Engine (Atomic Row-Level Locking `with_for_update()`)            |
|   • 9-Stage Lifecycle Timeline & Real-Time Role Notification Engine                     |
|   Port: http://127.0.0.1:5000 | Swagger Docs: http://127.0.0.1:5000/api/docs            |
+-----------------------------------------------------------------------------------------+
                                           |
                                  (PyMySQL / TCP 3306)
                                           v
+-----------------------------------------------------------------------------------------+
|                               MYSQL RELATIONAL DATABASE                                 |
|          Database: community_food_rescue (MariaDB 10.4.32 / InnoDB, 3NF Normalization)   |
|   `users`, `donors`, `ngo_partners`, `volunteers`, `food_batches`, `food_safety_rules`,  |
|   `pickup_requests`, `delivery_logs`, `notifications`                                   |
|   Alembic Revision: `3b4269e5df29` (Verification hashes, matching & timeline fields)    |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Core Upgrades & Feature Highlights

### A. Manual Donation Listing & Clear Statutory Expiry Display
- **Clean Manual Entry**: Food image recognition and AI description generation have been completely removed in favor of clean, donor-entered details (name, category, description, quantity, preparation time, storage conditions, and expiry time).
- **Ordinary Photo Uploads**: Supported via `POST /api/donations/upload-image` with validation for JPEG/PNG/WebP formats and $\le 10$ MB size limits.
- **Maximum Permitted Holding Duration Callout**:
  - Dynamically calculates the FSSAI statutory maximum holding limit upon selecting food type and storage conditions.
  - Clearly displayed directly below the expiry field on the donor form:
    - **Statutory Holding Limit**: e.g., `4 hours maximum holding time`
    - **Preparation Time**: e.g., `10:00 AM`
    - **Latest Permitted Expiry**: e.g., `2:00 PM`
    - **Regulatory Citation**: FSSAI Rule Clause
  - **Strict Enforcement**: The donor can pick an earlier expiry, but selecting any time past the statutory limit is blocked on the frontend and strictly capped on the backend (`effective_expiry = min(user_selected, approved_maximum)`).

### B. Strict Role-Based Access Control (RBAC) & IDOR Protection
- **Dedicated Role Portals**:
  - **Donor**: Overview, List Food, My Donations, Quantity Allocation, Notifications, Profile.
  - **NGO Partner**: Overview, Explore Surplus, My Claims, Quantity Allocation, Notifications, Profile.
  - **Volunteer Courier**: Overview, Available Deliveries, My Assigned Deliveries, Delivery History, Notifications, Availability Status.
- **Navigation Menu Isolation**: Unauthorized navigation links are completely hidden from non-eligible roles.
- **Direct Route Guards**: Client-side protected routes redirect unauthorized users directly to their designated dashboard.
- **IDOR Protection**: Every backend route verifies resource ownership (e.g., donors can only edit/cancel their own donations, NGOs can only view their own requests, couriers can only verify tasks assigned to them). Unauthorized access returns **HTTP 403 Forbidden**.

### C. Two-Stage Handover Verification (OTP & QR)
- **Stage 1: Pickup Handover (Donor $\rightarrow$ Volunteer)**:
  - When a courier claims an assignment, a secure 6-digit OTP and QR token are initialized.
  - The plaintext code is provided securely to the Donor.
  - Upon arrival at the donor's address, the courier enters the 6-digit code or scans the QR code.
  - On verification, request status atomically transitions from `assigned` $\rightarrow$ `collected`.
- **Stage 2: Delivery Handover (Volunteer $\rightarrow$ NGO)**:
  - When food is collected, Stage 2 Delivery OTP and QR token are automatically generated for the recipient NGO.
  - Upon delivery at the shelter, the courier enters the NGO's 6-digit delivery code.
  - On verification, request status transitions from `collected` $\rightarrow$ `delivered`.
- **Security & Integrity Guarantee**:
  - Plaintext OTPs are **never stored** in the database; only SHA-256 salted hashes are persisted.
  - **Single-Use**: OTP hash is wiped immediately upon successful verification to prevent replay attacks.
  - **Brute-Force Lockout**: Locked after 5 failed verification attempts (HTTP 429 Too Many Requests).
  - Couriers are strictly forbidden from inspecting handover codes via API (HTTP 403 Forbidden).

### D. Smart Multi-Factor NGO Matching Engine
Ranks registered, active NGO partners for any food batch using a transparent 5-factor weighted algorithm:
1. **Haversine Distance Suitability (30%)**: Great-circle distance calculated between donor and NGO coordinates ($< 5\text{ km} \rightarrow 100\%$, $< 15\text{ km} \rightarrow 75\%$, $< 30\text{ km} \rightarrow 45\%$).
2. **Food Category Compatibility (25%)**: Matches NGO preferred intake categories.
3. **Quantity Capacity Suitability (20%)**: Checks NGO intake capacity servings against surplus size.
4. **Expiry Urgency & Turnaround (15%)**: Prioritizes closest NGOs when food expiry is $< 3$ hours away.
5. **Operating Availability (10%)**: Active status and operating hours verification.

Every match includes a transparent match percentage and rationale explanation (e.g., *Located 2.4 km away • Specializes in Cooked Meals • Adequate intake capacity*).

### E. 9-Stage Donation Lifecycle Timeline
Visual, chronological tracking rendered across both batch and request details:
1. **Donation Listed**: Surplus posted by donor.
2. **FSSAI Safety Verified**: Validated against statutory holding limits.
3. **Smart NGO Match Discovered**: Top NGO partners ranked by matching engine.
4. **Portion Reserved by NGO**: Atomic partial claim submitted.
5. **Courier Assigned**: Volunteer accepts task; Stage 1 OTP initialized.
6. **Pickup Handover Verified**: Donor OTP verified at pickup location.
7. **Food In Transit**: Courier actively transporting meals.
8. **Delivery Handover Verified**: NGO shelter OTP verified upon arrival.
9. **Redistribution Completed**: Surplus meals distributed to beneficiaries.

### F. Atomic Partial Quantity Allocation (Multi-NGO Splitting)
- Allows multiple NGOs to partially claim portions of a large donation batch (e.g., 50 servings split into 20 and 30).
- **Concurrency Invariant**: Row-level locking via SQLAlchemy `with_for_update()` ensures zero overbooking under simultaneous requests.
- Automatic release back to surplus upon claim cancellation or rejection.

### G. Vibrant SaaS Interface
Styled with the requested modern palette:
- **Forest Green** (`#174D32`), **Emerald** (`#147D54`), **Leaf Green** (`#36A853`), **Mint** (`#DDF4E4`)
- **Deep Navy** (`#23395B`), **Soft Blue** (`#E5F0FF`), **Warm Orange** (`#F4A340`), **Soft Coral** (`#FFE4DC`), **Lavender** (`#EEE8FF`)
- Responsive cards with tinted backgrounds, clean typography, and interactive status badges.

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

### Verified Test Suite (37 Tests Passing):
- **Two-Stage Handover & OTP/QR Verification (`test_verification_handover.py`)**:
  - `test_otp_hashing_and_generation`: Validates cryptographic SHA-256 salted hashing and plaintext masking.
  - `test_handover_verification_workflow`: Tests full Stage 1 donor-to-courier handover, IDOR courier isolation (403), invalid code handling with remaining attempt counts, replay attack prevention, and Stage 2 courier-to-shelter delivery.
- **Smart Weighted NGO Matching (`test_smart_matching.py`)**:
  - `test_haversine_distance`: Verifies great-circle geographic distance calculations.
  - `test_matching_recommendations_endpoint`: Verifies 5-factor scoring (distance 30%, category 25%, capacity 20%, urgency 15%, availability 10%) and transparent explanations.
- **Timeline & In-App Notifications (`test_timeline_and_notifications.py`)**:
  - `test_batch_and_request_timeline`: Validates chronological 9-stage lifecycle events.
  - `test_in_app_notifications_flow`: Validates real-time role-targeted alerts.
- **Food Safety & FSSAI Expiry Calculation (`test_expiry_autofill_workflow.py`, `test_expiry_validation.py`, `test_expiry.py`)**:
  - Statutory holding hours, regulatory clauses, hot/cold holding thresholds, dynamic background expiries, and automated capping.
- **Atomic Concurrency & Partial Quantity Allocation (`test_partial_allocation.py`, `test_concurrency.py`)**:
  - Simultaneous multi-NGO splitting, `with_for_update()` row locking, and conflict prevention.
- **Ordinary Photo Uploads (`test_photo_upload.py`)**:
  - Validates JPEG/PNG/WebP formats and 10MB limits while rejecting invalid extensions.
- **Role Permissions & RBAC (`test_role_permissions.py`)**:
  - Enforces cross-role isolation and unauthenticated rejections across all endpoints.
- **Hosted Gemma 4 AI & Intent Chatbot (`test_ai_service.py`, `test_intent_chatbot.py`)**:
  - Intent classification, tool routing, confirmation workflows, and deterministic fallback resilience.

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
