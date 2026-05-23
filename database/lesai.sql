-- ======================================================
-- 乐赛 (LeSai) 数据库最终整合版 V2.1
-- 包含：用户、赛事、报名、积分流水、通知、审核记录
-- ======================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
CREATE DATABASE IF NOT EXISTS `lesai_db` CHARACTER SET utf8mb4;
USE `lesai_db`;

-- 1. 用户表
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL UNIQUE,
  `password` varchar(255) NOT NULL,
  `role` enum('ADMIN','ORGANIZER','PLAYER') NOT NULL,
  `nickname` varchar(50) DEFAULT NULL,
  `points` int DEFAULT 0,
  `level` varchar(20) DEFAULT '青铜',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 赛事表
DROP TABLE IF EXISTS `competition`;
CREATE TABLE `competition` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `category` enum('篮球','羽毛球','电竞','棋牌','其他') NOT NULL,
  `location` varchar(255) DEFAULT '线上',
  `organizer_id` bigint NOT NULL,
  `status` tinyint DEFAULT 0 COMMENT '0待审,1报名中,2进行中,3已结束,4已驳回',
  `reward_points` int DEFAULT 100,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_comp_user` FOREIGN KEY (`organizer_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 报名表
DROP TABLE IF EXISTS `registration`;
CREATE TABLE `registration` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `player_id` bigint NOT NULL,
  `competition_id` bigint NOT NULL,
  `status` tinyint DEFAULT 0 COMMENT '0待审,1成功,2拒绝',
  `final_score` varchar(50) DEFAULT NULL,
  `earned_points` int DEFAULT 0,
  `registration_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_reg_comp` FOREIGN KEY (`competition_id`) REFERENCES `competition` (`id`),
  CONSTRAINT `fk_reg_user` FOREIGN KEY (`player_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 赛事通知表 (新增)
DROP TABLE IF EXISTS `notice`;
CREATE TABLE `notice` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `competition_id` bigint NOT NULL,
  `title` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_notice_comp` FOREIGN KEY (`competition_id`) REFERENCES `competition` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 审核记录表 (新增)
DROP TABLE IF EXISTS `audit_record`;
CREATE TABLE `audit_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `competition_id` bigint NOT NULL,
  `auditor_id` bigint NOT NULL COMMENT '管理员ID',
  `result` tinyint NOT NULL COMMENT '1:通过, 2:驳回',
  `remark` varchar(255) DEFAULT NULL,
  `audit_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_audit_comp` FOREIGN KEY (`competition_id`) REFERENCES `competition` (`id`),
  CONSTRAINT `fk_audit_user` FOREIGN KEY (`auditor_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 积分流水表
DROP TABLE IF EXISTS `point_history`;
CREATE TABLE `point_history` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `change_amount` int NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_point_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- 丰富测试数据 (覆盖各种业务场景)
-- ----------------------------
INSERT INTO `user` VALUES 
(1, 'admin_root', '123456', 'ADMIN', '系统总管', 0, '无', NOW()),
(2, 'lesai_club', '123456', 'ORGANIZER', '乐赛官方俱乐部', 0, '无', NOW()),
(3, 'player_mike', '123456', 'PLAYER', '迈克', 1500, '白银', NOW()),
(4, 'player_jane', '123456', 'PLAYER', '简', 500, '青铜', NOW());

INSERT INTO `competition` VALUES 
(1, '第一届乐赛羽毛球公开赛', '羽毛球', '市体育馆', 2, 1, 150, '2026-06-10', '2026-06-12'),
(2, '社区电竞大赛-王者荣耀', '电竞', '线上', 2, 0, 200, '2026-07-01', '2026-07-05');

-- 模拟一条审核记录 (管理员审核了电竞大赛)
INSERT INTO `audit_record` (`competition_id`, `auditor_id`, `result`, `remark`) VALUES (2, 1, 1, '资料齐全，准予办赛');

-- 模拟一条通知
INSERT INTO `notice` (`competition_id`, `title`, `content`) VALUES (1, '场地变更通知', '原定于1号场地的比赛改为3号场地');

SET FOREIGN_KEY_CHECKS = 1;