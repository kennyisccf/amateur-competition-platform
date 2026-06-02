**乐赛平台接口说明文档**

## 全局规范
* **后端代码位于**`amateur-competition-platform\backend\amateur_competition_platform\app1\views.py`

* **基础路径:** `http://localhost:8000/api`

* **请求头:** 当前使用 **Session/Cookie** 进行状态保持。前端在登录成功后，浏览器会自动保存 `sessionid` Cookie。后续调用需要鉴权的接口时，请确保请求携带 Cookie。

* **全局返回格式:**

    ```json
    {
      "code": 200,
      "message": "success",
      "data": {}
    }
    ```



## **1. 基础模块**


### **1.1 获取 CSRF Token**

* **请求地址:** /csrf/
* **请求方式:** GET
* **功能说明:** 获取用于防御跨站请求伪造的 Token。
* **返回结果:**

JSON

{

&#x20; "csrfToken": "your\_token\_string"

}


## **2. 用户模块**


### **2.1 用户登录**

* **请求地址:** /api/login/
* **请求方式:** POST
* **请求格式:** application/json
* **请求参数:**

|**参数名**|**类型**|**必填**|**说明**|
|-|-|-|-|
|username|String|是|用户名|
|password|String|是|密码|
|role|String|是|角色中文，传："选手"、"主办方" 或 "管理员"|

* **返回结果:**

JSON

{

&#x20; "success": true,

&#x20; "msg": "登录成功",

&#x20; "user\_id": 1

&#x20; "token": "jwt_token_string"

}



### **2.2 用户注册**

* **请求地址:** /api/register/
* **请求方式:** POST
* **请求格式:** multipart/form-data 或 application/x-www-form-urlencoded
* **请求参数:**

|**参数名**|**类型**|**必填**|**说明**|
|-|-|-|-|
|username|String|是|用户名（最长50字符）|
|password|String|是|密码|
|password2|String|是|确认密码|
|role|String|否|角色英文，传：PLAYER, ORGANIZER, ADMIN（默认 PLAYER）|
|nickname|String|否|昵称（最长50字符，默认同用户名）|
|email|String|否|邮箱|

* **返回结果:**

JSON

{

&#x20; "success": true,

&#x20; "msg": "注册成功"

}


### **2.3 退出登录**

* **请求地址:** /api/logout/
* **请求方式:** POST

* **返回结果:**

JSON

{

&#x20; "success": true,

&#x20; "msg": "退出登录"

}



## **3. 赛事模块**

### **3.1 获取公开赛事列表**

* **请求地址:** /api/competitions/
* **请求方式:** GET
* **请求参数:**

|**参数名**|**类型**|**必填**|**说明**|
|-|-|-|-|
|category|String|否|赛事分类筛选|
|keyword|String|否|标题关键字搜索|

* **返回结果:**

JSON

{
  "success": true,
  "competitions": [
    {
      "id": 1,
      "title": "赛事名称",
      "category": "类别",
      "location": "比赛地点",
      "description": "赛事描述",
      "type": "PUBLIC",
      "status": 1,
      "max_participants": 100,
      "current_participants": 10,
      "reward_points": 100,
      "start_time": "2026-06-01 10:00:00",
      "end_time": "2026-06-02 18:00:00",
      "created_at": "2026-05-23 10:00:00",
      "organizer": {
        "id": 2,
        "username": "organizer1",
        "nickname": "主办方昵称"
      }
    }
  ]
}


### **3.2 获取赛事详情**

* **请求地址:** /api/competition/<int:competition_id>/
* **请求方式:** GET

* **返回结果:**

JSON

{
  "success": true,
  "data": {
    "id": 1,
    "title": "赛事名称",
    "category": "类别",
    "location": "比赛地点",
    "description": "赛事描述",
    "type": "赛事类型",
    "organizer": {
      "id": 2,
      "username": "organizer1",
      "nickname": "主办方昵称"
    },
    "status": 1,
    "max_participants": 100,
    "current_participants": 10,
    "reward_points": 100,
    "start_time": "2026-06-01T10:00:00",
    "end_time": "2026-06-02T18:00:00",
    "created_at": "2026-05-23 10:00:00"
  }
}


### **3.3 赛事报名**

* **请求地址:** /api/register_competition/ 
* **请求方式:** POST
* **请求格式:** application/json
* **请求参数:**

|**参数名**|**类型**|**必填**|**说明**|
|-|-|-|-|
|player\_id|Integer|是|选手 ID|
|competition\_id|Integer|是|赛事 ID|
|invite_code|string|否|私人赛事邀请码|

* **返回结果:**

JSON

{

&#x20; "success": true,

&#x20; "msg": "报名成功"

}


### **3.4 创建赛事**

- **请求地址:** /api/create_competition/ 
- **请求方式:**POST
- **请求格式:**application/json
- **请求参数:**

| **参数名**       | **类型** | **必填** | **说明**                            |
| ---------------- | -------- | -------- | ----------------------------------- |
| title            | string   | 是       | 赛事名称                            |
| category         | string   | 是       | 赛事种类                            |
| location         | string   | 是       | 赛事地点                            |
| description      | string   | 是       | 赛事描述                            |
| competition_type | string   | 是       | 是否公开，PUBLIC:公开，PRIVATE:私人 |
| organizer_id     | integer  | 是       | 主办方id                            |
| max_participants | integer  | 是       | 最大参与人数                        |
| reward_points    | integer  | 是       | 奖励积分                            |
| start_time       | datetime | 是       | 开始时间                            |
| end_time         | datetime | 是       | 结束时间                            |

* **返回结果:**

JSON

{
  "success": true,
  "msg": "赛事创建成功",
  "competition_id": 1,
  "status": 1,
  "invite_code": "AB12CD" 
}

------


### 3.5 我的赛事(主办方端)

- **请求地址:** `/api/my_competitions/`
- **请求方式:** GET
- **请求格式:** Query Params

- **请求参数:**

| 参数名       | 类型    | 必填 | 说明               |
| ------------ | ------- | ---- | ------------------ |
| organizer_id | integer | 是   | 主办方ID           |
| status       | integer | 否   | 赛事状态筛选       |
| type         | string  | 否   | 赛事类型筛选       |
| keyword      | string  | 否   | 赛事标题关键词搜索 |

- **请求示例:**

```
/api/my_competitions/?organizer_id=2&status=1
```

- **返回结果:**

```
{
  "success": true,
  "competitions": [
    {
      "id": 1,
      "title": "赛事名称",
      "category": "类别",
      "location": "比赛地点",
      "description": "赛事描述",
      "type": "PUBLIC",
      "status": 1,
      "max_participants": 100,
      "current_participants": 10,
      "reward_points": 100,
      "start_time": "2026-06-01T10:00:00",
      "end_time": "2026-06-02T18:00:00",
      "created_at": "2026-05-23T10:00:00",
      "invite_code": "",
      "reject_reason": null
    }
  ]
}
```

------

### 3.6 删除赛事

- **请求地址:** `/api/competitions/<competition_id>/delete/`
- **请求方式:** DELETE

- **返回结果:**

```
{
    "success": true,
    "msg": "删除成功"
}
```

------

### 3.7 修改赛事

- **请求地址:** `/api/competitions/<competition_id>/update/`
- **请求方式:** PUT
- **请求格式:** application/json

- **请求参数**

| 参数名           | 类型    | 必填 | 说明         |
| ---------------- | ------- | ---- | ------------ |
| title            | string  | 否   | 赛事名称     |
| category         | string  | 否   | 赛事分类     |
| location         | string  | 否   | 赛事地点     |
| description      | string  | 否   | 赛事描述     |
| max_participants | integer | 否   | 最大参与人数 |
| reward_points    | integer | 否   | 奖励积分     |

- **返回结果**

```
{
    "success": true,
    "msg": "修改成功"
}
```

------

### 3.8 查看赛事报名情况

- **请求地址:** `/api/competitions/<competition_id>/registrations/`
- **请求方式:** GET


- **返回结果**

```
{
  "success": true,
  "registrations": [
    {
      "registration_id": 1,
      "player_id": 2,
      "username": "player1",
      "nickname": "选手昵称",
      "status": 1,
      "registration_time": "2026-05-24T10:00:00"
    }
  ]
}
```


## **4. 个人档案模块**



### **4.1 获取个人信息与积分**

* **请求地址:** /api/user/
* **请求方式:** GET
* **权限说明:** 需要先登录，通过 Session 验证

* **返回结果:**

{ 
  "success": true,
  "data": {
    "id": 1,
    "username": "username",
    "nickname": "nickname",
    "email": "user@example.com",
    "role": "PLAYER",
    "points": 100,
    "created_at": "2026-05-20 10:00:00",
    "is_deleted": false
  }
}


### **4.2 修改个人信息**

* **请求地址:** /api/update_user/
* **请求方式:** POST
* **请求格式:** application/json
* **权限说明:** 需要先登录，通过 Session 验证
* **请求参数:**

|**参数名**|**类型**|**必填**|**说明**|
|-|-|-|-|
|nickname|String|否|新昵称|
|email|String|否|新邮箱|

* **返回结果:**

JSON

{

&#x20; "success": true,

&#x20; "msg": "注册成功"

}

### **4.3 获取我的报名记录**

* **请求地址:** /api/my_registrations/
* **请求方式:** GET
* **权限说明:** 需要先登录，接口自动从 Session 获取当前登录用户 ID，无需额外传参。


* **返回结果:**

{ 
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "赛事名称",
      "time": "2026-05-24 10:00",
      "desc": "审核备注",
      "status": "finished",
      "statusText": "报名成功"
    }
  ]
}


## **5. 管理员模块**


### 5.1 获取待审核赛事

- **请求地址:** `/api/admin/pending_competitions/`
- **请求方式:** GET
- **请求格式:** 无

- **返回结果:**

```
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "赛事名称",
      "category": "类别",
      "location": "比赛地点",
      "description": "赛事描述",
      "max_participants": 100,
      "current_participants": 0,
      "reward_points": 100,
      "start_time": "2026-06-01T10:00:00",
      "end_time": "2026-06-02T18:00:00",
      "organizer": {
        "id": 2,
        "username": "organizer1",
        "nickname": "主办方昵称"
      }
    }
  ]
}```


### 5.2 审核赛事

- **请求地址:** `/api/admin/review_competition/`
- **请求方式:** POST
- **请求格式:** application/json

- **请求参数:**

| 参数名         | 类型    | 必填 | 说明                             |
| -------------- | ------- | ---- | -------------------------------- |
| competition_id | integer | 是   | 赛事ID                           |
| status         | integer | 是   | 审核结果：1=审核通过，4=审核驳回 |
| reason         | String  | 否   | 驳回原因 |


- **返回结果:**

```
{
    "success": true,
    "msg": "审核完成"
}
```


### 5.3 获取用户列表

- **请求地址:** `/api/admin/users/`
- **请求方式:** GET
- **请求格式:** 无


- **返回结果:**

```
{
  "success": true,
  "users": [
    {
      "user_id": ,
      "username": "",
      "role": "",
      "is_active": ,
      "created_at": ""
    }
  ]
}


```


### 5.4 封禁/解封用户

- **请求地址:** `/api/admin/users/<int:user_id>/status/`
- **请求方式:** PUT
- **请求格式:** application/json

- **请求参数:**

| 参数名     | 类型    | 必填 | 说明                  |
| ----------| ------- | ---- | -------------------- |
| is_active | Boolean | 是   | true=解封，false=封禁 |



- **返回结果:**

```
{
  "success": true,
  "msg": "用户状态更新成功"
}  


```

### 5.5 获取审核记录

- **请求地址:** `/api/admin/audit_records/`
- **请求方式:** GET
- **请求格式:** 无



- **返回结果:**

```
{
  "success": true,
  "records": [
    {
      "record_id": ,
      "competition_id": ,
      "admin_id": ,
      "action": "审核通过",
      "created_at": ""
    }
  ]
}


```





