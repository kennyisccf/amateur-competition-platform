# 乐赛前端说明

前端位于 `frontend/`，使用 Vue 3 + Vite + Element Plus 构建。

## 1. 技术栈

| 技术 | 用途 |
| --- | --- |
| Vue 3 Composition API | 页面与组件开发 |
| Vite | 开发服务器和生产构建 |
| Vue Router | 路由和页面权限控制 |
| Element Plus | UI 组件 |
| Axios | 请求封装 |

## 2. 主要页面

| 页面 | 文件 | 说明 |
| --- | --- | --- |
| 登录 | `src/views/Login.vue` | 验证码登录、动态背景 |
| 注册 | `src/views/Register.vue` | 注册表单、动态背景 |
| 全局布局 | `src/layout/Layout.vue` | 左侧导航、通知角标、角色菜单 |
| 赛事大厅 | `src/views/Home.vue` | 赛事搜索、筛选、卡片列表 |
| 赛事详情 | `src/views/EventDetail.vue` | 赛事信息、报名入口、邀请码 |
| 赛事报名 | `src/views/EventRegister.vue` | 个人/战队报名 |
| 创建赛事 | `src/views/CreateCompetition.vue` | 创建表单、默认缩图、本地上传 |
| 编辑赛事 | `src/views/CompetitionEdit.vue` | 编辑赛事信息和缩图 |
| 赛事工作台 | `src/views/Workbench.vue` | 赛事管理入口 |
| 报名管理 | `src/views/RegistrationManage.vue` | 审核、批量生成、批量删除 |
| 淘汰树组件 | `src/components/CompetitionBracket.vue` | 嵌入赛事详情和报名管理，负责单淘汰树可视化 |
| 好友系统 | `src/views/Friends.vue` | 搜索、申请、聊天、删除 |
| 消息通知 | `src/views/Notifications.vue` | 待办、通知、未读消息 |
| 个人档案 | `src/views/Profile.vue` | 资料、积分、报名记录 |
| 管理员审核 | `src/views/AdminReview.vue` | 赛事审核、用户管理、风控 |
| 无权限页 | `src/views/Forbidden.vue` | 越权访问提示 |

## 3. 启动

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\frontend"
npm.cmd run dev
```

访问：

```text
http://localhost:5173/
```

## 4. 构建

```powershell
npm.cmd run build
```

## 5. 前端权限说明

路由守卫位于 `src/router/index.js`：

- 未登录访问业务页面会跳转登录页。
- 已登录访问登录/注册页会跳回首页。
- 需要管理员角色的页面会检查 `localStorage.role`。
- 后端接口仍是最终权限边界，前端权限只负责用户体验和入口控制。

## 6. 通知刷新说明

通知角标由 `src/utils/notificationEvents.js` 和 `Layout.vue` 协同维护：

- 页面加载时刷新。
- 路由切换时刷新。
- 浏览器窗口重新聚焦时刷新。
- 页面从隐藏恢复可见时刷新。
- 事件触发时主动刷新。
- 短轮询兜底刷新。
