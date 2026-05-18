-- Active: 1779072788328@@127.0.0.1@3306@mysql
/*
 Navicat MySQL Data Transfer
 Target Server Type    : MySQL
 Target Server Version : 80046
 File Encoding         : 65001
 Project               : 乐赛一站式服务平台 (LeSai Platform)
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 1. 创建数据库
-- ----------------------------
CREATE DATABASE IF NOT EXISTS `lesai_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lesai_db`;

-- ----------------------------
-- 2. 创建用户表 (user)
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` varchar(50) NOT NULL UNIQUE COMMENT '登录账号',
  `password` varchar(255) NOT NULL COMMENT '密码(明文存储仅限测试，建议后期加密)',
  `role` enum('ADMIN','ORGANIZER','PLAYER') NOT NULL DEFAULT 'PLAYER' COMMENT '角色: ADMIN-管理员, ORGANIZER-主办方, PLAYER-选手',
  `nickname` varchar(50) DEFAULT NULL COMMENT '昵称',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `points` int DEFAULT 0 COMMENT '积分',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `is_deleted` tinyint(1) DEFAULT 0 COMMENT '逻辑删除: 0-正常, 1-已删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='用户基础信息表';

-- ----------------------------
-- 3. 创建赛事表 (competition)
-- ----------------------------
DROP TABLE IF EXISTS `competition`;
CREATE TABLE `competition` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '赛事ID',
  `title` varchar(100) NOT NULL COMMENT '赛事名称',
  `description` text COMMENT '赛事介绍',
  `type` enum('PUBLIC','PRIVATE') DEFAULT 'PUBLIC' COMMENT '赛事类型: PUBLIC-公开积分赛, PRIVATE-私人赛',
  `organizer_id` bigint NOT NULL COMMENT '主办方ID(关联user表)',
  `status` tinyint DEFAULT 0 COMMENT '状态: 0-待审核, 1-报名中, 2-进行中, 3-已结束',
  `max_participants` int DEFAULT 100 COMMENT '人数上限',
  `current_participants` int DEFAULT 0 COMMENT '已报名人数',
  `start_time` datetime NOT NULL COMMENT '开始时间',
  `end_time` datetime NOT NULL COMMENT '结束时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_organizer` (`organizer_id`),
  CONSTRAINT `fk_comp_user` FOREIGN KEY (`organizer_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='赛事信息表';

-- ----------------------------
-- 4. 创建报名记录表 (registration)
-- ----------------------------
DROP TABLE IF EXISTS `registration`;
CREATE TABLE `registration` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '报名ID',
  `player_id` bigint NOT NULL COMMENT '选手ID(关联user表)',
  `competition_id` bigint NOT NULL COMMENT '赛事ID(关联competition表)',
  `status` tinyint DEFAULT 0 COMMENT '报名状态: 0-审核中, 1-报名成功, 2-已驳回',
  `audit_remark` varchar(255) DEFAULT NULL COMMENT '审核意见',
  `registration_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报名提交时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_player_comp` (`player_id`,`competition_id`) COMMENT '防止重复报名',
  KEY `idx_comp` (`competition_id`),
  CONSTRAINT `fk_reg_comp` FOREIGN KEY (`competition_id`) REFERENCES `competition` (`id`),
  CONSTRAINT `fk_reg_user` FOREIGN KEY (`player_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='赛事报名表';

-- ----------------------------
-- 5. 准备测试数据
-- ----------------------------

-- 测试账号 (密码统一为 123456)
INSERT INTO `user` (`username`, `password`, `role`, `nickname`, `email`, `points`) VALUES 
('admin01', '123456', 'ADMIN', '平台总管', 'admin@lesai.com', 0),
('org_ali', '123456', 'ORGANIZER', '阿里体育', 'contact@ali.com', 0),
('player_zs', '123456', 'PLAYER', '张三', 'zs@example.com', 500),
('player_ls', '123456', 'PLAYER', '李四', 'ls@example.com', 1200);

-- 测试赛事 (主办方ID=2，即 org_ali)
INSERT INTO `competition` (`title`, `description`, `type`, `organizer_id`, `status`, `max_participants`, `start_time`, `end_time`) VALUES 
('2026春季篮球联赛', '业余组巅峰对决', 'PUBLIC', 2, 1, 50, '2026-06-01 09:00:00', '2026-06-15 18:00:00'),
('内部羽毛球友谊赛', '仅限受邀成员', 'PRIVATE', 2, 1, 20, '2026-07-10 14:00:00', '2026-07-10 18:00:00');

-- 测试报名记录 (选手3报名赛事1)
INSERT INTO `registration` (`player_id`, `competition_id`, `status`, `audit_remark`) VALUES 
(3, 1, 1, '系统自动通过');

SET FOREIGN_KEY_CHECKS = 1;