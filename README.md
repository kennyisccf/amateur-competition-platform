# 乐赛：一站式业余赛事组织服务平台

「乐赛」是中山大学软件工程课程第 14 组的期末项目，面向校园社团、兴趣组织和大众业余赛事场景，提供赛事发现、报名审核、赛程生成、结果记录、积分档案、好友互动与消息通知的一体化平台。

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
| 当前分支 | `dev/zzf` |

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、Vite、Element Plus、Vue Router、Axios |
| 后端 | Python、Django、Session/Cookie 登录态、CSRF、验证码 |
| 数据库 | MySQL 8.0、utf8mb4、InnoDB |
| 静态资源 | 默认赛事缩图、本地上传缩图、登录/注册背景图 |

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
- 演示数据支持：预置多角色账号和多状态赛事，方便课堂现场演示。

## 文档索引

| 文档 | 说明 |
| --- | --- |
| [运行指南](docs/run-guide.md) | 本地数据库、后端、前端启动步骤 |
| [功能说明](docs/feature-overview.md) | 按角色和业务流程说明系统功能 |
| [接口说明](docs/api.md) | 当前 Django API 接口摘要 |
| [数据库设计](database/database-design.md) | 当前 MySQL 表结构和状态码 |
| [淘汰树设计](docs/bracket-design.md) | 单淘汰树、种子、轮空和回滚逻辑 |
| [测试报告](docs/test/test-report.md) | 构建、Django check、功能测试和边界测试 |
| [演示指南](docs/demo-guide.md) | 课堂展示账号、流程和重点说明 |
| [文档审查](docs/documentation-audit.md) | 已有文档盘点与最终文档说明 |

## 快速启动

后端：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\backend\amateur_competition_platform"
.\.venv\Scripts\python.exe manage.py runserver
```

前端：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\frontend"
npm.cmd run dev
```

访问地址：

```text
http://localhost:5173/
```

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

## 最终检查命令

前端构建：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\frontend"
npm.cmd run build
```

后端检查：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\backend\amateur_competition_platform"
.\.venv\Scripts\python.exe manage.py check
```
