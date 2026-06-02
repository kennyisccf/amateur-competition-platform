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
  `password` varchar(255) NOT NULL COMMENT 'MD5(123456) = e10adc3949ba59abbe56e057f20f883e',
  `role` varchar(20) NOT NULL COMMENT 'ADMIN/ORGANIZER/PLAYER',
  `nickname` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `points` int DEFAULT 0,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_deleted` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 2. 赛事表 (对齐 class Competition)
-- ----------------------------
DROP TABLE IF EXISTS `competition`;
CREATE TABLE `competition` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `category` varchar(50) NOT NULL,
  `location` varchar(100) NOT NULL,
  `description` text,
  `type` varchar(10) NOT NULL COMMENT 'PUBLIC/PRIVATE',
  `organizer_id` bigint NOT NULL,
  `status` int DEFAULT 0 COMMENT '0待审核 1报名中 2进行中 3已结束 4驳回',
  `max_participants` int DEFAULT 100,
  `current_participants` int DEFAULT 0,
  `reward_points` int DEFAULT 100,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `invite_code` varchar(50) DEFAULT NULL,
  `reject_reason` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
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
  `status` varchar(20) DEFAULT '' COMMENT 'pending ongoing finished ',
  `review_status` int DEFAULT 0, COMMENT '0未审核 1通过 2未通过'
  `final_score` varchar(50) NOT NULL DEFAULT '',
  `final_rank` int DEFAULT 0,
  `earned_points` int DEFAULT 0,
  `audit_remark` varchar(255) DEFAULT NULL,
  `registration_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `invite_code` varchar(50) DEFAULT NULL,
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_time` (`username`, `time`)
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

-- ======================================================
-- 插入测试数据 (满足组长路良钧的“完整性”要求)
-- 密码统一为: e10adc3949ba59abbe56e057f20f883e (即 123456)
-- ======================================================

-- 用户数据 (各角色齐备)
INSERT INTO `user` (`id`, `username`, `password`, `role`, `nickname`, `email`, `points`) VALUES 
(1, 'admin', 'e10adc3949ba59abbe56e057f20f883e', 'ADMIN', '总管理员', 'admin@lesai.com', 0),
(2, 'org_zs', 'e10adc3949ba59abbe56e057f20f883e', 'ORGANIZER', '张主办', 'zhang@club.com', 0),
(3, 'player_mike', 'e10adc3949ba59abbe56e057f20f883e', 'PLAYER', '迈克', 'mike@test.com', 1500),
(4, 'player_jane', 'e10adc3949ba59abbe56e057f20f883e', 'PLAYER', '简', 'jane@test.com', 500),
(5, 'player_test', 'e10adc3949ba59abbe56e057f20f883e', 'PLAYER', '测试员', 'test@test.com', 0);

-- 赛事数据 (覆盖全状态: 0待审, 1报名, 2进行, 3结束, 4驳回)
INSERT INTO `competition` (`id`, `title`, `category`, `location`, `type`, `organizer_id`, `status`, `start_time`, `end_time`) VALUES 
(1, '正在招募的羽毛球赛', '羽毛球', '市体育馆', 'PUBLIC', 2, 1, '2026-06-10 09:00:00', '2026-06-10 18:00:00'),
(2, '待审核的篮球赛', '篮球', '大学球场', 'PUBLIC', 2, 0, '2026-07-01 10:00:00', '2026-07-02 18:00:00'),
(3, '已结束的电竞周赛', '电竞', '线上', 'PUBLIC', 2, 3, '2026-05-01 20:00:00', '2026-05-01 23:00:00'),
(4, '被驳回的棋牌聚会', '棋牌', '茶室', 'PRIVATE', 2, 4, '2026-08-01 14:00:00', '2026-08-01 18:00:00');

-- 报名数据 (包含成功与待定)
INSERT INTO `registration` (`player_id`, `competition_id`, `status`, `final_score`, `final_rank`, `earned_points`) VALUES 
(3, 1, 1, '', 0, 0), -- 迈克成功报名羽毛球赛
(4, 1, 0, '', 0, 0), -- 简正在申请羽毛球赛
(3, 3, 1, '100', 1, 200); -- 迈克参加过电竞赛并拿了第一名

-- 积分流水 (对应迈克的加分)
INSERT INTO `point_history` (`username`, `change_amount`, `reason`) VALUES 
('player_mike', 200, '参加[已结束的电竞周赛]获得第一名奖励');

-- 审核记录 (对应被驳回的比赛)
INSERT INTO `audit_record` (`competition_id`, `auditor_id`, `result`, `remark`) VALUES 
(4, 1, 2, '私人赛事描述过于简单，不符合社区规范');

-- 通知数据 (对应羽毛球赛)
INSERT INTO `notice` (`competition_id`, `title`, `content`) VALUES 
(1, '入场须知', '请各位选手自备球拍，准时在体育馆门口集合。');

SET FOREIGN_KEY_CHECKS = 1;