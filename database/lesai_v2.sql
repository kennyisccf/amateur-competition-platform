SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

USE `lesai_db`;

-- 1. 用户表 (完善 points 相关)
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL UNIQUE,
  `password` varchar(255) NOT NULL,
  `role` enum('ADMIN','ORGANIZER','PLAYER') NOT NULL,
  `nickname` varchar(50) DEFAULT NULL,
  `points` int DEFAULT 0 COMMENT '当前总积分',
  `level` varchar(20) DEFAULT '青铜' COMMENT '段位名称(由积分计算得出)',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 赛事表 (完善字段：类别、地点、奖励积分)
DROP TABLE IF EXISTS `competition`;
CREATE TABLE `competition` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `category` enum('篮球','羽毛球','电竞','棋牌','其他') NOT NULL COMMENT '赛事类别',
  `location` varchar(255) DEFAULT '线上' COMMENT '比赛地点',
  `description` text,
  `type` enum('PUBLIC','PRIVATE') DEFAULT 'PUBLIC',
  `organizer_id` bigint NOT NULL,
  `status` tinyint DEFAULT 0 COMMENT '0待审核,1报名中,2进行中,3已结束',
  `max_participants` int DEFAULT 100,
  `current_participants` int DEFAULT 0,
  `reward_points` int DEFAULT 100 COMMENT '获胜可得基础积分',
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_comp_user_v2` FOREIGN KEY (`organizer_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 报名表 (完善字段：最终成绩、所获积分)
DROP TABLE IF EXISTS `registration`;
CREATE TABLE `registration` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `player_id` bigint NOT NULL,
  `competition_id` bigint NOT NULL,
  `status` tinyint DEFAULT 0 COMMENT '0审核中,1成功,2拒绝',
  `final_score` varchar(50) DEFAULT NULL COMMENT '比赛最终成绩(如 21-15)',
  `final_rank` int DEFAULT NULL COMMENT '最终名次',
  `earned_points` int DEFAULT 0 COMMENT '本场赛事实际获得的积分',
  `registration_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_player_comp` (`player_id`,`competition_id`),
  CONSTRAINT `fk_reg_comp_v2` FOREIGN KEY (`competition_id`) REFERENCES `competition` (`id`),
  CONSTRAINT `fk_reg_user_v2` FOREIGN KEY (`player_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 新增：积分变动流水表 (用于支撑个人运动档案)
DROP TABLE IF EXISTS `point_history`;
CREATE TABLE `point_history` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `change_amount` int NOT NULL COMMENT '变动数额(正负)',
  `reason` varchar(255) NOT NULL COMMENT '变动原因(如：参加某赛事获胜)',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_point_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='积分变动流水记录';

-- ----------------------------
-- 插入测试数据
-- ----------------------------

-- 插入 5 个测试用户
INSERT INTO `user` (`username`, `password`, `role`, `nickname`, `points`, `level`) VALUES 
('admin_linda', '123456', 'ADMIN', '林大管家', 0, '无'),
('org_club', '123456', 'ORGANIZER', '悦动俱乐部', 0, '无'),
('player_01', '123456', 'PLAYER', '扣篮王小张', 1250, '白银'),
('player_02', '123456', 'PLAYER', '羽球天后小李', 2100, '黄金'),
('player_03', '123456', 'PLAYER', '电竞大神小周', 500, '青铜');

-- 插入 3 场不同类别的赛事
INSERT INTO `competition` (`title`, `category`, `location`, `organizer_id`, `status`, `max_participants`, `reward_points`, `start_time`, `end_time`) VALUES 
('夏季3v3篮球赛', '篮球', '第一体育馆', 2, 1, 24, 200, '2026-06-01 10:00:00', '2026-06-01 18:00:00'),
('王者荣耀社区巅峰赛', '电竞', '线上', 2, 1, 100, 150, '2026-06-15 19:00:00', '2026-06-16 23:00:00'),
('周末羽毛球友谊单打', '羽毛球', '学校羽毛球馆', 2, 3, 8, 50, '2026-05-10 09:00:00', '2026-05-10 12:00:00');

-- 插入报名和成绩测试数据
-- 小张报了篮球赛
INSERT INTO `registration` (`player_id`, `competition_id`, `status`) VALUES (3, 1, 1);
-- 小李报了篮球赛
INSERT INTO `registration` (`player_id`, `competition_id`, `status`) VALUES (4, 1, 1);
-- 小李参加了已结束的羽毛球赛，获得了第1名和50积分
INSERT INTO `registration` (`player_id`, `competition_id`, `status`, `final_score`, `final_rank`, `earned_points`) 
VALUES (4, 3, 1, '21-12', 1, 50);

-- 插入积分流水
INSERT INTO `point_history` (`user_id`, `change_amount`, `reason`) VALUES (4, 50, '完成赛事[周末羽毛球友谊单打]获得冠军');

SET FOREIGN_KEY_CHECKS = 1;