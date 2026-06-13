/*
 Navicat MySQL Data Transfer
 Target Server Type    : MySQL
 Target Server Version : 80046
 Project               : 乐赛一站式服务平台 (LeSai Platform) V2.5
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS `lesai_db` CHARACTER SET utf8mb4;
USE `lesai_db`;

-- ----------------------------
-- 1. 用户表 (对齐 class User)
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL UNIQUE,
  `user_code` varchar(20) DEFAULT NULL,
  `password` varchar(255) NOT NULL COMMENT 'MD5(123456) = e10adc3949ba59abbe56e057f20f883e',
  `role` varchar(20) NOT NULL COMMENT 'ADMIN/ORGANIZER/PLAYER',
  `nickname` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `points` int DEFAULT 0,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_deleted` tinyint(1) DEFAULT 0,
  `allow_friend_requests` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 2. 赛事表 (对齐 class Competition)
-- ----------------------------
DROP TABLE IF EXISTS `competition`;
CREATE TABLE `competition` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `competition_no` varchar(20) DEFAULT NULL,
  `title` varchar(100) NOT NULL,
  `category` varchar(50) NOT NULL,
  `location` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `type` varchar(10) NOT NULL COMMENT 'PUBLIC/PRIVATE',
  `organizer_id` bigint NOT NULL,
  `status` int DEFAULT 0 COMMENT '0待审核 1报名中 2进行中 3已结束 4驳回',
  `max_participants` int DEFAULT 100,
  `current_participants` int DEFAULT 0,
  `reward_points` int DEFAULT 100,
  `reward` text DEFAULT NULL,
  `competition_format` varchar(30) DEFAULT 'SINGLE_ELIMINATION',
  `group_count` int DEFAULT 0,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `invite_code` varchar(50) DEFAULT NULL,
  `reject_reason` varchar(255) DEFAULT NULL,
  `bracket_state` text DEFAULT NULL,
  `thumbnail_url` varchar(500) DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_competition_no` (`competition_no`),
  KEY `fk_organizer_idx` (`organizer_id`),
  CONSTRAINT `fk_organizer` FOREIGN KEY (`organizer_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 3. 报名表 (对齐 class Registration)
-- ----------------------------
DROP TABLE IF EXISTS `registration`;
CREATE TABLE `registration` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `player_id` bigint NOT NULL,
  `competition_id` bigint NOT NULL,
  `status` varchar(20) DEFAULT '' COMMENT 'pending ongoing finished rejected',
  `review_status` int DEFAULT 0 COMMENT '0未审核 1通过 2未通过',
  `register_type` varchar(20) DEFAULT 'single',
  `team_name` varchar(100) DEFAULT '',
  `team_members` text DEFAULT NULL,
  `contact_name` varchar(50) DEFAULT '',
  `phone` varchar(50) DEFAULT '',
  `final_score` varchar(50) NOT NULL DEFAULT '',
  `final_rank` int DEFAULT 0,
  `earned_points` int DEFAULT 0,
  `audit_remark` varchar(255) DEFAULT NULL,
  `registration_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `invite_code` varchar(50) DEFAULT NULL,
  `show_in_profile` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_player_comp` (`player_id`,`competition_id`),
  KEY `fk_reg_comp_idx` (`competition_id`),
  CONSTRAINT `fk_reg_comp` FOREIGN KEY (`competition_id`) REFERENCES `competition` (`id`),
  CONSTRAINT `fk_reg_player` FOREIGN KEY (`player_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 4. 积分流水表 (对齐 class Point_history)
-- ----------------------------
DROP TABLE IF EXISTS `point_history`;
CREATE TABLE `point_history` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `change_amount` int DEFAULT 0,
  `reason` varchar(100) NOT NULL,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 5. 审核记录表 (辅助管理后台)
-- ----------------------------
DROP TABLE IF EXISTS `audit_record`;
CREATE TABLE `audit_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `competition_id` bigint NOT NULL,
  `auditor_id` bigint NOT NULL,
  `result` int NOT NULL COMMENT '1通过 2驳回',
  `remark` varchar(255) DEFAULT NULL,
  `audit_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 6. 通知数据表 (辅助主办方业务)
-- ----------------------------
DROP TABLE IF EXISTS `notice`;
CREATE TABLE `notice` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `competition_id` bigint NOT NULL,
  `title` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 7. 好友关系表 (对齐 class FriendRelation)
-- ----------------------------
DROP TABLE IF EXISTS `friend_relation`;
CREATE TABLE `friend_relation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `requester_id` bigint NOT NULL,
  `addressee_id` bigint NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'pending' COMMENT 'pending/accepted/rejected',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_friend_pair` (`requester_id`,`addressee_id`),
  KEY `idx_friend_requester` (`requester_id`),
  KEY `idx_friend_addressee` (`addressee_id`),
  KEY `idx_friend_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 8. 好友聊天消息表 (对齐 class FriendMessage)
-- ----------------------------
DROP TABLE IF EXISTS `friend_message`;
CREATE TABLE `friend_message` (
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

-- ======================================================
-- 插入测试数据 (满足组长路良钧的“完整性”要求)
-- 密码统一为: e10adc3949ba59abbe56e057f20f883e (即 123456)
-- ======================================================

-- 用户数据 (各角色齐备)
INSERT INTO `user` (`id`, `username`, `user_code`, `password`, `role`, `nickname`, `email`, `points`) VALUES
(1, 'admin', 'U000001', 'e10adc3949ba59abbe56e057f20f883e', 'ADMIN', '总管理员', 'admin@lesai.com', 0),
(2, 'org_zs', 'U000002', 'e10adc3949ba59abbe56e057f20f883e', 'ORGANIZER', '张主办', 'zhang@club.com', 0),
(3, 'player_mike', 'U000003', 'e10adc3949ba59abbe56e057f20f883e', 'PLAYER', '迈克', 'mike@test.com', 1500),
(4, 'player_jane', 'U000004', 'e10adc3949ba59abbe56e057f20f883e', 'PLAYER', '简', 'jane@test.com', 500),
(5, 'player_test', 'U000005', 'e10adc3949ba59abbe56e057f20f883e', 'PLAYER', '测试员', 'test@test.com', 0),
(6, 'test_admin', 'U000006', 'e10adc3949ba59abbe56e057f20f883e', 'ADMIN', '全功能测试账号', 'test_admin@lesai.com', 9999);

-- 赛事数据 (覆盖全状态: 0待审, 1报名, 2进行, 3结束, 4驳回)
INSERT INTO `competition`
(`id`, `competition_no`, `title`, `category`, `location`, `description`, `type`, `organizer_id`, `status`, `max_participants`, `current_participants`, `reward_points`, `reward`, `competition_format`, `group_count`, `start_time`, `end_time`, `invite_code`, `reject_reason`, `thumbnail_url`) VALUES
(1, 'NO.00000001', '正在招募的羽毛球赛', '羽毛球', '市体育馆', '面向校园羽毛球爱好者的公开招募赛事', 'PUBLIC', 2, 1, 32, 0, 100, '冠军奖牌与100积分', 'SINGLE_ELIMINATION', 0, '2026-06-24 09:00:00', '2026-06-24 18:00:00', NULL, NULL, '/default-thumbnails/badminton.png'),
(2, 'NO.00000002', '待审核的篮球赛', '篮球', '大学球场', '等待平台管理员审核的篮球赛事', 'PUBLIC', 2, 0, 16, 0, 100, '冠军奖杯', 'SINGLE_ELIMINATION', 0, '2026-07-01 10:00:00', '2026-07-02 18:00:00', NULL, NULL, '/default-thumbnails/basketball.png'),
(3, 'NO.00000003', '已结束的电竞周赛', '电竞', '线上', '用于演示历史成绩与积分记录的已结束赛事', 'PUBLIC', 2, 3, 16, 1, 200, '冠军200积分', 'SINGLE_ELIMINATION', 0, '2026-05-01 20:00:00', '2026-05-01 23:00:00', NULL, NULL, '/default-thumbnails/esports.png'),
(4, 'NO.00000004', '被驳回的棋牌聚会', '棋牌桌游', '茶室', '用于演示赛事审核驳回状态', 'PUBLIC', 2, 4, 20, 0, 50, '参与纪念品', 'SINGLE_ELIMINATION', 0, '2026-08-01 14:00:00', '2026-08-01 18:00:00', NULL, '赛事描述过于简单', '/default-thumbnails/boardgame.png'),
(5, 'NO.00000005', '校内私人羽毛球友谊赛', '羽毛球', '校内体育馆', '需要邀请码报名的校内私人赛事', 'PRIVATE', 2, 1, 8, 0, 0, '私人友谊赛无积分', 'SINGLE_ELIMINATION', 0, '2026-06-26 14:00:00', '2026-06-26 18:00:00', 'LESAI6', NULL, '/default-thumbnails/badminton.png'),
(6, 'NO.00000006', '正在进行的足球赛', '足球', '大学足球场', '用于演示开赛后录入成绩与结束赛事', 'PUBLIC', 2, 2, 22, 1, 150, '冠军150积分', 'SINGLE_ELIMINATION', 0, '2026-06-21 09:00:00', '2026-06-23 18:00:00', NULL, NULL, '/default-thumbnails/football.png');

-- 报名数据 (招募中的羽毛球赛不预置报名，避免无人报名时显示示例选手)
INSERT INTO `registration`
(`player_id`, `competition_id`, `status`, `review_status`, `register_type`, `team_name`, `team_members`, `contact_name`, `phone`, `final_score`, `final_rank`, `earned_points`, `invite_code`, `show_in_profile`) VALUES
(3, 3, 'finished', 1, 'team', '迈克战队', 'player_mike, player_jane', '迈克', '13800000001', '100', 1, 200, NULL, 1), -- 迈克参加过电竞赛并拿了第一名
(5, 5, 'pending', 0, 'single', '测试员', 'player_test', '测试员', '13800000003', '', 0, 0, 'LESAI6', 1), -- 私人赛事报名
(4, 6, 'ongoing', 1, 'single', '简', 'player_jane', '简', '13800000002', '', 0, 0, NULL, 1); -- 可用于演示录入成绩

-- 积分流水 (对应迈克的加分)
INSERT INTO `point_history` (`username`, `change_amount`, `reason`) VALUES 
('player_mike', 200, '参加[已结束的电竞周赛]获得第一名奖励');

-- 审核记录 (对应被驳回的比赛)
INSERT INTO `audit_record` (`competition_id`, `auditor_id`, `result`, `remark`) VALUES 
(4, 1, 2, '私人赛事描述过于简单，不符合社区规范');

-- 通知数据 (对应羽毛球赛)
INSERT INTO `notice` (`competition_id`, `title`, `content`) VALUES 
(1, '入场须知', '请各位选手自备球拍，准时在体育馆门口集合。');

-- 好友关系数据 (用于演示好友列表和申请通知)
INSERT INTO `friend_relation` (`requester_id`, `addressee_id`, `status`) VALUES
(3, 4, 'accepted'),
(5, 3, 'pending');

INSERT INTO `friend_message` (`sender_id`, `receiver_id`, `content`, `is_read`) VALUES
(3, 4, '这场羽毛球赛要不要一起组队？', 0),
(4, 3, '可以，我晚点看一下报名信息。', 1);

SET FOREIGN_KEY_CHECKS = 1;
