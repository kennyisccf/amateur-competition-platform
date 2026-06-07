SET NAMES utf8mb4;
USE `lesai_db`;

ALTER DATABASE `lesai_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `user` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `competition` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `registration` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `point_history` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `audit_record` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'registration'
    AND column_name = 'register_type'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `registration` ADD COLUMN `register_type` varchar(20) DEFAULT ''single'' AFTER `review_status`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'registration'
    AND column_name = 'team_name'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `registration` ADD COLUMN `team_name` varchar(100) DEFAULT '''' AFTER `register_type`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'registration'
    AND column_name = 'team_members'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `registration` ADD COLUMN `team_members` text DEFAULT NULL AFTER `team_name`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'registration'
    AND column_name = 'contact_name'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `registration` ADD COLUMN `contact_name` varchar(50) DEFAULT '''' AFTER `team_members`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'registration'
    AND column_name = 'phone'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `registration` ADD COLUMN `phone` varchar(50) DEFAULT '''' AFTER `contact_name`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'registration'
    AND column_name = 'show_in_profile'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `registration` ADD COLUMN `show_in_profile` tinyint(1) DEFAULT 1 AFTER `invite_code`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'competition'
    AND column_name = 'competition_no'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `competition` ADD COLUMN `competition_no` varchar(20) DEFAULT NULL AFTER `id`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'competition'
    AND column_name = 'competition_format'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `competition` ADD COLUMN `competition_format` varchar(30) DEFAULT ''SINGLE_ELIMINATION'' AFTER `reward`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'competition'
    AND column_name = 'group_count'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `competition` ADD COLUMN `group_count` int DEFAULT 0 AFTER `competition_format`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'competition'
    AND column_name = 'bracket_state'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `competition` ADD COLUMN `bracket_state` text DEFAULT NULL AFTER `reject_reason`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

UPDATE `competition`
SET `competition_no` = CONCAT('NO.', LPAD(`id`, 8, '0'))
WHERE `competition_no` IS NULL OR `competition_no` = '';

UPDATE `competition`
SET `reward_points` = 0
WHERE `type` = 'PRIVATE';

UPDATE `registration`
SET `team_members` = (
  SELECT `username`
  FROM `user`
  WHERE `user`.`id` = `registration`.`player_id`
)
WHERE `team_members` IS NULL OR `team_members` = '';

UPDATE `user`
SET
  `role` = 'ADMIN',
  `nickname` = '全功能测试账号',
  `email` = 'test_admin@lesai.com',
  `points` = 9999,
  `is_deleted` = 0
WHERE `username` = 'test_admin';

INSERT INTO `user` (`username`, `password`, `role`, `nickname`, `email`, `points`, `is_deleted`)
SELECT 'test_admin', 'e10adc3949ba59abbe56e057f20f883e', 'ADMIN', '全功能测试账号', 'test_admin@lesai.com', 9999, 0
WHERE NOT EXISTS (
  SELECT 1 FROM `user` WHERE `username` = 'test_admin'
);

UPDATE `registration`
SET `status` = CASE
  WHEN `review_status` = 0 THEN 'pending'
  WHEN `review_status` = 1 THEN 'ongoing'
  WHEN `review_status` = 2 THEN 'rejected'
  ELSE `status`
END;

UPDATE `competition` c
SET `current_participants` = (
  SELECT COUNT(*)
  FROM `registration` r
  WHERE r.`competition_id` = c.`id`
    AND r.`review_status` = 1
);

SET @idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'point_history'
    AND index_name = 'uk_user_time'
);
SET @drop_idx_sql := IF(@idx_exists > 0, 'ALTER TABLE `point_history` DROP INDEX `uk_user_time`', 'SELECT 1');
PREPARE drop_idx_stmt FROM @drop_idx_sql;
EXECUTE drop_idx_stmt;
DEALLOCATE PREPARE drop_idx_stmt;
