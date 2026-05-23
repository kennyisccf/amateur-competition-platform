# 乐赛 (LeSai) 数据库设计文档 (V2.1)

## 1. 概述
本项目数据库旨在支撑“乐赛一站式全民赛事组织服务平台”。文档定义的结构已完全适配项目企划书中的积分体系、双轨赛制、自动化审核及运动档案需求。

- **数据库名称**：`lesai_db`
- **字符集**：`utf8mb4` (支持 Emoji 及复杂中文字符)
- **存储引擎**：`InnoDB` (支持事务与外键)

## 2. 逻辑设计 (E-R 关系)
- **用户 (User) <---> 赛事 (Competition)**：1对多（主办方发布赛事）。
- **用户 (User) <---> 报名 (Registration)**：1对多（选手参加多项比赛）。
- **赛事 (Competition) <---> 报名 (Registration)**：1对多（一个赛事接受多人报名）。
- **赛事 (Competition) <---> 通知 (Notice)**：1对多（赛事下发多个公告）。
- **赛事 (Competition) <---> 审核 (Audit_Record)**：1对1（记录管理员对该赛事的审核结果）。
- **用户 (User) <---> 积分流水 (Point_History)**：1对多（记录用户每一次积分变动明细）。

## 3. 数据字典

### 3.1 用户表 (`user`)
| 字段名 | 类型 | 说明 | 约束 |
| :--- | :--- | :--- | :--- |
| id | bigint | 主键ID | 自增 |
| username | varchar(50) | 登录账号 | 唯一, 非空 |
| password | varchar(255) | 密码 (加密存储) | 非空 |
| role | enum | 角色 (ADMIN/ORGANIZER/PLAYER) | 非空 |
| nickname | varchar(50) | 用户昵称 | - |
| points | int | 当前累计总积分 | 默认 0 |
| level | varchar(20) | 段位名称 (如：青铜, 黄金) | 默认 '青铜' |
| created_at | timestamp | 注册时间 | DEFAULT NOW() |

### 3.2 赛事表 (`competition`)
| 字段名 | 类型 | 说明 | 约束 |
| :--- | :--- | :--- | :--- |
| id | bigint | 赛事ID | 主键 |
| title | varchar(100) | 赛事名称 | 非空 |
| category | enum | 类别 (篮球, 羽毛球, 电竞, 棋牌, 其他) | 非空 |
| location | varchar(255) | 比赛地点 (线下地址或"线上") | 默认 "线上" |
| organizer_id | bigint | 发布者ID | 外键关联 user.id |
| status | tinyint | 状态 (见4.1状态码定义) | 默认 0 |
| reward_points| int | 获胜基础奖励积分 | 默认 100 |
| start_time | datetime | 比赛开始时间 | 非空 |
| end_time | datetime | 比赛结束时间 | 非空 |

### 3.3 报名记录表 (`registration`)
| 字段名 | 类型 | 说明 | 约束 |
| :--- | :--- | :--- | :--- |
| id | bigint | 报名ID | 主键 |
| player_id | bigint | 选手ID | 外键关联 user.id |
| competition_id| bigint | 赛事ID | 外键关联 competition.id |
| status | tinyint | 报名状态 (0:待审, 1:成功, 2:拒绝) | 默认 0 |
| final_score | varchar(50) | 比赛最终比分/成绩 (如 "21-15") | - |
| earned_points | int | 本场实际获得积分 | 默认 0 |
| registration_time| timestamp | 报名提交时间 | DEFAULT NOW() |

### 3.4 赛事通知表 (`notice`)
| 字段名 | 类型 | 说明 | 约束 |
| :--- | :--- | :--- | :--- |
| id | bigint | 通知ID | 主键 |
| competition_id| bigint | 所属赛事ID | 外键关联 competition.id |
| title | varchar(100) | 通知标题 | 非空 |
| content | text | 通知正文内容 | 非空 |
| create_time | timestamp | 发布时间 | DEFAULT NOW() |

### 3.5 审核记录表 (`audit_record`)
| 字段名 | 类型 | 说明 | 约束 |
| :--- | :--- | :--- | :--- |
| id | bigint | 记录ID | 主键 |
| competition_id| bigint | 被审核赛事ID | 外键关联 competition.id |
| auditor_id | bigint | 审核人(管理员)ID | 外键关联 user.id |
| result | tinyint | 审核结果 (1:通过, 2:驳回) | 非空 |
| remark | varchar(255) | 审核意见/驳回原因 | - |
| audit_time | timestamp | 审核操作时间 | DEFAULT NOW() |

### 3.6 积分变动流水表 (`point_history`)
| 字段名 | 类型 | 说明 | 约束 |
| :--- | :--- | :--- | :--- |
| id | bigint | 流水ID | 主键 |
| user_id | bigint | 用户ID | 外键关联 user.id |
| change_amount | int | 变动数额 (正为加分，负为扣分) | 非空 |
| reason | varchar(255) | 变动原因说明 (如：参加某赛获胜) | 非空 |
| created_at | timestamp | 发生时间 | DEFAULT NOW() |

## 4. 业务状态码定义

### 4.1 赛事状态 (`competition.status`)
- `0`: **待审核** —— 主办方已提交，等待管理员批准。
- `1`: **报名中** —— 审核通过，选手可见并可申请。
- `2`: **进行中** —— 报名截止，赛事正在进行。
- `3`: **已结束** —— 比赛完成，积分已结算发放。
- `4`: **已驳回** —— 管理员拒绝办赛申请。

### 4.2 报名状态 (`registration.status`)
- `0`: **待处理** —— 选手已申请，等待主办方确认。
- `1`: **已确认** —— 主办方接受，选手正式参赛。
- `2`: **已拒绝** —— 主办方拒绝了该选手的参赛申请。

## 5. 测试数据说明
系统已内置以下典型数据，位于 `lesai.sql` 脚本中：
- **测试账号**：包含 `admin_root` (管理员), `lesai_club` (主办方), `player_mike` (高分选手)。
- **典型场景**：包含一场已过审的羽毛球赛（含通知示例）和一场待审核的电竞大赛。
- **关联数据**：包含完整的审核记录示例与积分变更流水记录。

## 6. 修改日志
- **V1.0**: 基础用户与赛事逻辑建立。
- **V2.0**: 引入积分体系、段位系统、多维度赛事类别及积分流水。
- **V2.1 (Current)**: 整合 `notice` 通知系统与 `audit_record` 管理员审计系统，补全状态码 4 (驳回) 逻辑。