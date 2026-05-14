# 乐赛平台项目运行说明

### \## 1. 环境依赖准备

\* \*\*Node.js\*\*: 建议版本 18+

\* \*\*Python\*\*: 版本 3.11

\* \*\*MySQL\*\*: 版本 8.0



### \## 2. 数据库配置 (MySQL)

1\. 启动本地 MySQL 服务，默认端口 `3306`。

2\. 创建数据库（名称可与后端配置保持一致，如 `lesai`）。

3\. 导入 `database/lesai.sql` 脚本初始化表结构和测试数据。



### \## 3. 后端运行 (Django)

1\. 进入后端目录：`cd backend`

2\. 创建并激活虚拟环境：

&#x20;  ```bash

&#x20;  python -m venv venv

&#x20;  source venv/bin/activate  # Windows 运行 venv\\Scripts\\activate

