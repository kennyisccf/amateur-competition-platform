# 乐赛 API 说明文档

## 1. 全局约定

| 项目 | 内容 |
| --- | --- |
| 后端地址 | `http://localhost:8000` |
| API 前缀 | `/api/` |
| 登录态 | Django Session / Cookie |
| 请求格式 | JSON 为主，缩图上传使用 `multipart/form-data` |
| 返回格式 | `{ "success": true/false, "msg": "...", ... }` |

当前系统不使用 Bearer Token。登录成功后，后端将用户信息写入 Session，前端通过 `withCredentials` 携带 Cookie。

## 2. 鉴权与用户

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| GET | `/api/login-captcha/` | 获取登录验证码 | 无 |
| POST | `/api/login/` | 用户登录 | 无 |
| POST | `/api/logout/` | 退出登录 | 登录 |
| POST | `/api/register/` | 用户注册 | 无 |
| GET | `/api/user/` | 当前用户详情 | 登录 |
| POST | `/api/update_user/` | 更新用户资料 | 登录 |
| GET | `/csrf/` | 获取 CSRF Token | 无 |

登录参数示例：

```json
{
  "username": "player_mike",
  "password": "123456",
  "captcha": "ABCD"
}
```

登录返回示例：

```json
{
  "success": true,
  "msg": "登录成功",
  "user_id": 3,
  "username": "player_mike",
  "role": "PLAYER",
  "is_super_admin": false
}
```

## 3. 赛事接口

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| GET | `/api/competitions/` | 赛事大厅列表 | 登录 |
| GET | `/api/competition/<id>/` | 赛事详情 | 登录 |
| POST | `/api/create_competition/` | 创建赛事 | `PLAYER` / `ORGANIZER` / `ADMIN` |
| GET | `/api/my_competitions/` | 我的赛事/赛事工作台 | `PLAYER` / `ORGANIZER` / `ADMIN` |
| PUT | `/api/competitions/<id>/update/` | 修改赛事 | 创建者/管理员 |
| DELETE | `/api/competitions/<id>/delete/` | 删除赛事 | 创建者/管理员 |
| POST | `/api/competitions/<id>/status/` | 更新赛事状态 | 创建者/管理员 |
| POST | `/api/upload/competition_thumbnail/` | 上传赛事缩图 | 登录 |

创建赛事核心字段：

| 字段 | 说明 |
| --- | --- |
| `title` | 赛事名称 |
| `category` | 赛事分类 |
| `location` | 比赛地点 |
| `description` | 赛事说明 |
| `type` | `PUBLIC` 或 `PRIVATE` |
| `max_participants` | 人数上限 |
| `reward_points` | 奖励积分 |
| `start_time` | 开始时间 |
| `end_time` | 结束时间 |
| `thumbnail_url` | 默认缩图或上传图路径 |

## 4. 报名接口

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | `/api/register_competition/` | 赛事报名 | 登录 |
| GET | `/api/competitions/<id>/registrations/` | 查看赛事报名 | 登录 |
| GET | `/api/my_registrations/` | 我的报名记录 | 登录 |
| POST | `/api/cancel_registration/` | 取消报名 | 登录 |
| POST | `/api/approve_registration/` | 通过报名 | 创建者/管理员 |
| POST | `/api/reject_registration/` | 驳回报名 | 创建者/管理员 |
| POST | `/api/registrations/status/` | 更新报名状态 | 创建者/管理员 |
| POST | `/api/registrations/visibility/` | 更新档案可见性 | 登录 |
| POST | `/api/admin/force_registration/` | 管理员强制添加报名 | 管理员 |
| DELETE | `/api/admin/registrations/<id>/delete/` | 删除报名记录 | 管理员 |
| POST | `/api/admin/registrations/bulk_delete/` | 批量删除报名记录 | 管理员 |

报名校验：

- 用户必须登录。
- 赛事必须存在。
- 赛事人数不能超过上限。
- 同一用户不能重复报名同一赛事。
- 私人赛事需邀请码正确。
- 战队报名会校验成员账号。

## 5. 淘汰树与结果接口

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| GET/POST | `/api/competitions/<id>/bracket/` | 读取或生成淘汰树 | 登录/创建者 |
| POST | `/api/record_result/` | 录入比赛结果 | 创建者/管理员 |

淘汰树数据保存在 `competition.bracket_state` 字段中。详见 [淘汰树设计说明](bracket-design.md)。

## 6. 消息通知与好友接口

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| GET | `/api/notifications/` | 消息中心 | 登录 |
| GET | `/api/friends/` | 好友列表和申请 | 登录 |
| GET | `/api/friends/search/` | 搜索用户/好友 | 登录 |
| POST | `/api/friends/request/` | 发送好友申请 | 登录 |
| POST | `/api/friends/respond/` | 通过或拒绝好友申请 | 登录 |
| GET/POST | `/api/friends/settings/` | 好友申请开关 | 登录 |
| GET/POST | `/api/friends/<user_id>/messages/` | 好友聊天消息 | 登录 |
| DELETE | `/api/friends/<user_id>/delete/` | 删除好友 | 登录 |

通知中心汇总：

- 好友申请。
- 好友聊天未读。
- 赛事审核驳回。
- 报名审核驳回。

删除好友时，系统会清理双方之间未读消息，避免通知残留。

## 7. 管理员接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/admin/pending_competitions/` | 待审核赛事 |
| POST | `/api/admin/review_competition/` | 审核赛事 |
| GET | `/api/admin/users/` | 用户列表 |
| POST | `/api/admin/users/create/` | 创建用户 |
| POST | `/api/admin/users/bulk_create/` | 批量生成用户 |
| POST | `/api/admin/users/bulk_delete/` | 批量删除用户 |
| PUT | `/api/admin/users/<id>/status/` | 封禁/解封用户 |
| DELETE | `/api/admin/users/<id>/delete/` | 删除用户 |
| GET | `/api/admin/audit_records/` | 审核记录 |
| GET | `/api/admin/stats/` | 平台统计 |
| POST | `/api/admin/competitions/bulk_add_users/` | 批量添加参赛者 |
| POST | `/api/admin/competitions/bulk_create/` | 批量创建赛事 |
| POST | `/api/admin/competitions/bulk_delete/` | 批量删除赛事 |

## 8. 状态码说明

### 8.1 赛事状态

| 值 | 含义 |
| --- | --- |
| 0 | 待审核 |
| 1 | 报名中 |
| 2 | 进行中 |
| 3 | 已结束 |
| 4 | 已驳回 |

### 8.2 报名审核状态

| 值 | 含义 |
| --- | --- |
| 0 | 未审核 |
| 1 | 审核通过 |
| 2 | 审核未通过 |

### 8.3 好友关系状态

| 值 | 含义 |
| --- | --- |
| `pending` | 待处理 |
| `accepted` | 已通过 |
| `rejected` | 已拒绝 |
