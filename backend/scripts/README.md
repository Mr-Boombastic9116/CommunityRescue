# Community Food Rescue Network - Synthetic Data & Seeder Documentation

This directory provides idempotent seeding and verification scripts to populate the MySQL database with realistic synthetic data tailored for development, testing, and college DBMS project demonstrations.

---

## 1. Overview of Synthetic Data

All entities are configured with plausible, geographically coordinated locations in **Goa, India** (Panaji, Margao, Mapusa, Vasco da Gama, Porvorim, Ponda, and Bambolim).

### Synthetic Entities & Breakdown

| Entity | Count | Description / Role |
|---|---|---|
| **Users** | 20 | 6 Donors, 5 NGOs, 9 Volunteers (Password for all: `Password123!`) |
| **Donors** | 6 | Restaurants, college messes, bakeries, caterers, banquet kitchens |
| **NGO Partners** | 5 | Shelters, food missions, children's homes, community kitchens |
| **Volunteers** | 9 | 5 Available, 2 Busy, 2 Offline |
| **Food Batches** | 20 | Cooked Meals (14), Bakery (4), Fresh Produce (2) across all lifecycle statuses |
| **Pickup Requests** | 15 | 3 Requested, 3 Assigned, 3 Collected, 3 Delivered, 3 Cancelled |
| **Delivery Logs** | 36 | Complete audit trail covering food rescue lifecycle transitions |
| **Notifications** | 25+ | Cross-role in-app alerts (requests, claims, transit, deliveries, expiries) |

---

## 2. Demo User Credentials

All synthetic demo accounts use the standard password: **`Password123!`**

### A. Donors (Food Providers)
| Email | Organization Name | Location | Focus Area |
|---|---|---|---|
| `green_bites@example.com` | Green Bites Organic Cafe | Miramar, Panaji | Organic Cafe & Sandwiches |
| `campus_mess@example.com` | Goa University Dining Hall | Taleigao Plateau | University Mess & Rice/Meals |
| `ritz_classic@example.com` | Ritz Classic Seafood Restaurant | 18th June Road, Panaji | Coastal & Thali Meals |
| `bakers_street@example.com` | Bakers Street Patisserie | Chogm Road, Porvorim | Artisan Bakery & Bread |
| `grand_hyatt_kitchen@example.com` | Grand Hyatt Banquet Kitchen | Bambolim Bay | Banquet Buffets & Produce |
| `spice_goa@example.com` | Spice Goa Caterers & Kitchen | Karaswada, Mapusa | Catering & Biryani |

### B. NGO Partners (Food Recipients)
| Email | NGO Organization Name | Location | Primary Mission |
|---|---|---|---|
| `care_foundation@example.com` | Care & Hope Shelter Home | Altinho, Panaji | Homeless & Shelter Care |
| `feed_all@example.com` | Feed The Hungry Mission Goa | Station Road, Margao | Daily Food Relief |
| `st_anthony_home@example.com` | St. Anthony's Children's Home & Care | Duler, Mapusa | Orphanage & Youth Center |
| `pragati_trust@example.com` | Pragati Community Welfare Center | Swatantra Path, Vasco | Slum Community Kitchen |
| `sneha_mandir@example.com` | Sneha Mandir Elderly Care & Food Center | Bandora, Ponda | Elder Care & Nutrition |

### C. Volunteers (Rescue Couriers)
| Email | Name | Phone | Status |
|---|---|---|---|
| `alex_volunteer@example.com` | Alex Rivera | +91 97654 32101 | `available` |
| `priya_volunteer@example.com` | Priya Sharma | +91 97654 32102 | `available` |
| `rohan_volunteer@example.com` | Rohan Fernandes | +91 97654 32103 | `available` |
| `ananya_volunteer@example.com` | Ananya Deshmukh | +91 97654 32104 | `available` |
| `vikram_volunteer@example.com` | Vikram Naik | +91 97654 32105 | `available` |
| `neha_volunteer@example.com` | Neha Kamat | +91 97654 32106 | `busy` |
| `samuel_volunteer@example.com` | Samuel D'Souza | +91 97654 32107 | `busy` |
| `fatima_volunteer@example.com` | Fatima Bi Sheikh | +91 97654 32108 | `offline` |
| `rahul_volunteer@example.com` | Rahul Vernekar | +91 97654 32109 | `offline` |

---

## 3. Files Created for Seeding and Verification

1. **`scripts/seed_data.py`** (and `backend/scripts/seed_data.py`):
   - Python SQLAlchemy idempotent seeder.
   - Populates or updates the synthetic records with relative timestamps calculated dynamically from current UTC time.
2. **`database/seed_data.sql`** (and `scripts/seed_data.sql`):
   - Deterministic MySQL SQL script using `ON DUPLICATE KEY UPDATE` and `NOT EXISTS`.
   - Never hardcodes assumptions about auto-increment IDs; looks up relational keys dynamically via subqueries.
3. **`scripts/verify_seed_data.py`** (and `backend/scripts/verify_seed_data.py`):
   - Comprehensive verification suite checking record counts, foreign key constraints, timestamp progression, and executing live DBMS analytical dashboard queries.
4. **`scripts/README.md`** & **`backend/scripts/README.md`**:
   - Complete reference documentation for instructors, students, and evaluators.

---

## 4. Prerequisites

1. **MySQL Server Running**:
   - Open **XAMPP Control Panel** and ensure **MySQL** is started (Default port: `3306`).
2. **Python Virtual Environment**:
   - Project Python virtual environment located at `.\venv`.
3. **Database Schema Initialized**:
   - The database `community_food_rescue` must exist and schema tables created.
   - If not yet initialized, run:
     ```powershell
     .\venv\Scripts\python.exe -m alembic -c backend\alembic.ini upgrade head
     ```
     Or import `scripts\schema.sql` via MySQL / phpMyAdmin.

---

## 5. Execution Instructions (Windows PowerShell)

### Step 1: Run the Python Idempotent Seeder
From the project root `C:\Users\Shreyank\Desktop\NGO`:

```powershell
.\venv\Scripts\python.exe scripts\seed_data.py
```
*(Alternative path: `.\venv\Scripts\python.exe backend\scripts\seed_data.py`)*

### Step 2: Verify the Seeded Records & Analytics
Run the automated verification script:

```powershell
.\venv\Scripts\python.exe scripts\verify_seed_data.py
```

### Step 3 (Optional): Alternative Seeding via MySQL CLI / phpMyAdmin
You can also run the SQL seed file directly against MySQL:

```powershell
& "C:\xampp\mysql\bin\mysql.exe" -u root community_food_rescue -e "source database/seed_data.sql"
```

---

## 6. How Idempotency and Duplicates are Handled

- **User Accounts**: Matched uniquely by `email`. If an account exists, its profile is updated/reused; no duplicate user is created.
- **Profiles**: Matched 1-to-1 on `user_id`.
- **Food Batches**: Matched on `(donor_id, food_name)`. Running the seeder again refreshes relative expiry timestamps so urgent countdown badges and expiry tags work dynamically.
- **Pickup Requests & Logs**: Checked conditionally before insertion; rerunning skips previously recorded audit events.

---

## 7. Cleaning Up Synthetic Records

To remove **only** the synthetic demo records without affecting user-created accounts or other test data, run:

```powershell
.\venv\Scripts\python.exe scripts\seed_data.py --clean
```

To perform a clean refresh (wipe synthetic records and reinsert fresh):

```powershell
.\venv\Scripts\python.exe scripts\seed_data.py --refresh
```

