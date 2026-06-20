# 乐赛本地运行指南

本文档用于在本机启动「乐赛」前后端和 MySQL 数据库。路径以当前项目机器为准。

## 1. 环境要求

| 环境 | 建议版本 |
| --- | --- |
| Node.js | 18+ |
| Python | 3.12+ |
| Django | 6.0.5 |
| MySQL | 8.0 |
| 浏览器 | Chrome / Edge |

后端默认使用本机 MySQL 配置，必要时可通过环境变量覆盖：

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | 本地开发默认值 | Django 密钥 |
| `DJANGO_DEBUG` | `true` | 是否开启调试模式 |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | 允许访问的后端域名 |
| `DJANGO_CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | 允许跨域的前端地址 |
| `MYSQL_DATABASE` | `lesai_db` | 数据库名 |
| `MYSQL_USER` | `root` | 数据库用户名 |
| `MYSQL_PASSWORD` | 空 | 数据库密码，启动后端前通过环境变量设置 |
| `MYSQL_HOST` | `127.0.0.1` | 数据库地址 |
| `MYSQL_PORT` | `3306` | 数据库端口 |

## 2. 项目路径

```text
C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git
```

后端：

```text
C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\backend\amateur_competition_platform
```

前端：

```text
C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\frontend
```

## 3. 数据库初始化

数据库名：`lesai_db`

数据库密码不写入仓库。执行 MySQL 命令时使用 `-p` 交互输入密码；启动后端前通过环境变量提供密码。

完整初始化脚本：

```powershell
Get-Content -Raw -Encoding UTF8 "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\database\lesai.sql" | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p "--default-character-set=utf8mb4"
```

如果只执行升级脚本：

```powershell
Get-Content -Raw -Encoding UTF8 "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\database\upgrade_registration_fields.sql" | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p "--default-character-set=utf8mb4" lesai_db
```

## 4. 安装依赖

创建后端虚拟环境并安装依赖：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\backend\amateur_competition_platform"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ..\requirements.txt
```

安装前端依赖：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\frontend"
npm.cmd ci
```

## 5. 启动后端

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

## 6. 启动前端

另开一个 PowerShell：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git\frontend"
npm.cmd run dev
```

前端默认地址：

```text
http://localhost:5173/
```

## 7. 测试账号

所有账号密码均为 `123456`，验证码按登录页显示填写。

| 角色 | 账号 |
| --- | --- |
| 管理员 | `admin` |
| 管理员 | `test_admin` |
| 主办方 | `org_zs` |
| 参赛者 | `player_mike` |
| 参赛者 | `player_jane` |
| 参赛者 | `player_test` |

## 8. 常用检查命令

查看工作区状态：

```powershell
cd "C:\Users\kenny\Desktop\軟件工程\amateur-competition-platform-git"
git status --short
```

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

## 9. 常见问题

### 9.1 登录失败

- 确认密码为 `123456`。
- 确认验证码填写的是登录页当前显示值。
- 确认后端服务已启动。

### 9.2 前端无法请求后端

- 确认后端运行在 `localhost:8000`。
- 确认前端运行在 `localhost:5173`。
- 当前 Axios 使用同源代理/本地配置，开发时需要同时启动前后端。

### 9.3 数据和页面状态不一致

- 重新导入 `database/lesai.sql`。
- 确认数据库名为 `lesai_db`。
- 确认后端 settings 中数据库账号密码正确。
