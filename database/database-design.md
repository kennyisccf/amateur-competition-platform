# 乐赛数据库设计文档

## 1. 数据库概述

| 项目 | 内容 |
| --- | --- |
| 数据库名 | `lesai_db` |
| 字符集 | `utf8mb4` |
| 存储引擎 | InnoDB |
| 初始化脚本 | `database/lesai.sql` |
| 升级脚本 | `database/upgrade_registration_fields.sql` |

数据库用于支撑用户、赛事、报名、赛程、审核、积分、通知和好友聊天等业务。

## 2. 表结构总览

| 表名 | 说明 |
| --- | --- |
| `user` | 用户表，保存账号、角色、积分、用户编号和好友设置 |
| `competition` | 赛事表，保存赛事基本信息、状态、邀请码、缩图和淘汰树状态 |
| `registration` | 报名表，保存参赛者报名、审核、成绩和档案可见性 |
| `point_history` | 积分流水表 |
| `audit_record` | 管理员赛事审核记录 |
| `notice` | 赛事通知数据 |
| `friend_relation` | 好友关系表 |
| `friend_message` | 好友聊天消息表 |

## 3. 核心关系

```text
user 1 --- N competition        一个主办方可创建多个赛事
user 1 --- N registration       一个参赛者可报名多个赛事
competition 1 --- N registration 一个赛事包含多条报名记录
competition 1 --- N notice       一个赛事可发布多个通知
competition 1 --- N audit_record 一个赛事可产生审核记录
user 1 --- N friend_relation     用户之间产生好友申请/关系
user 1 --- N friend_message      用户之间产生聊天消息
```

## 4. 数据字典

### 4.1 `user`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | bigint | 主键 |
| `username` | varchar(50) | 登录账号，唯一 |
| `user_code` | varchar(20) | 用户编号，如 `U000001` |
| `password` | varchar(255) | MD5 密码 |
| `role` | varchar(20) | `ADMIN` / `ORGANIZER` / `PLAYER` |
| `nickname` | varchar(50) | 昵称 |
| `email` | varchar(100) | 邮箱 |
| `points` | int | 当前积分 |
| `created_at` | datetime | 创建时间 |
| `is_deleted` | tinyint | 是否封禁/软删除 |
| `allow_friend_requests` | tinyint | 是否允许好友申请 |

### 4.2 `competition`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | bigint | 主键 |
| `competition_no` | varchar(20) | 赛事编号，如 `NO.00000001` |
| `title` | varchar(100) | 赛事名称 |
| `category` | varchar(50) | 赛事分类 |
| `location` | varchar(100) | 比赛地点 |
| `description` | text | 赛事描述 |
| `type` | varchar(10) | `PUBLIC` / `PRIVATE` |
| `organizer_id` | bigint | 主办方 ID |
| `status` | int | 赛事状态 |
| `max_participants` | int | 最大报名人数 |
| `current_participants` | int | 当前人数 |
| `reward_points` | int | 奖励积分 |
| `reward` | text | 奖励说明 |
| `competition_format` | varchar(30) | 赛制，当前主要为 `SINGLE_ELIMINATION` |
| `group_count` | int | 分组数量 |
| `start_time` | datetime | 开始时间 |
| `end_time` | datetime | 结束时间 |
| `created_at` | datetime | 创建时间 |
| `invite_code` | varchar(50) | 私人赛事邀请码 |
| `reject_reason` | varchar(255) | 驳回原因 |
| `bracket_state` | text | 淘汰树 JSON 状态 |
| `thumbnail_url` | varchar(500) | 缩图地址 |

### 4.3 `registration`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | bigint | 主键 |
| `player_id` | bigint | 参赛者 ID |
| `competition_id` | bigint | 赛事 ID |
| `status` | varchar(20) | `pending` / `ongoing` / `finished` / `rejected` |
| `review_status` | int | 审核状态 |
| `register_type` | varchar(20) | `single` 或 `team` |
| `team_name` | varchar(100) | 队伍名 |
| `team_members` | text | 队员账号 |
| `contact_name` | varchar(50) | 联系人 |
| `phone` | varchar(50) | 联系电话 |
| `final_score` | varchar(50) | 最终比分 |
| `final_rank` | int | 最终排名 |
| `earned_points` | int | 获得积分 |
| `audit_remark` | varchar(255) | 审核备注 |
| `registration_time` | datetime | 报名时间 |
| `invite_code` | varchar(50) | 报名时使用的邀请码 |
| `show_in_profile` | tinyint | 是否在个人档案显示 |

约束：`player_id + competition_id` 唯一，防止重复报名。

### 4.4 其他表

| 表 | 关键字段 | 说明 |
| --- | --- | --- |
| `point_history` | `username`, `change_amount`, `reason`, `time` | 积分流水 |
| `audit_record` | `competition_id`, `auditor_id`, `result`, `remark` | 审核记录 |
| `notice` | `competition_id`, `title`, `content` | 赛事通知 |
| `friend_relation` | `requester_id`, `addressee_id`, `status` | 好友申请/关系 |
| `friend_message` | `sender_id`, `receiver_id`, `content`, `is_read` | 好友聊天消息 |

## 5. 状态码

### 5.1 赛事状态

| 值 | 状态 | 说明 |
| --- | --- | --- |
| 0 | 待审核 | 公开赛事等待管理员审核 |
| 1 | 报名中 | 审核通过，可报名 |
| 2 | 进行中 | 比赛进行或可推进赛程 |
| 3 | 已结束 | 完赛归档 |
| 4 | 已驳回 | 管理员驳回 |

### 5.2 报名审核状态

| 值 | 状态 |
| --- | --- |
| 0 | 未审核 |
| 1 | 通过 |
| 2 | 未通过 |

### 5.3 好友状态

| 值 | 状态 |
| --- | --- |
| `pending` | 待处理 |
| `accepted` | 已通过 |
| `rejected` | 已拒绝 |

## 6. 样例数据

初始化脚本内置：

- 管理员：`admin`、`test_admin`
- 主办方：`org_zs`
- 参赛者：`player_mike`、`player_jane`、`player_test`
- 赛事状态覆盖：待审核、报名中、进行中、已结束、已驳回。
- 示例赛事日期已设置为未来时间段，便于本地运行和功能验证。

## 7. 设计说明

- 用户编号 `user_code` 用于好友搜索和用户识别。
- 赛事编号 `competition_no` 用于赛事检索。
- `bracket_state` 用于持久化淘汰树，避免刷新页面后丢失赛程。
- 好友消息通过 `is_read` 支撑未读通知统计。
- 删除好友后，未读消息会被清理为已读，避免通知残留。
