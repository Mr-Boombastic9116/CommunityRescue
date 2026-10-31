-- ============================================================================
-- COMMUNITY FOOD RESCUE NETWORK - DETERMINISTIC SYNTHETIC SEED DATA
-- Database: community_food_rescue
-- Engine: MySQL 8.x / MariaDB 10.4+ (XAMPP Compatible)
-- Location: Goa, India
-- Idempotency: Safe to run repeatedly (uses ON DUPLICATE KEY UPDATE and NOT EXISTS)
-- ============================================================================

USE `community_food_rescue`;

SET @DEFAULT_PASSWORD_HASH = '$2b$12$/m8YuZOBEOY5VnSu5TyBU.8.YauOTruoT20JMuKcMOwTT7HROpvkK'; -- Password123!
SET @NOW = UTC_TIMESTAMP();

-- ----------------------------------------------------------------------------
-- 1. USERS (20 Fictional Accounts: 6 Donors, 5 NGOs, 9 Volunteers)
-- ----------------------------------------------------------------------------
INSERT INTO `users` (`name`, `email`, `password_hash`, `role`, `is_active`, `created_at`, `updated_at`)
VALUES
  -- 6 Donors
  ('Green Bites Organic Cafe', 'green_bites@example.com', @DEFAULT_PASSWORD_HASH, 'donor', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Goa University Dining Hall', 'campus_mess@example.com', @DEFAULT_PASSWORD_HASH, 'donor', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Ritz Classic Seafood Restaurant', 'ritz_classic@example.com', @DEFAULT_PASSWORD_HASH, 'donor', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Bakers Street Patisserie', 'bakers_street@example.com', @DEFAULT_PASSWORD_HASH, 'donor', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Grand Hyatt Banquet Kitchen', 'grand_hyatt_kitchen@example.com', @DEFAULT_PASSWORD_HASH, 'donor', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Spice Goa Caterers & Kitchen', 'spice_goa@example.com', @DEFAULT_PASSWORD_HASH, 'donor', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),

  -- 5 NGOs
  ('Care & Hope Shelter', 'care_foundation@example.com', @DEFAULT_PASSWORD_HASH, 'ngo', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Feed The Hungry Mission Goa', 'feed_all@example.com', @DEFAULT_PASSWORD_HASH, 'ngo', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('St. Anthony Children\'s Home', 'st_anthony_home@example.com', @DEFAULT_PASSWORD_HASH, 'ngo', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Pragati Community Kitchen', 'pragati_trust@example.com', @DEFAULT_PASSWORD_HASH, 'ngo', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Sneha Mandir Welfare Foundation', 'sneha_mandir@example.com', @DEFAULT_PASSWORD_HASH, 'ngo', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),

  -- 9 Volunteers
  ('Alex Rivera', 'alex_volunteer@example.com', @DEFAULT_PASSWORD_HASH, 'volunteer', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Priya Sharma', 'priya_volunteer@example.com', @DEFAULT_PASSWORD_HASH, 'volunteer', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Rohan Fernandes', 'rohan_volunteer@example.com', @DEFAULT_PASSWORD_HASH, 'volunteer', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Ananya Deshmukh', 'ananya_volunteer@example.com', @DEFAULT_PASSWORD_HASH, 'volunteer', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Vikram Naik', 'vikram_volunteer@example.com', @DEFAULT_PASSWORD_HASH, 'volunteer', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Neha Kamat', 'neha_volunteer@example.com', @DEFAULT_PASSWORD_HASH, 'volunteer', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Samuel D\'Souza', 'samuel_volunteer@example.com', @DEFAULT_PASSWORD_HASH, 'volunteer', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Fatima Bi Sheikh', 'fatima_volunteer@example.com', @DEFAULT_PASSWORD_HASH, 'volunteer', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW),
  ('Rahul Vernekar', 'rahul_volunteer@example.com', @DEFAULT_PASSWORD_HASH, 'volunteer', 1, DATE_SUB(@NOW, INTERVAL 30 DAY), @NOW)
ON DUPLICATE KEY UPDATE
  `name` = VALUES(`name`),
  `role` = VALUES(`role`),
  `is_active` = VALUES(`is_active`),
  `updated_at` = VALUES(`updated_at`);

-- ----------------------------------------------------------------------------
-- 2. DONOR PROFILES (Goa, India Coordinates)
-- ----------------------------------------------------------------------------
INSERT INTO `donors` (`user_id`, `donor_name`, `phone`, `address`, `latitude`, `longitude`)
SELECT `user_id`, 'Green Bites Organic Cafe', '+91 98221 12345', '142 Dayanand Bandodkar Marg, Miramar, Panaji, Goa 403001', 15.48600000, 73.80800000
FROM `users` WHERE `email` = 'green_bites@example.com'
ON DUPLICATE KEY UPDATE `donor_name` = VALUES(`donor_name`), `phone` = VALUES(`phone`), `address` = VALUES(`address`), `latitude` = VALUES(`latitude`), `longitude` = VALUES(`longitude`);

INSERT INTO `donors` (`user_id`, `donor_name`, `phone`, `address`, `latitude`, `longitude`)
SELECT `user_id`, 'Goa University Dining Hall', '+91 98222 23456', 'Central Mess Block, Goa University Campus, Taleigao Plateau, Goa 403206', 15.45780000, 73.83350000
FROM `users` WHERE `email` = 'campus_mess@example.com'
ON DUPLICATE KEY UPDATE `donor_name` = VALUES(`donor_name`), `phone` = VALUES(`phone`), `address` = VALUES(`address`), `latitude` = VALUES(`latitude`), `longitude` = VALUES(`longitude`);

INSERT INTO `donors` (`user_id`, `donor_name`, `phone`, `address`, `latitude`, `longitude`)
SELECT `user_id`, 'Ritz Classic Seafood Restaurant', '+91 98223 34567', '18th June Road, Opposite Municipal Market, Panaji, Goa 403001', 15.49750000, 73.82600000
FROM `users` WHERE `email` = 'ritz_classic@example.com'
ON DUPLICATE KEY UPDATE `donor_name` = VALUES(`donor_name`), `phone` = VALUES(`phone`), `address` = VALUES(`address`), `latitude` = VALUES(`latitude`), `longitude` = VALUES(`longitude`);

INSERT INTO `donors` (`user_id`, `donor_name`, `phone`, `address`, `latitude`, `longitude`)
SELECT `user_id`, 'Bakers Street Patisserie', '+91 98224 45678', 'Chogm Road, Alto-Porvorim, Goa 403521', 15.53200000, 73.83100000
FROM `users` WHERE `email` = 'bakers_street@example.com'
ON DUPLICATE KEY UPDATE `donor_name` = VALUES(`donor_name`), `phone` = VALUES(`phone`), `address` = VALUES(`address`), `latitude` = VALUES(`latitude`), `longitude` = VALUES(`longitude`);

INSERT INTO `donors` (`user_id`, `donor_name`, `phone`, `address`, `latitude`, `longitude`)
SELECT `user_id`, 'Grand Hyatt Banquet Kitchen', '+91 98225 56789', 'P.O. Goa University, Bambolim Bay, Goa 403206', 15.44900000, 73.85400000
FROM `users` WHERE `email` = 'grand_hyatt_kitchen@example.com'
ON DUPLICATE KEY UPDATE `donor_name` = VALUES(`donor_name`), `phone` = VALUES(`phone`), `address` = VALUES(`address`), `latitude` = VALUES(`latitude`), `longitude` = VALUES(`longitude`);

INSERT INTO `donors` (`user_id`, `donor_name`, `phone`, `address`, `latitude`, `longitude`)
SELECT `user_id`, 'Spice Goa Caterers & Kitchen', '+91 98226 67890', 'NH 66 Bypass, Karaswada, Mapusa, Goa 403507', 15.60200000, 73.81800000
FROM `users` WHERE `email` = 'spice_goa@example.com'
ON DUPLICATE KEY UPDATE `donor_name` = VALUES(`donor_name`), `phone` = VALUES(`phone`), `address` = VALUES(`address`), `latitude` = VALUES(`latitude`), `longitude` = VALUES(`longitude`);

-- ----------------------------------------------------------------------------
-- 3. NGO PARTNER PROFILES
-- ----------------------------------------------------------------------------
INSERT INTO `ngo_partners` (`user_id`, `ngo_name`, `phone`, `address`, `latitude`, `longitude`)
SELECT `user_id`, 'Care & Hope Shelter Home', '+91 83222 11001', 'Altinho Hill Road, Near Bishop\'s Palace, Panaji, Goa 403001', 15.49500000, 73.82900000
FROM `users` WHERE `email` = 'care_foundation@example.com'
ON DUPLICATE KEY UPDATE `ngo_name` = VALUES(`ngo_name`), `phone` = VALUES(`phone`), `address` = VALUES(`address`), `latitude` = VALUES(`latitude`), `longitude` = VALUES(`longitude`);

INSERT INTO `ngo_partners` (`user_id`, `ngo_name`, `phone`, `address`, `latitude`, `longitude`)
SELECT `user_id`, 'Feed The Hungry Mission Goa', '+91 83222 22002', 'Station Road, Near Railway Junction, Margao, Goa 403601', 15.27500000, 73.96200000
FROM `users` WHERE `email` = 'feed_all@example.com'
ON DUPLICATE KEY UPDATE `ngo_name` = VALUES(`ngo_name`), `phone` = VALUES(`phone`), `address` = VALUES(`address`), `latitude` = VALUES(`latitude`), `longitude` = VALUES(`longitude`);

INSERT INTO `ngo_partners` (`user_id`, `ngo_name`, `phone`, `address`, `latitude`, `longitude`)
SELECT `user_id`, 'St. Anthony\'s Children\'s Home & Care', '+91 83222 33003', 'Duler Grounds, Mapusa, Goa 403507', 15.59800000, 73.81600000
FROM `users` WHERE `email` = 'st_anthony_home@example.com'
ON DUPLICATE KEY UPDATE `ngo_name` = VALUES(`ngo_name`), `phone` = VALUES(`phone`), `address` = VALUES(`address`), `latitude` = VALUES(`latitude`), `longitude` = VALUES(`longitude`);

INSERT INTO `ngo_partners` (`user_id`, `ngo_name`, `phone`, `address`, `latitude`, `longitude`)
SELECT `user_id`, 'Pragati Community Welfare Center', '+91 83222 44004', 'Swatantra Path, Port Area, Vasco da Gama, Goa 403802', 15.39800000, 73.81400000
FROM `users` WHERE `email` = 'pragati_trust@example.com'
ON DUPLICATE KEY UPDATE `ngo_name` = VALUES(`ngo_name`), `phone` = VALUES(`phone`), `address` = VALUES(`address`), `latitude` = VALUES(`latitude`), `longitude` = VALUES(`longitude`);

INSERT INTO `ngo_partners` (`user_id`, `ngo_name`, `phone`, `address`, `latitude`, `longitude`)
SELECT `user_id`, 'Sneha Mandir Elderly Care & Food Center', '+91 83222 55005', 'Bandora, Near Ramnathi Temple Road, Ponda, Goa 403401', 15.40100000, 74.01300000
FROM `users` WHERE `email` = 'sneha_mandir@example.com'
ON DUPLICATE KEY UPDATE `ngo_name` = VALUES(`ngo_name`), `phone` = VALUES(`phone`), `address` = VALUES(`address`), `latitude` = VALUES(`latitude`), `longitude` = VALUES(`longitude`);

-- ----------------------------------------------------------------------------
-- 4. VOLUNTEER PROFILES
-- ----------------------------------------------------------------------------
INSERT INTO `volunteers` (`user_id`, `volunteer_name`, `phone`, `availability_status`, `created_at`)
SELECT `user_id`, 'Alex Rivera', '+91 97654 32101', 'available', DATE_SUB(@NOW, INTERVAL 30 DAY)
FROM `users` WHERE `email` = 'alex_volunteer@example.com'
ON DUPLICATE KEY UPDATE `volunteer_name` = VALUES(`volunteer_name`), `phone` = VALUES(`phone`), `availability_status` = VALUES(`availability_status`);

INSERT INTO `volunteers` (`user_id`, `volunteer_name`, `phone`, `availability_status`, `created_at`)
SELECT `user_id`, 'Priya Sharma', '+91 97654 32102', 'available', DATE_SUB(@NOW, INTERVAL 30 DAY)
FROM `users` WHERE `email` = 'priya_volunteer@example.com'
ON DUPLICATE KEY UPDATE `volunteer_name` = VALUES(`volunteer_name`), `phone` = VALUES(`phone`), `availability_status` = VALUES(`availability_status`);

INSERT INTO `volunteers` (`user_id`, `volunteer_name`, `phone`, `availability_status`, `created_at`)
SELECT `user_id`, 'Rohan Fernandes', '+91 97654 32103', 'available', DATE_SUB(@NOW, INTERVAL 30 DAY)
FROM `users` WHERE `email` = 'rohan_volunteer@example.com'
ON DUPLICATE KEY UPDATE `volunteer_name` = VALUES(`volunteer_name`), `phone` = VALUES(`phone`), `availability_status` = VALUES(`availability_status`);

INSERT INTO `volunteers` (`user_id`, `volunteer_name`, `phone`, `availability_status`, `created_at`)
SELECT `user_id`, 'Ananya Deshmukh', '+91 97654 32104', 'available', DATE_SUB(@NOW, INTERVAL 30 DAY)
FROM `users` WHERE `email` = 'ananya_volunteer@example.com'
ON DUPLICATE KEY UPDATE `volunteer_name` = VALUES(`volunteer_name`), `phone` = VALUES(`phone`), `availability_status` = VALUES(`availability_status`);

INSERT INTO `volunteers` (`user_id`, `volunteer_name`, `phone`, `availability_status`, `created_at`)
SELECT `user_id`, 'Vikram Naik', '+91 97654 32105', 'available', DATE_SUB(@NOW, INTERVAL 30 DAY)
FROM `users` WHERE `email` = 'vikram_volunteer@example.com'
ON DUPLICATE KEY UPDATE `volunteer_name` = VALUES(`volunteer_name`), `phone` = VALUES(`phone`), `availability_status` = VALUES(`availability_status`);

INSERT INTO `volunteers` (`user_id`, `volunteer_name`, `phone`, `availability_status`, `created_at`)
SELECT `user_id`, 'Neha Kamat', '+91 97654 32106', 'busy', DATE_SUB(@NOW, INTERVAL 30 DAY)
FROM `users` WHERE `email` = 'neha_volunteer@example.com'
ON DUPLICATE KEY UPDATE `volunteer_name` = VALUES(`volunteer_name`), `phone` = VALUES(`phone`), `availability_status` = VALUES(`availability_status`);

INSERT INTO `volunteers` (`user_id`, `volunteer_name`, `phone`, `availability_status`, `created_at`)
SELECT `user_id`, 'Samuel D\'Souza', '+91 97654 32107', 'busy', DATE_SUB(@NOW, INTERVAL 30 DAY)
FROM `users` WHERE `email` = 'samuel_volunteer@example.com'
ON DUPLICATE KEY UPDATE `volunteer_name` = VALUES(`volunteer_name`), `phone` = VALUES(`phone`), `availability_status` = VALUES(`availability_status`);

INSERT INTO `volunteers` (`user_id`, `volunteer_name`, `phone`, `availability_status`, `created_at`)
SELECT `user_id`, 'Fatima Bi Sheikh', '+91 97654 32108', 'offline', DATE_SUB(@NOW, INTERVAL 30 DAY)
FROM `users` WHERE `email` = 'fatima_volunteer@example.com'
ON DUPLICATE KEY UPDATE `volunteer_name` = VALUES(`volunteer_name`), `phone` = VALUES(`phone`), `availability_status` = VALUES(`availability_status`);

INSERT INTO `volunteers` (`user_id`, `volunteer_name`, `phone`, `availability_status`, `created_at`)
SELECT `user_id`, 'Rahul Vernekar', '+91 97654 32109', 'offline', DATE_SUB(@NOW, INTERVAL 30 DAY)
FROM `users` WHERE `email` = 'rahul_volunteer@example.com'
ON DUPLICATE KEY UPDATE `volunteer_name` = VALUES(`volunteer_name`), `phone` = VALUES(`phone`), `availability_status` = VALUES(`availability_status`);

-- ----------------------------------------------------------------------------
-- 5. FOOD BATCHES (20 Comprehensive Batches)
-- ----------------------------------------------------------------------------

-- Batch 1: Available (<2h urgent)
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Vegetable Pulao & Cucumber Raita', 'Cooked Meals', 40.00, 'servings', DATE_SUB(@NOW, INTERVAL 2 HOUR), DATE_ADD(@NOW, INTERVAL 90 MINUTE), 'available', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 2 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'green_bites@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Vegetable Pulao & Cucumber Raita');

-- Batch 2: Available (<2h urgent)
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Goan Fish Curry & Steamed Rice', 'Cooked Meals', 35.00, 'servings', DATE_SUB(@NOW, INTERVAL 105 MINUTE), DATE_ADD(@NOW, INTERVAL 105 MINUTE), 'available', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 105 MINUTE), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'ritz_classic@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Goan Fish Curry & Steamed Rice');

-- Batch 3: Available (<5h today)
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Fresh Goan Poee & Mixed Vegetable Xacuti', 'Cooked Meals', 50.00, 'servings', DATE_SUB(@NOW, INTERVAL 2 HOUR), DATE_ADD(@NOW, INTERVAL 4 HOUR), 'available', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 2 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'bakers_street@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Fresh Goan Poee & Mixed Vegetable Xacuti');

-- Batch 4: Available (<6h today)
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Steamed Basmati Rice & Dal Tadka', 'Cooked Meals', 60.00, 'servings', DATE_SUB(@NOW, INTERVAL 3 HOUR), DATE_ADD(@NOW, INTERVAL 5 HOUR), 'available', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 3 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'campus_mess@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Steamed Basmati Rice & Dal Tadka');

-- Batch 5: Available (Fresh 18h)
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Assorted Artisan Bread & Baguettes', 'Bakery & Bread', 25.00, 'kg', DATE_SUB(@NOW, INTERVAL 4 HOUR), DATE_ADD(@NOW, INTERVAL 18 HOUR), 'available', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 4 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'bakers_street@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Assorted Artisan Bread & Baguettes');

-- Batch 6: Available (Fresh Produce 12h)
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Fresh Cut Seasonal Tropical Fruits', 'Fresh Produce', 20.00, 'kg', DATE_SUB(@NOW, INTERVAL 2 HOUR), DATE_ADD(@NOW, INTERVAL 12 HOUR), 'available', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 2 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'grand_hyatt_kitchen@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Fresh Cut Seasonal Tropical Fruits');

-- Batch 7: Requested
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Fresh Vegetable Club Sandwiches', 'Bakery & Bread', 45.00, 'packs', DATE_SUB(@NOW, INTERVAL 2 HOUR), DATE_ADD(@NOW, INTERVAL 3 HOUR), 'requested', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 2 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'green_bites@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Fresh Vegetable Club Sandwiches');

-- Batch 8: Requested
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Paneer Butter Masala & Phulkas', 'Cooked Meals', 30.00, 'servings', DATE_SUB(@NOW, INTERVAL 90 MINUTE), DATE_ADD(@NOW, INTERVAL 4 HOUR), 'requested', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 90 MINUTE), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'spice_goa@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Paneer Butter Masala & Phulkas');

-- Batch 9: Requested
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'South Indian Tiffin: Idli, Vada & Sambar', 'Cooked Meals', 50.00, 'servings', DATE_SUB(@NOW, INTERVAL 2 HOUR), DATE_ADD(@NOW, INTERVAL 210 MINUTE), 'requested', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 2 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'campus_mess@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'South Indian Tiffin: Idli, Vada & Sambar');

-- Batch 10: Assigned
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Cooked Chicken Cafreal & Butter Pav', 'Cooked Meals', 35.00, 'servings', DATE_SUB(@NOW, INTERVAL 3 HOUR), DATE_ADD(@NOW, INTERVAL 3 HOUR), 'assigned', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 3 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'ritz_classic@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Cooked Chicken Cafreal & Butter Pav');

-- Batch 11: Assigned
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Vegetable Dum Biryani & Mirchi Salan', 'Cooked Meals', 45.00, 'servings', DATE_SUB(@NOW, INTERVAL 150 MINUTE), DATE_ADD(@NOW, INTERVAL 210 MINUTE), 'assigned', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 150 MINUTE), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'spice_goa@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Vegetable Dum Biryani & Mirchi Salan');

-- Batch 12: Assigned
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Banana Walnut Bread & Tea Cakes', 'Bakery & Bread', 18.00, 'kg', DATE_SUB(@NOW, INTERVAL 4 HOUR), DATE_ADD(@NOW, INTERVAL 14 HOUR), 'assigned', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 4 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'bakers_street@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Banana Walnut Bread & Tea Cakes');

-- Batch 13: Collected
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Whole Wheat Chapatis & Aloo Gobi Dry', 'Cooked Meals', 50.00, 'servings', DATE_SUB(@NOW, INTERVAL 3 HOUR), DATE_ADD(@NOW, INTERVAL 3 HOUR), 'collected', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 3 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'campus_mess@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Whole Wheat Chapatis & Aloo Gobi Dry');

-- Batch 14: Collected
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Continental Banquet Buffet Trays', 'Cooked Meals', 40.00, 'servings', DATE_SUB(@NOW, INTERVAL 210 MINUTE), DATE_ADD(@NOW, INTERVAL 150 MINUTE), 'collected', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 210 MINUTE), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'grand_hyatt_kitchen@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Continental Banquet Buffet Trays');

-- Batch 15: Collected
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Farm Fresh Spinach & Green Vegetables', 'Fresh Produce', 15.00, 'kg', DATE_SUB(@NOW, INTERVAL 5 HOUR), DATE_ADD(@NOW, INTERVAL 20 HOUR), 'collected', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 5 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'green_bites@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Farm Fresh Spinach & Green Vegetables');

-- Batch 16: Delivered
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Goan Fish Thali Box Meals', 'Cooked Meals', 30.00, 'servings', DATE_SUB(@NOW, INTERVAL 24 HOUR), DATE_SUB(@NOW, INTERVAL 14 HOUR), 'delivered', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 24 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'ritz_classic@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Goan Fish Thali Box Meals');

-- Batch 17: Delivered
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Assorted Croissants & Sweet Buns', 'Bakery & Bread', 16.00, 'kg', DATE_SUB(@NOW, INTERVAL 26 HOUR), DATE_SUB(@NOW, INTERVAL 10 HOUR), 'delivered', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 26 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'bakers_street@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Assorted Croissants & Sweet Buns');

-- Batch 18: Delivered
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Comfort Moong Dal Khichdi & Pickle', 'Cooked Meals', 55.00, 'servings', DATE_SUB(@NOW, INTERVAL 30 HOUR), DATE_SUB(@NOW, INTERVAL 18 HOUR), 'delivered', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 30 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'spice_goa@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Comfort Moong Dal Khichdi & Pickle');

-- Batch 19: Expired
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Cooked Rajma Masala & Jeera Rice', 'Cooked Meals', 40.00, 'servings', DATE_SUB(@NOW, INTERVAL 28 HOUR), DATE_SUB(@NOW, INTERVAL 6 HOUR), 'expired', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 28 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'campus_mess@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Cooked Rajma Masala & Jeera Rice');

-- Batch 20: Expired
INSERT INTO `food_batches` (`donor_id`, `food_name`, `food_category`, `quantity`, `unit`, `prepared_at`, `expiry_time`, `food_status`, `pickup_address`, `latitude`, `longitude`, `created_at`, `updated_at`)
SELECT d.donor_id, 'Vegetable Samosas & Mint Chutney', 'Cooked Meals', 60.00, 'pieces', DATE_SUB(@NOW, INTERVAL 20 HOUR), DATE_SUB(@NOW, INTERVAL 4 HOUR), 'expired', d.address, d.latitude, d.longitude, DATE_SUB(@NOW, INTERVAL 20 HOUR), @NOW
FROM `donors` d JOIN `users` u ON d.user_id = u.user_id WHERE u.email = 'green_bites@example.com'
AND NOT EXISTS (SELECT 1 FROM `food_batches` fb WHERE fb.donor_id = d.donor_id AND fb.food_name = 'Vegetable Samosas & Mint Chutney');

-- ----------------------------------------------------------------------------
-- 6. PICKUP REQUESTS (15 Requests)
-- ----------------------------------------------------------------------------

-- Helper macro: Insert pickup request if not exists for batch and NGO
-- PR-01: Requested
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, NULL, 'requested', DATE_SUB(@NOW, INTERVAL 45 MINUTE), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n
JOIN `users` u ON n.user_id = u.user_id
WHERE fb.food_name = 'Fresh Vegetable Club Sandwiches' AND u.email = 'care_foundation@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-02: Requested
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, NULL, 'requested', DATE_SUB(@NOW, INTERVAL 30 MINUTE), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n
JOIN `users` u ON n.user_id = u.user_id
WHERE fb.food_name = 'Paneer Butter Masala & Phulkas' AND u.email = 'feed_all@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-03: Requested
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, NULL, 'requested', DATE_SUB(@NOW, INTERVAL 20 MINUTE), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n
JOIN `users` u ON n.user_id = u.user_id
WHERE fb.food_name = 'South Indian Tiffin: Idli, Vada & Sambar' AND u.email = 'st_anthony_home@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-04: Assigned
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `assigned_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, v.volunteer_id, 'assigned', DATE_SUB(@NOW, INTERVAL 2 HOUR), DATE_SUB(@NOW, INTERVAL 90 MINUTE), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n JOIN `users` un ON n.user_id = un.user_id
CROSS JOIN `volunteers` v JOIN `users` uv ON v.user_id = uv.user_id
WHERE fb.food_name = 'Cooked Chicken Cafreal & Butter Pav' AND un.email = 'care_foundation@example.com' AND uv.email = 'alex_volunteer@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-05: Assigned
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `assigned_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, v.volunteer_id, 'assigned', DATE_SUB(@NOW, INTERVAL 105 MINUTE), DATE_SUB(@NOW, INTERVAL 75 MINUTE), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n JOIN `users` un ON n.user_id = un.user_id
CROSS JOIN `volunteers` v JOIN `users` uv ON v.user_id = uv.user_id
WHERE fb.food_name = 'Vegetable Dum Biryani & Mirchi Salan' AND un.email = 'st_anthony_home@example.com' AND uv.email = 'priya_volunteer@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-06: Assigned
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `assigned_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, v.volunteer_id, 'assigned', DATE_SUB(@NOW, INTERVAL 135 MINUTE), DATE_SUB(@NOW, INTERVAL 100 MINUTE), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n JOIN `users` un ON n.user_id = un.user_id
CROSS JOIN `volunteers` v JOIN `users` uv ON v.user_id = uv.user_id
WHERE fb.food_name = 'Banana Walnut Bread & Tea Cakes' AND un.email = 'sneha_mandir@example.com' AND uv.email = 'rohan_volunteer@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-07: Collected
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `assigned_at`, `collected_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, v.volunteer_id, 'collected', DATE_SUB(@NOW, INTERVAL 150 MINUTE), DATE_SUB(@NOW, INTERVAL 2 HOUR), DATE_SUB(@NOW, INTERVAL 1 HOUR), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n JOIN `users` un ON n.user_id = un.user_id
CROSS JOIN `volunteers` v JOIN `users` uv ON v.user_id = uv.user_id
WHERE fb.food_name = 'Whole Wheat Chapatis & Aloo Gobi Dry' AND un.email = 'feed_all@example.com' AND uv.email = 'alex_volunteer@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-08: Collected
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `assigned_at`, `collected_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, v.volunteer_id, 'collected', DATE_SUB(@NOW, INTERVAL 3 HOUR), DATE_SUB(@NOW, INTERVAL 135 MINUTE), DATE_SUB(@NOW, INTERVAL 75 MINUTE), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n JOIN `users` un ON n.user_id = un.user_id
CROSS JOIN `volunteers` v JOIN `users` uv ON v.user_id = uv.user_id
WHERE fb.food_name = 'Continental Banquet Buffet Trays' AND un.email = 'pragati_trust@example.com' AND uv.email = 'ananya_volunteer@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-09: Collected
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `assigned_at`, `collected_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, v.volunteer_id, 'collected', DATE_SUB(@NOW, INTERVAL 4 HOUR), DATE_SUB(@NOW, INTERVAL 3 HOUR), DATE_SUB(@NOW, INTERVAL 105 MINUTE), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n JOIN `users` un ON n.user_id = un.user_id
CROSS JOIN `volunteers` v JOIN `users` uv ON v.user_id = uv.user_id
WHERE fb.food_name = 'Farm Fresh Spinach & Green Vegetables' AND un.email = 'sneha_mandir@example.com' AND uv.email = 'vikram_volunteer@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-10: Delivered
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `assigned_at`, `collected_at`, `completed_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, v.volunteer_id, 'delivered', DATE_SUB(@NOW, INTERVAL 23 HOUR), DATE_SUB(@NOW, INTERVAL 22 HOUR), DATE_SUB(@NOW, INTERVAL 21 HOUR), DATE_SUB(@NOW, INTERVAL 20 HOUR), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n JOIN `users` un ON n.user_id = un.user_id
CROSS JOIN `volunteers` v JOIN `users` uv ON v.user_id = uv.user_id
WHERE fb.food_name = 'Goan Fish Thali Box Meals' AND un.email = 'care_foundation@example.com' AND uv.email = 'alex_volunteer@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-11: Delivered
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `assigned_at`, `collected_at`, `completed_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, v.volunteer_id, 'delivered', DATE_SUB(@NOW, INTERVAL 25 HOUR), DATE_SUB(@NOW, INTERVAL 24 HOUR), DATE_SUB(@NOW, INTERVAL 23 HOUR), DATE_SUB(@NOW, INTERVAL 22 HOUR), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n JOIN `users` un ON n.user_id = un.user_id
CROSS JOIN `volunteers` v JOIN `users` uv ON v.user_id = uv.user_id
WHERE fb.food_name = 'Assorted Croissants & Sweet Buns' AND un.email = 'st_anthony_home@example.com' AND uv.email = 'priya_volunteer@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-12: Delivered
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `assigned_at`, `collected_at`, `completed_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, v.volunteer_id, 'delivered', DATE_SUB(@NOW, INTERVAL 28 HOUR), DATE_SUB(@NOW, INTERVAL 27 HOUR), DATE_SUB(@NOW, INTERVAL 26 HOUR), DATE_SUB(@NOW, INTERVAL 25 HOUR), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n JOIN `users` un ON n.user_id = un.user_id
CROSS JOIN `volunteers` v JOIN `users` uv ON v.user_id = uv.user_id
WHERE fb.food_name = 'Comfort Moong Dal Khichdi & Pickle' AND un.email = 'pragati_trust@example.com' AND uv.email = 'neha_volunteer@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-13: Cancelled (Expired)
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, NULL, 'cancelled', DATE_SUB(@NOW, INTERVAL 12 HOUR), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n
JOIN `users` u ON n.user_id = u.user_id
WHERE fb.food_name = 'Cooked Rajma Masala & Jeera Rice' AND u.email = 'feed_all@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-14: Cancelled (Expired)
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, NULL, 'cancelled', DATE_SUB(@NOW, INTERVAL 8 HOUR), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n
JOIN `users` u ON n.user_id = u.user_id
WHERE fb.food_name = 'Vegetable Samosas & Mint Chutney' AND u.email = 'sneha_mandir@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- PR-15: Cancelled (Surplus returned to pool)
INSERT INTO `pickup_requests` (`batch_id`, `ngo_id`, `volunteer_id`, `request_status`, `requested_at`, `updated_at`)
SELECT fb.batch_id, n.ngo_id, NULL, 'cancelled', DATE_SUB(@NOW, INTERVAL 2 HOUR), @NOW
FROM `food_batches` fb
CROSS JOIN `ngo_partners` n
JOIN `users` u ON n.user_id = u.user_id
WHERE fb.food_name = 'Vegetable Pulao & Cucumber Raita' AND u.email = 'pragati_trust@example.com'
AND NOT EXISTS (SELECT 1 FROM `pickup_requests` pr WHERE pr.batch_id = fb.batch_id AND pr.ngo_id = n.ngo_id);

-- ----------------------------------------------------------------------------
-- 7. NOTIFICATIONS (Sample of 25 Cross-Role Alerts)
-- ----------------------------------------------------------------------------
INSERT INTO `notifications` (`user_id`, `title`, `message`, `is_read`, `created_at`)
SELECT u.user_id, 'Donation Listed Successfully', 'Your donation Vegetable Pulao & Cucumber Raita is now available for local NGOs.', 1, DATE_SUB(@NOW, INTERVAL 2 HOUR)
FROM `users` u WHERE u.email = 'green_bites@example.com'
AND NOT EXISTS (SELECT 1 FROM `notifications` n WHERE n.user_id = u.user_id AND n.title = 'Donation Listed Successfully');

INSERT INTO `notifications` (`user_id`, `title`, `message`, `is_read`, `created_at`)
SELECT u.user_id, 'Pickup Request Received', 'Care & Hope Shelter Home has requested your donation Fresh Vegetable Club Sandwiches.', 0, DATE_SUB(@NOW, INTERVAL 45 MINUTE)
FROM `users` u WHERE u.email = 'green_bites@example.com'
AND NOT EXISTS (SELECT 1 FROM `notifications` n WHERE n.user_id = u.user_id AND n.title = 'Pickup Request Received');

INSERT INTO `notifications` (`user_id`, `title`, `message`, `is_read`, `created_at`)
SELECT u.user_id, 'Delivery Completed!', 'Thank you! 30 servings of Goan Fish Thali Box Meals delivered to Care & Hope Shelter.', 1, DATE_SUB(@NOW, INTERVAL 20 HOUR)
FROM `users` u WHERE u.email = 'ritz_classic@example.com'
AND NOT EXISTS (SELECT 1 FROM `notifications` n WHERE n.user_id = u.user_id AND n.title = 'Delivery Completed!');

INSERT INTO `notifications` (`user_id`, `title`, `message`, `is_read`, `created_at`)
SELECT u.user_id, 'Urgent Rescue Available in Panaji', 'Vegetable Pulao & Cucumber Raita is expiring in under 2 hours! Claim pickup now.', 0, DATE_SUB(@NOW, INTERVAL 1 HOUR)
FROM `users` u WHERE u.email = 'alex_volunteer@example.com'
AND NOT EXISTS (SELECT 1 FROM `notifications` n WHERE n.user_id = u.user_id AND n.title = 'Urgent Rescue Available in Panaji');

-- Seeding complete message
SELECT 'Deterministic Synthetic Data Seeded Successfully' AS `Result`;

