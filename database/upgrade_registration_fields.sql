SET NAMES utf8mb4;
USE `lesai_db`;

ALTER DATABASE `lesai_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `user` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `competition` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `registration` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `point_history` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `audit_record` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `friend_relation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `requester_id` bigint NOT NULL,
  `addressee_id` bigint NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_friend_pair` (`requester_id`,`addressee_id`),
  KEY `idx_friend_requester` (`requester_id`),
  KEY `idx_friend_addressee` (`addressee_id`),
  KEY `idx_friend_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE `friend_relation` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `friend_message` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sender_id` bigint NOT NULL,
  `receiver_id` bigint NOT NULL,
  `content` varchar(500) NOT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_friend_message_pair` (`sender_id`,`receiver_id`,`created_at`),
  KEY `idx_friend_message_unread` (`receiver_id`,`is_read`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE `friend_message` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'user'
    AND column_name = 'user_code'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `user` ADD COLUMN `user_code` varchar(20) DEFAULT NULL AFTER `username`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'user'
    AND column_name = 'allow_friend_requests'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `user` ADD COLUMN `allow_friend_requests` tinyint(1) DEFAULT 1 AFTER `is_deleted`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'competition'
    AND column_name = 'thumbnail_url'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE `competition` ADD COLUMN `thumbnail_url` varchar(500) DEFAULT '''' AFTER `bracket_state`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

UPDATE `competition`
SET `thumbnail_url` = CASE
  WHEN `category` = '篮球' THEN '/default-thumbnails/basketball.png'
  WHEN `category` = '足球' THEN '/default-thumbnails/football.png'
  WHEN `category` = '羽毛球' THEN '/default-thumbnails/badminton.png'
  WHEN `category` = '网球' THEN '/default-thumbnails/tennis.png'
  WHEN `category` = '电竞' THEN '/default-thumbnails/esports.png'
  WHEN `category` = '棋牌桌游' THEN '/default-thumbnails/boardgame.png'
  ELSE '/default-thumbnails/badminton.png'
END
WHERE `thumbnail_url` IS NULL OR `thumbnail_url` = '';

UPDATE `competition`
SET `thumbnail_url` = CASE `competition_no`
  WHEN 'NO.00000001' THEN '/default-thumbnails/badminton.png'
  WHEN 'NO.00000002' THEN '/default-thumbnails/basketball.png'
  WHEN 'NO.00000003' THEN '/default-thumbnails/esports.png'
  WHEN 'NO.00000004' THEN '/default-thumbnails/boardgame.png'
  WHEN 'NO.00000005' THEN '/default-thumbnails/badminton.png'
  WHEN 'NO.00000006' THEN '/default-thumbnails/football.png'
  ELSE `thumbnail_url`
END
WHERE `competition_no` IN ('NO.00000001', 'NO.00000002', 'NO.00000003', 'NO.00000004', 'NO.00000005', 'NO.00000006');

UPDATE `competition`
SET `thumbnail_url` = REPLACE(`thumbnail_url`, '.svg', '.png')
WHERE `thumbnail_url` IN (
  '/default-thumbnails/badminton.svg',
  '/default-thumbnails/basketball.svg',
  '/default-thumbnails/football.svg',
  '/default-thumbnails/tennis.svg',
  '/default-thumbnails/esports.svg',
  '/default-thumbnails/boardgame.svg'
);

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
  `user_code` = COALESCE(NULLIF(`user_code`, ''), CONCAT('U', LPAD(`id`, 6, '0'))),
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

UPDATE `user`
SET `user_code` = CONCAT('U', LPAD(`id`, 6, '0'))
WHERE `user_code` IS NULL OR `user_code` = '';

UPDATE `competition`
SET
  `title` = '校内羽毛球挑战赛',
  `location` = '校内体育馆羽毛球场',
  `description` = '用于验证大规模单淘汰赛程、种子选手、报名审核和赛程维护流程的私人赛事。',
  `reward` = '私人赛事不设置积分，优胜者获得荣誉证书。',
  `thumbnail_url` = '/default-thumbnails/badminton.png'
WHERE `competition_no` = 'NO.00000026'
  AND (`title` = '1' OR `location` = '1');

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
