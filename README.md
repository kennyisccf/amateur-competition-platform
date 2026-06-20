# 乐赛：一站式业余赛事组织服务平台

「乐赛」面向校园社团、兴趣组织和大众业余赛事场景，提供赛事发现、报名审核、赛程生成、结果记录、积分档案、好友互动与消息通知的一体化平台。

项目的核心目标不是做一个静态报名表，而是把一次业余比赛抽象成可追踪、可推进、可回滚的数字化业务闭环。

## 项目概况

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 乐赛 amateur-competition-platform |
| 项目类型 | Web 前后端分离应用 |
| 主要用户 | 参赛者、赛事主办方、管理员 |
| 核心用例 | 18 个 |
| 源文件规模 | 50 个代码/SQL 源文件 |
| 代码规模 | 约 12448 行 |

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、Vite、Element Plus、Vue Router、Axios |
| 后端 | Python、Django、Session/Cookie 登录态、CSRF、验证码 |
| 数据库 | MySQL 8.0、utf8mb4、InnoDB |
| 静态资源 | 默认赛事缩图、本地上传缩图、登录/注册背景图 |

## 团队成员与分工

| 成员 | GitHub | 主要职责 | 工作内容 |
| --- | --- | --- | --- |
| 张振丰 | @kennyisccf | 项目经理 / 产品经理 / 前端开发 | 负责项目整体规划、需求收敛、核心前端开发、产品体验打磨、赛事大厅、赛事详情、报名管理、淘汰树组件、响应式页面适配、整体页面美化、最终文档与交付材料整合 |
| 陈俊皓 | @eric3685 | 技术负责人 / 文档工程师 | 负责技术路线梳理、架构文档、接口与状态流转说明、部分后端逻辑协助、项目交付文档维护 |
| 张二思 | @zhangers324 | 前端开发 | 负责 Vue 页面基础开发、部分页面实现、前端路由与布局协作 |
| 董祉含 | @dzh0628 | 后端主开发 | 负责 Django API、用户登录注册、赛事与报名接口、权限校验、赛程状态保存和数据库模型对接 |
| 路良钧 | @toki-xinyue | 数据库负责 / 测试负责人 | 负责 MySQL 表结构、初始化脚本、样例数据、数据库升级脚本、功能测试与边界测试整理 |
| 李峻安 | @lja1872 | UI 设计师 | 负责早期 UI 设计参考、界面截图素材和部分视觉方向建议 |

## 核心功能

### 参赛者

- 浏览赛事大厅，按分类、状态、关键词、赛事编号检索赛事。
- 查看赛事详情，支持公开赛事和私人邀请码赛事。
- 提交个人或战队报名，查看报名状态。
- 查看抽签与单淘汰树。
- 查看个人运动档案、积分和参赛记录。
- 使用好友搜索、好友申请、好友聊天和消息通知。

### 赛事主办方

- 创建、编辑、删除赛事。
- 选择默认缩图或上传本地缩图。
- 审核报名名单，通过、驳回、批量管理参赛者。
- 批量生成测试参赛者，可选择随机积分。
- 生成单淘汰树，处理晋级、退赛、比分录入和结果撤销。
- 开始比赛、结束比赛，并沉淀排名和积分。

### 管理员

- 审核公开赛事，通过或驳回并填写原因。
- 管理用户，支持创建、封禁、删除、批量生成和批量删除。
- 批量创建赛事、批量导入参赛者。
- 查看审核记录和平台统计。
- 通过权限校验限制普通用户访问后台功能。

## 技术亮点

- RBAC 角色权限：前端路由守卫和后端接口装饰器共同限制访问边界。
- 单淘汰树引擎：支持非 2 的幂人数、轮空位、种子选手首轮保送、节点回滚和边界场景。
- 状态流转控制：赛事、报名、赛程和积分通过后端接口统一变更，降低前端随意改状态风险。
- 通知联动：报名结果、赛事审核、好友申请和聊天未读集中进入消息中心。
- 样例数据支持：预置多角色账号和多状态赛事，便于本地验证和功能验收。

## 文档索引

| 文档 | 说明 |
| --- | --- |
| [运行指南](docs/run-guide.md) | 本地数据库、后端、前端启动步骤 |
| [功能说明](docs/feature-overview.md) | 按角色和业务流程说明系统功能 |
| [接口说明](docs/api.md) | 当前 Django API 接口摘要 |
| [数据库设计](database/database-design.md) | 当前 MySQL 表结构和状态码 |
| [淘汰树设计](docs/bracket-design.md) | 单淘汰树、种子、轮空和回滚逻辑 |
| [测试报告](docs/test/test-report.md) | 构建、Django check、功能测试和边界测试 |
| [界面截图](docs/assets/screenshots.md) | 登录、注册、赛事大厅、工作台、淘汰树等页面截图 |
| [文档审查](docs/documentation-audit.md) | 已有文档盘点与最终文档说明 |
| [最终文档](docs/final-submission/README.md) | 最终版 PDF、可编辑源文件、演示 PPT 与产品视频 |
| [历史设计资料](docs/archive/README.md) | 保留中文原名的早期设计与测试资料 |

## 完整执行指南

以下步骤用于从数据库到前后端完整运行项目。若已在本机配置好环境，也可以直接从第 4 步启动。

### 1. 克隆或进入项目

```powershell
cd "C:\Users\kenny\Desktop\軟件工程"
git clone https://github.com/kennyisccf/amateur-competition-platform.git amateur-competition-platform-git
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git"
```

如果本机已经有项目：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git"
git status --short
```

### 2. 初始化数据库

数据库使用 MySQL 8.0，数据库名为 `lesai_db`，字符集为 `utf8mb4`。

本机数据库初始化命令：

```powershell
Get-Content -Raw -Encoding UTF8 "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\database\lesai.sql" | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p "--default-character-set=utf8mb4"
```

如果数据库已存在，只需要执行升级脚本：

```powershell
Get-Content -Raw -Encoding UTF8 "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\database\upgrade_registration_fields.sql" | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p "--default-character-set=utf8mb4" lesai_db
```

### 3. 安装依赖

后端依赖：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\backend\amateur_competition_platform"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ..\requirements.txt
```

前端依赖：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\frontend"
npm.cmd ci
```

### 4. 启动后端

后端：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\backend\amateur_competition_platform"
$securePassword = Read-Host "MySQL password" -AsSecureString
$env:MYSQL_PASSWORD = [System.Net.NetworkCredential]::new("", $securePassword).Password
.\.venv\Scripts\python.exe manage.py runserver
```

后端默认地址：

```text
http://localhost:8000
```

### 5. 启动前端

另开一个 PowerShell：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\frontend"
npm.cmd run dev
```

访问地址：

```text
http://localhost:5173/
```

### 6. 完整检查

前端生产构建：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\frontend"
npm.cmd run build
```

后端系统检查：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\backend\amateur_competition_platform"
.\.venv\Scripts\python.exe manage.py check
```

Git 格式检查：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git"
git diff --check
```

### 7. 推荐验收流程

```text
普通用户登录 -> 赛事大厅 -> 赛事详情 -> 报名/通知/档案
主办方登录 -> 赛事工作台 -> 报名管理 -> 批量生成参赛者 -> 抽签与淘汰树
管理员登录 -> 审核与风控 -> 赛事审核 -> 用户管理 -> 平台统计
```

重点验证：

- 赛事大厅搜索、筛选和赛事缩图。
- 公开赛事与私人邀请码赛事。
- 报名审核、批量生成参赛者和随机积分。
- 单淘汰树、种子选手轮空、晋级和撤销。
- 好友系统、消息通知和删除好友后的通知清理。
- 管理员赛事审核、用户治理和权限边界。

## 测试账号

所有测试账号密码均为 `123456`，登录页验证码按页面显示填写。

| 角色 | 账号 | 说明 |
| --- | --- | --- |
| 管理员 | `admin` | 普通管理员 |
| 管理员 | `test_admin` | 全功能测试管理员 |
| 主办方 | `org_zs` | 赛事创建与报名管理 |
| 参赛者 | `player_mike` | 高积分选手 |
| 参赛者 | `player_jane` | 普通选手 |
| 参赛者 | `player_test` | 私人赛事测试用户 |
