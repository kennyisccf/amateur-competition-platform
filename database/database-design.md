# 数据库设计说明

本项目主要包含以下数据表：

1. user 用户表
2. competition 赛事表
3. registration 报名表
4. notice 赛事通知表
5. audit_record 审核记录表
# 乐赛 (LeSai) 数据库设计文档 (V1.0)

## 1. 概述
本项目采用 MySQL 8.0 数据库，字符集使用 `utf8mb4`。主要用于支撑业余赛事的创建、报名及用户管理。

## 2. 逻辑设计 (E-R 关系)
- **User (1) <---> (N) Competition**: 一个主办方可以发布多个赛事。
- **User (1) <---> (N) Registration**: 一个选手可以有多个报名记录。
- **Competition (1) <---> (N) Registration**: 一个赛事可以接收多个选手的报名。

## 3. 数据字典

### 3.1 用户表 (user)
| 字段名 | 类型 | 说明 | 约束 |
| :--- | :--- | :--- | :--- |
| id | bigint | 主键ID | 自增 |
| username | varchar(50) | 登录账号 | 唯一, 非空 |
| role | enum | 角色 (ADMIN/ORGANIZER/PLAYER) | 非空 |
| points | int | 用户累计积分 | 默认为0 |

### 3.2 赛事表 (competition)
| 字段名 | 类型 | 说明 | 约束 |
| :--- | :--- | :--- | :--- |
| id | bigint | 赛事ID | 主键 |
| type | enum | 类型 (PUBLIC-公开赛 / PRIVATE-私人赛) | 默认 PUBLIC |
| status | tinyint | 状态 (0-待核, 1-报名中, 2-进行中, 3-结束) | 默认 0 |
| organizer_id | bigint | 发布者ID | 外键关联 user.id |

### 3.3 报名表 (registration)
| 字段名 | 类型 | 说明 | 约束 |
| :--- | :--- | :--- | :--- |
| player_id | bigint | 选手ID | 外键关联 user.id |
| competition_id | bigint | 赛事ID | 外键关联 competition.id |
| status | tinyint | 状态 (0-审核中, 1-成功, 2-驳回) | 默认 0 |

## 4. 测试账号矩阵
| 账号 | 初始密码 | 角色 | 权限说明 |
| :--- | :--- | :--- | :--- |
| admin01 | 123456 | 管理员 | 审核赛事、管理用户 |
| org_ali | 123456 | 主办方 | 创建赛事、审核选手报名 |
| player_zs | 123456 | 选手 | 浏览赛事、提交报名 |


# 乐赛 (LeSai) 数据库设计文档 (V2.0)

## 1. 概述
本项目数据库旨在支撑“乐赛一站式全民赛事组织服务平台”。V2.0 版本在 V1.0 基础上强化了积分段位体系、多维度赛事管理以及个人运动档案流水功能，完全适配项目企划书需求。
数据库名称：lesai_db
字符集：utf8mb4 (支持表情及复杂中文字符)
存储引擎：InnoDB

## 2. 逻辑设计 (E-R 关系)
用户 (User) <---> 赛事 (Competition)：1对多（主办方发布赛事）。
用户 (User) <---> 报名 (Registration)：1对多（选手参加多项比赛）。
赛事 (Competition) <---> 报名 (Registration)：1对多（一个赛事接受多人报名）。
用户 (User) <---> 积分流水 (Point_History)：1对多（记录用户每一次积分变动明细）。

## 3. 数据字典

### 3.1 用户表 (user)
字段名	类型	说明	约束
id	bigint	主键ID	自增
username	varchar(50)	登录账号	唯一, 非空
password	varchar(255)	密码 (建议加密存储)	非空
role	enum	角色 (ADMIN/ORGANIZER/PLAYER)	非空
nickname	varchar(50)	用户昵称	-
points	int	当前累计总积分	默认 0
level	varchar(20)	段位名称 (如：青铜, 黄金)	默认 '青铜'
created_at	timestamp	注册时间	自动生成

### 3.2 赛事表 (competition)
字段名	类型	说明	约束
id	bigint	赛事ID	主键
title	varchar(100)	赛事名称	非空
category	enum	类别 (篮球, 羽毛球, 电竞, 棋牌, 其他)	非空
location	varchar(255)	比赛地点 (线下地址或"线上")	默认 "线上"
organizer_id	bigint	发布者ID	外键关联 user.id
status	tinyint	状态 (0:待审, 1:报名中, 2:进行中, 3:已结束)	默认 0
reward_points	int	获胜基础奖励积分	默认 100
start_time	datetime	比赛开始时间	非空
end_time	datetime	比赛结束时间	非空

### 3.3 报名记录表 (registration)
字段名	类型	说明	约束
id	bigint	报名ID	主键
player_id	bigint	选手ID	外键关联 user.id
competition_id	bigint	赛事ID	外键关联 competition.id
status	tinyint	报名状态 (0:审核中, 1:成功, 2:驳回)	默认 0
final_score	varchar(50)	比赛最终比分/成绩 (如 "21-15")	-
final_rank	int	最终名次	-
earned_points	int	本场实际获得积分	默认 0

### 3.4 积分变动流水表 (point_history)
字段名	类型	说明	约束
id	bigint	流水ID	主键
user_id	bigint	用户ID	外键关联 user.id
change_amount	int	变动数额 (正数为加分，负数为扣分)	非空
reason	varchar(255)	变动原因说明	非空
created_at	timestamp	发生时间	自动生成

## 4. 业务状态码定义

### 4.1 赛事状态 (competition.status)
0: 待审核 —— 主办方提交，等待管理员批准。
1: 报名中 —— 选手可在前端看到并点击报名。
2: 进行中 —— 报名截止，比赛正在开展或等待录入成绩。
3: 已结束 —— 成绩已录入，积分已发放。

### 4.2 报名状态 (registration.status)
0: 审核中 —— 选手已申请，等待主办方确认。
1: 已确认 —— 选手获得参赛资格。
2: 已驳回 —— 主办方拒绝了选手的报名请求。

## 5. 测试数据说明
系统已初始化以下典型数据供开发调试：
多角色账号：包含管理员、俱乐部主办方、以及不同积分等级的选手（青铜、白银、黄金）。
多类别赛事：覆盖了篮球（线下）、电竞（线上）、羽毛球（已结束）三种场景。
闭环流水：包含一条完整的“比赛结束 -> 录入成绩 -> 自动加分 -> 生成流水”的示例数据，位于 point_history 中。

## 6. 安全与维护建议
索引优化：已对 organizer_id 和 player_id 建立外键索引，提升关联查询效率。
数据一致性：earned_points 的变动应与 user.points 的更新保持在同一个事务中处理。
逻辑删除：V2.0 暂不强制物理删除，建议重要业务数据保留 is_deleted 标记空间。