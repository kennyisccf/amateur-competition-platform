**乐赛平台接口说明文档**

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

**全局规范**

* **基础路径:** http://localhost:8000
* **鉴权方式:** 目前暂未使用 JWT。如果是本地开发，跨域 POST 请求可能需要携带 CSRF Token，请先调用 /csrf/ 接口获取并在 Header 中携带 X-CSRFToken。
* **全局返回格式:**

JSON

{

&#x20; "success": true, // 或 false

&#x20; "msg": "提示信息" // 部分接口为 data

}



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
* **请求格式:** application/json (Raw JSON)
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

}



### **2.2 用户注册**

* **请求地址:** /api/register/
* **请求方式:** POST
* **请求格式:** multipart/form-data 或 application/x-www-form-urlencoded **(注意：这里不是 JSON)**
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



## **3. 赛事模块**

### **3.1 获取赛事详情**

* **请求地址:** /api/competition/[int:competition\\\_id](int:competition\\\\_id)/ (例如: /api/competition/1/)
* **请求方式:** GET
* **返回结果:**

JSON

{

&#x20; "success": true,

&#x20; "data": {

&#x20;   "id": 1,

&#x20;   "title": "赛事名称",

&#x20;   "category": "类别",

&#x20;   "location": "比赛地点",

&#x20;   "description": "赛事描述",

&#x20;   "type": "赛事类型",

&#x20;   "organizer": {

&#x20;     "id": 2,

&#x20;     "username": "organizer1",

&#x20;     "nickname": "主办方昵称"

&#x20;   },

&#x20;   "status": "状态",

&#x20;   "max\_participants": 100,

&#x20;   "current\_participants": 10,

&#x20;   "reward\_points": 100,

&#x20;   "start\_time": "2026-06-01T10:00:00",

&#x20;   "end\_time": "2026-06-02T18:00:00",

&#x20;   "created\_at": "2026-05-23T10:00:00"

&#x20; }

}

### **3.2 赛事报名**

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

1. `player_id` 为当前登录用户 ID，`competition_id` 为要报名的赛事 ID。
2. 后端会验证：
   - 用户存在且为选手角色
   - 赛事存在
   - 报名人数未超过上限
   - 用户未重复报名
3. 前端收到返回 JSON 后，根据 `success` 判断是否报名成功，并展示 `msg` 提示用户。
4. 建议用 axios 或 fetch 发送 POST 请求，设置 `Content-Type: application/json`。
5. 开发阶段 CSRF 可暂时使用 `@csrf_exempt`，生产环境请传递 CSRF Token。

### **3.3创建赛事**

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

* **返回结果:**JSON{&#x20; "success": true,&#x20; "msg": "赛事创建成功"}

------

### 3.4 获取待审核赛事

- **请求地址:** `/api/admin/pending_competitions/`
- **请求方式:** GET
- **请求格式:** 无

- **请求参数：**无

- **返回结果:**

```
{
    "success": true,
    "competitions": [
        {
            "id": ,
            "title": "",
            "category": "",
            "location": "",
            "description": "",
            "max_participants":,
            "current_participants":,
            "reward_points":,
            "start_time": "",
            "end_time": "",
            "organizer": {
                "id": ,
                "username": "",
                "nickname": ""
            }
        }
    ]
}
```

------

### 3.5 审核赛事

- **请求地址:** `/api/admin/review_competition/`
- **请求方式:** POST
- **请求格式:** application/json

- **请求参数:**

| 参数名         | 类型    | 必填 | 说明                             |
| -------------- | ------- | ---- | -------------------------------- |
| competition_id | integer | 是   | 赛事ID                           |
| status         | integer | 是   | 审核结果：1=审核通过，4=审核驳回 |

- **返回结果:**

```
{
    "success": true,
    "msg": "审核完成"
}
```

------

### 3.6 我的赛事

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
            "id":,
            "title": "",
            "category": "",
            "location": "",
            "description": "",
            "type": "",
            "status":,
            "max_participants": ,
            "current_participants": ,
            "reward_points": ,
            "start_time": "",
            "end_time": "",
            "invite_code": "",
            "reject_reason":
        }
    ]
}
```

------

### 3.7 删除赛事

- **请求地址:** `/api/competitions/<competition_id>/delete/`
- **请求方式:** DELETE
- **请求格式:** 无

- **路径参数:**

| 参数名         | 类型    | 必填 | 说明   |
| -------------- | ------- | ---- | ------ |
| competition_id | integer | 是   | 赛事ID |

- **返回结果:**

```
{
    "success": true,
    "msg": "删除成功"
}
```

------

### 3.8 修改赛事

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

### 3.9 查看赛事报名情况

- **请求地址:** `/api/competitions/<competition_id>/registrations/`
- **请求方式:** GET
- **请求格式:** 无

- **路径参数**

| 参数名         | 类型    | 必填 | 说明   |
| -------------- | ------- | ---- | ------ |
| competition_id | integer | 是   | 赛事ID |

- **返回结果**

```
{
    "success": true,
    "registrations": [
        {
            "registration_id": ,
            "player_id": ,
            "username": "",
            "nickname": "",
            "status": ,
            "registration_time": ""
        }
    ]
}
```

