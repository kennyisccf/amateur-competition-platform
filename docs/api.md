# 乐赛平台接口说明文档 (API)

## 全局规范
* **前端代码位于**`amateur-competition-platform\backend\amateur_competition_platform\app1\views.py`

* **基础路径:** `http://localhost:8000/api`

* **请求头:** 所有需要鉴权的接口，均需要在 Header 中携带 `Authorization: Bearer <your_jwt_token>`

* **全局返回格式:**

    ```json
    {
      "code": 200,
      "message": "success",
      "data": {}
    }
    ```


## 1. 用户模块 (User)

### 1.1 用户登录
* **请求地址:** `/users/login/`
* **请求方式:** `POST`
* **功能说明:** 参赛选手、主办方或管理员登录获取 JWT Token。

**请求参数:**
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| username | String | 是 | 用户名 |
| password | String | 是 | 密码 |

**返回结果 (data 字段):**
| 字段名 | 类型 | 说明 |
|---|---|---|
| access | String | JWT 访问令牌 |
| refresh | String | JWT 刷新令牌 |
| role | String | 用户角色 (PLAYER, ORGANIZER, ADMIN) |
| user_id | Integer | 用户唯一 ID |

**响应示例:**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access": "eyJhbGciOiJIUz...",
    "refresh": "eyJhbGciOiJIUz...",
    "role": "PLAYER",
    "user_id": 1001
  }
}
```

## 2. 查看赛事详情（Competition Detail）

### 接口信息

- **URL**：`/api/competition/<competition_id>/`
- **方法**：GET
- 请求参数:`competition_id`（URL 参数）：赛事 ID，例如 `/api/competition/1/`

### 返回 JSON 示例

```
{
  "success": true,
  "data": {
    "id": 1,
    "title": "2026春季篮球联赛",
    "category": "篮球",
    "location": "体育馆A",
    "description": "业余组巅峰对决",
    "type": "PUBLIC",
    "organizer": {
      "id": 2,
      "username": "org_ali",
      "nickname": "阿里体育"
    },
    "status": 1,
    "max_participants": 50,
    "current_participants": 10,
    "reward_points": 100,
    "start_time": "2026-06-01T09:00:00",
    "end_time": "2026-06-15T18:00:00",
    "created_at": "2026-05-22T08:00:00"
  }
}
```

### 前端注意事项

1. 成功响应包含 `success: true` 和赛事详细数据。
2. `organizer` 字段包含主办方信息，前端可直接显示昵称或用户名。
3. 若赛事不存在，后端会返回 404 页面，可通过 axios 的 `catch` 捕获。

------

## 3. 报名赛事（Submit Registration）

### 接口信息

- **URL**：`/api/register/`
- **方法**：POST
- **请求数据（JSON）**：

```
{
  "player_id": 3,
  "competition_id": 1
}
```

### 返回 JSON 示例

#### 成功

```
{
  "success": true,
  "msg": "报名成功"
}
```

#### 失败（示例）

```
{
  "success": false,
  "msg": "你已报名该赛事"
}
```

### 前端注意事项

1. `player_id` 为当前登录用户 ID，`competition_id` 为要报名的赛事 ID。
2. 后端会验证：
   - 用户存在且为选手角色
   - 赛事存在
   - 报名人数未超过上限
   - 用户未重复报名
3. 前端收到返回 JSON 后，根据 `success` 判断是否报名成功，并展示 `msg` 提示用户。
4. 建议用 axios 或 fetch 发送 POST 请求，设置 `Content-Type: application/json`。
5. 开发阶段 CSRF 可暂时使用 `@csrf_exempt`，生产环境请传递 CSRF Token。

## 4.管理员获取待审核赛事

#### GET

```
axios.get('/api/admin/pending_competitions/')
```

返回：

```
{
  "success": true,
  "data": [...]
}
```

## 5.管理员审核赛事

### POST

```
axios.post('/api/admin/review_competition/', {
    competition_id: 1,
    status: 1
})
```

### 审核状态

| status | 含义 |
| ------ | ---- |
| 1      | 通过 |
| 4      | 驳回 |

## 6.获取赛事详细信息

#### GET

```
axios.get('api/competition/<int:competition_id>/')
```

返回：

```
{
  "success": true,
  "data": [...]
}
```

## 7.获取用户详细信息

#### GET

```
axios.get('api/user/<int:user_id>/')
```

返回：

```
{
  "success": true,
  "data": [...]
}
```

## 