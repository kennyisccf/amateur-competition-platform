# 乐赛平台接口说明文档 (API)

## 全局规范
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

---

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