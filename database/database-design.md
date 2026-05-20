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