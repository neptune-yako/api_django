/*
 Navicat Premium Data Transfer

 Source Server         : 10.0.31.32
 Source Server Type    : MySQL
 Source Server Version : 80402 (8.4.2)
 Source Host           : 10.0.31.32:3306
 Source Schema         : igtest

 Target Server Type    : MySQL
 Target Server Version : 80402 (8.4.2)
 File Encoding         : 65001

 Date: 25/12/2025 21:33:31
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for categories
-- ----------------------------
DROP TABLE IF EXISTS `categories`;
CREATE TABLE `categories`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `execution_id` int NOT NULL,
  `category_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `count` int NULL DEFAULT 0,
  `severity` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'major',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_execution_id`(`execution_id` ASC) USING BTREE,
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`execution_id`) REFERENCES `test_execution` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for feature_scenarios
-- ----------------------------
DROP TABLE IF EXISTS `feature_scenarios`;
CREATE TABLE `feature_scenarios`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `execution_id` int NOT NULL,
  `scenario_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `count` int NULL DEFAULT 0,
  `passed` int NULL DEFAULT 0,
  `failed` int NULL DEFAULT 0,
  `total` int NULL DEFAULT 0,
  `pass_rate` decimal(5, 2) NULL DEFAULT 0.00,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_execution_id`(`execution_id` ASC) USING BTREE,
  CONSTRAINT `feature_scenarios_ibfk_1` FOREIGN KEY (`execution_id`) REFERENCES `test_execution` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for test_execution
-- ----------------------------
DROP TABLE IF EXISTS `test_execution`;
CREATE TABLE `test_execution`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `timestamp` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `report_title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `total_cases` int NULL DEFAULT 0,
  `passed_cases` int NULL DEFAULT 0,
  `failed_cases` int NULL DEFAULT 0,
  `skipped_cases` int NULL DEFAULT 0,
  `broken_cases` int NULL DEFAULT 0,
  `unknown_cases` int NULL DEFAULT 0,
  `pass_rate` decimal(5, 2) NULL DEFAULT 0.00,
  `min_duration` int NULL DEFAULT 0,
  `max_duration` int NULL DEFAULT 0,
  `sum_duration` int NULL DEFAULT 0,
  `execution_time` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `start_time` datetime NULL DEFAULT NULL,
  `end_time` datetime NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'success',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `timestamp`(`timestamp` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for test_suite_details
-- ----------------------------
DROP TABLE IF EXISTS `test_suite_details`;
CREATE TABLE `test_suite_details`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `execution_id` int NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `duration_in_ms` decimal(12, 3) NULL DEFAULT 0.000,
  `name` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `parent_suite` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_time` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `status` enum('passed','failed','skipped','broken','unknown') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'unknown',
  `stop_time` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `sub_suite` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `suite` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `test_class` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `test_method` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_execution_id`(`execution_id` ASC) USING BTREE,
  INDEX `idx_parent_suite`(`parent_suite` ASC) USING BTREE,
  CONSTRAINT `test_suite_details_ibfk_1` FOREIGN KEY (`execution_id`) REFERENCES `test_execution` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 889 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for test_suites
-- ----------------------------
DROP TABLE IF EXISTS `test_suites`;
CREATE TABLE `test_suites`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `execution_id` int NOT NULL,
  `suite_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_cases` int NULL DEFAULT 0,
  `passed_cases` int NULL DEFAULT 0,
  `failed_cases` int NULL DEFAULT 0,
  `skipped_cases` int NULL DEFAULT 0,
  `broken_cases` int NULL DEFAULT 0,
  `unknown_cases` int NULL DEFAULT 0,
  `pass_rate` decimal(5, 2) NULL DEFAULT 0.00,
  `min_duration` int NULL DEFAULT 0,
  `max_duration` int NULL DEFAULT 0,
  `sum_duration` int NULL DEFAULT 0,
  `duration_seconds` decimal(10, 3) NULL DEFAULT 0.000,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_execution_id`(`execution_id` ASC) USING BTREE,
  CONSTRAINT `test_suites_ibfk_1` FOREIGN KEY (`execution_id`) REFERENCES `test_execution` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
