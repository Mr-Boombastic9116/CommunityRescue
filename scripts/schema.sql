-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: community_food_rescue
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `delivery_logs`
--

DROP TABLE IF EXISTS `delivery_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `delivery_logs` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `request_id` int(11) NOT NULL,
  `performed_by_user_id` int(11) DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `notes` text DEFAULT NULL,
  `logged_at` datetime NOT NULL,
  PRIMARY KEY (`log_id`),
  KEY `ix_delivery_logs_request_id` (`request_id`),
  KEY `ix_delivery_logs_performed_by_user_id` (`performed_by_user_id`),
  KEY `idx_log_time` (`logged_at`),
  KEY `ix_delivery_logs_log_id` (`log_id`),
  KEY `idx_log_action` (`action`),
  CONSTRAINT `delivery_logs_ibfk_1` FOREIGN KEY (`request_id`) REFERENCES `pickup_requests` (`request_id`) ON DELETE CASCADE,
  CONSTRAINT `delivery_logs_ibfk_2` FOREIGN KEY (`performed_by_user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `donors`
--

DROP TABLE IF EXISTS `donors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `donors` (
  `donor_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `donor_name` varchar(255) NOT NULL,
  `phone` varchar(50) NOT NULL,
  `address` text NOT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  PRIMARY KEY (`donor_id`),
  UNIQUE KEY `ix_donors_user_id` (`user_id`),
  KEY `ix_donors_donor_id` (`donor_id`),
  CONSTRAINT `donors_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `food_batches`
--

DROP TABLE IF EXISTS `food_batches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `food_batches` (
  `batch_id` int(11) NOT NULL AUTO_INCREMENT,
  `donor_id` int(11) NOT NULL,
  `food_name` varchar(255) NOT NULL,
  `food_category` varchar(100) NOT NULL,
  `quantity` decimal(10,2) NOT NULL,
  `unit` varchar(50) NOT NULL,
  `prepared_at` datetime NOT NULL,
  `expiry_time` datetime NOT NULL,
  `food_status` varchar(50) NOT NULL,
  `pickup_address` text NOT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`batch_id`),
  KEY `ix_food_batches_donor_id` (`donor_id`),
  KEY `idx_food_status` (`food_status`),
  KEY `ix_food_batches_batch_id` (`batch_id`),
  KEY `idx_food_category` (`food_category`),
  KEY `idx_food_expiry` (`expiry_time`),
  CONSTRAINT `food_batches_ibfk_1` FOREIGN KEY (`donor_id`) REFERENCES `donors` (`donor_id`) ON DELETE CASCADE,
  CONSTRAINT `chk_food_quantity_positive` CHECK (`quantity` > 0),
  CONSTRAINT `chk_food_expiry_after_prep` CHECK (`expiry_time` > `prepared_at`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ngo_partners`
--

DROP TABLE IF EXISTS `ngo_partners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ngo_partners` (
  `ngo_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `ngo_name` varchar(255) NOT NULL,
  `phone` varchar(50) NOT NULL,
  `address` text NOT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  PRIMARY KEY (`ngo_id`),
  UNIQUE KEY `ix_ngo_partners_user_id` (`user_id`),
  KEY `ix_ngo_partners_ngo_id` (`ngo_id`),
  CONSTRAINT `ngo_partners_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notifications` (
  `notification_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`notification_id`),
  KEY `idx_notif_user_read` (`user_id`,`is_read`),
  KEY `ix_notifications_user_id` (`user_id`),
  KEY `ix_notifications_notification_id` (`notification_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pickup_requests`
--

DROP TABLE IF EXISTS `pickup_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pickup_requests` (
  `request_id` int(11) NOT NULL AUTO_INCREMENT,
  `batch_id` int(11) NOT NULL,
  `ngo_id` int(11) NOT NULL,
  `volunteer_id` int(11) DEFAULT NULL,
  `request_status` varchar(50) NOT NULL,
  `requested_at` datetime NOT NULL,
  `assigned_at` datetime DEFAULT NULL,
  `collected_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`request_id`),
  KEY `ix_pickup_requests_request_id` (`request_id`),
  KEY `idx_request_status` (`request_status`),
  KEY `ix_pickup_requests_ngo_id` (`ngo_id`),
  KEY `ix_pickup_requests_batch_id` (`batch_id`),
  KEY `ix_pickup_requests_volunteer_id` (`volunteer_id`),
  KEY `idx_req_volunteer` (`volunteer_id`),
  KEY `idx_req_batch` (`batch_id`),
  KEY `idx_req_ngo` (`ngo_id`),
  CONSTRAINT `pickup_requests_ibfk_1` FOREIGN KEY (`batch_id`) REFERENCES `food_batches` (`batch_id`) ON DELETE CASCADE,
  CONSTRAINT `pickup_requests_ibfk_2` FOREIGN KEY (`ngo_id`) REFERENCES `ngo_partners` (`ngo_id`) ON DELETE CASCADE,
  CONSTRAINT `pickup_requests_ibfk_3` FOREIGN KEY (`volunteer_id`) REFERENCES `volunteers` (`volunteer_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `v_active_rescue_pipeline`
--

DROP TABLE IF EXISTS `v_active_rescue_pipeline`;
/*!50001 DROP VIEW IF EXISTS `v_active_rescue_pipeline`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `v_active_rescue_pipeline` AS SELECT
 1 AS `request_id`,
  1 AS `request_status`,
  1 AS `requested_at`,
  1 AS `assigned_at`,
  1 AS `collected_at`,
  1 AS `batch_id`,
  1 AS `food_name`,
  1 AS `food_category`,
  1 AS `quantity`,
  1 AS `unit`,
  1 AS `expiry_time`,
  1 AS `donor_name`,
  1 AS `donor_phone`,
  1 AS `pickup_address`,
  1 AS `ngo_name`,
  1 AS `ngo_phone`,
  1 AS `ngo_address`,
  1 AS `volunteer_name`,
  1 AS `volunteer_phone` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `volunteers`
--

DROP TABLE IF EXISTS `volunteers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `volunteers` (
  `volunteer_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `volunteer_name` varchar(255) NOT NULL,
  `phone` varchar(50) NOT NULL,
  `availability_status` varchar(50) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`volunteer_id`),
  UNIQUE KEY `ix_volunteers_user_id` (`user_id`),
  KEY `ix_volunteers_volunteer_id` (`volunteer_id`),
  CONSTRAINT `volunteers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `v_active_rescue_pipeline`
--

/*!50001 DROP VIEW IF EXISTS `v_active_rescue_pipeline`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = cp850 */;
/*!50001 SET character_set_results     = cp850 */;
/*!50001 SET collation_connection      = cp850_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_active_rescue_pipeline` AS select `pr`.`request_id` AS `request_id`,`pr`.`request_status` AS `request_status`,`pr`.`requested_at` AS `requested_at`,`pr`.`assigned_at` AS `assigned_at`,`pr`.`collected_at` AS `collected_at`,`fb`.`batch_id` AS `batch_id`,`fb`.`food_name` AS `food_name`,`fb`.`food_category` AS `food_category`,`fb`.`quantity` AS `quantity`,`fb`.`unit` AS `unit`,`fb`.`expiry_time` AS `expiry_time`,`d`.`donor_name` AS `donor_name`,`d`.`phone` AS `donor_phone`,`fb`.`pickup_address` AS `pickup_address`,`n`.`ngo_name` AS `ngo_name`,`n`.`phone` AS `ngo_phone`,`n`.`address` AS `ngo_address`,`v`.`volunteer_name` AS `volunteer_name`,`v`.`phone` AS `volunteer_phone` from ((((`pickup_requests` `pr` join `food_batches` `fb` on(`pr`.`batch_id` = `fb`.`batch_id`)) join `donors` `d` on(`fb`.`donor_id` = `d`.`donor_id`)) join `ngo_partners` `n` on(`pr`.`ngo_id` = `n`.`ngo_id`)) left join `volunteers` `v` on(`pr`.`volunteer_id` = `v`.`volunteer_id`)) where `pr`.`request_status` not in ('delivered','cancelled','rejected') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-30 14:14:20
