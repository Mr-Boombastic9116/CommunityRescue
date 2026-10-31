-- ============================================================================
-- COMMUNITY FOOD RESCUE NETWORK - DBMS VIVA DEMONSTRATION SCRIPT
-- Database: community_food_rescue
-- Engine: MySQL 8.x / MariaDB 10.4+ (XAMPP Compatible)
-- ============================================================================

USE `community_food_rescue`;

DELIMITER $$

-- ----------------------------------------------------------------------------
-- 1. STORED PROCEDURE: Automatically Expire Overdue Donations
-- Demonstrates: Transactions, conditional logic, cursors/updates, date math
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_expire_overdue_donations`$$
CREATE PROCEDURE `sp_expire_overdue_donations`(OUT expired_count INT)
BEGIN
    DECLARE current_ts DATETIME;
    SET current_ts = UTC_TIMESTAMP();
    SET expired_count = 0;

    START TRANSACTION;

    -- Update eligible available and requested batches that passed expiry
    UPDATE food_batches
    SET food_status = 'expired',
        updated_at = current_ts
    WHERE expiry_time <= current_ts
      AND food_status IN ('available', 'requested');

    SET expired_count = ROW_COUNT();

    -- Automatically cancel pending requests on expired batches
    UPDATE pickup_requests pr
    JOIN food_batches fb ON pr.batch_id = fb.batch_id
    SET pr.request_status = 'cancelled',
        pr.updated_at = current_ts
    WHERE fb.food_status = 'expired'
      AND pr.request_status = 'requested';

    COMMIT;
END$$

-- ----------------------------------------------------------------------------
-- 2. STORED PROCEDURE: Donor Impact Analytics
-- Demonstrates: JOIN queries, aggregate functions (COUNT, SUM, AVG)
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_get_donor_impact_summary`$$
CREATE PROCEDURE `sp_get_donor_impact_summary`(IN p_donor_id INT)
BEGIN
    SELECT 
        d.donor_name,
        d.phone,
        COUNT(fb.batch_id) AS total_batches_listed,
        SUM(CASE WHEN fb.food_status = 'delivered' THEN 1 ELSE 0 END) AS total_batches_delivered,
        SUM(CASE WHEN fb.food_status = 'expired' THEN 1 ELSE 0 END) AS total_batches_expired,
        COALESCE(SUM(CASE WHEN fb.food_status = 'delivered' THEN fb.quantity ELSE 0 END), 0) AS total_food_rescued_units
    FROM donors d
    LEFT JOIN food_batches fb ON d.donor_id = fb.donor_id
    WHERE d.donor_id = p_donor_id
    GROUP BY d.donor_id, d.donor_name, d.phone;
END$$

DELIMITER ;

-- ----------------------------------------------------------------------------
-- 3. SQL VIEW: Live Active Rescue Pipeline
-- Demonstrates: Multi-table relational joins, data abstraction for dashboards
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `v_active_rescue_pipeline` AS
SELECT 
    pr.request_id,
    pr.request_status,
    pr.requested_at,
    pr.assigned_at,
    pr.collected_at,
    fb.batch_id,
    fb.food_name,
    fb.food_category,
    fb.quantity,
    fb.unit,
    fb.expiry_time,
    d.donor_name,
    d.phone AS donor_phone,
    fb.pickup_address,
    n.ngo_name,
    n.phone AS ngo_phone,
    n.address AS ngo_address,
    v.volunteer_name,
    v.phone AS volunteer_phone
FROM pickup_requests pr
JOIN food_batches fb ON pr.batch_id = fb.batch_id
JOIN donors d ON fb.donor_id = d.donor_id
JOIN ngo_partners n ON pr.ngo_id = n.ngo_id
LEFT JOIN volunteers v ON pr.volunteer_id = v.volunteer_id
WHERE pr.request_status NOT IN ('delivered', 'cancelled', 'rejected');

