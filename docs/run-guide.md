## 乐赛平台本地运行指南
本文档介绍如何在本地启动「乐赛一站式全民赛事组织服务平台」的前后端及数据库。

# 一、 环境要求
前端: Node.js (推荐 v18+)

后端: Python 3.11

数据库: MySQL 8.0

# 二、 数据库配置
1.打开本地 MySQL 数据库工具（如 Navicat 或 DataGrip）。

2.执行以下命令创建数据库：

 SQL
 
 CREATE DATABASE lesai DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
 
3.导入数据库表结构：运行 database/lesai.sql 文件中的 SQL 语句。

4.核对配置：确保本地 MySQL 用户名和密码与后端配置文件一致。

# 三、 后端运行 (Django)

1.进入后端目录：

cd backend/amateur_competition_platform

2.创建并激活虚拟环境（推荐）：

   创建虚拟环境
   python -m venv venv
   
   Windows 激活:
   venv\Scripts\activate

   
3.安装依赖包：

   pip install django djangorestframework djangorestframework-simplejwt django-cors-headers mysqlclient

   如果目录下有 requirements.txt，可直接运行以下命令批量安装：
   
   pip install -r requirements.txt
   
4.配置数据库：

在 amateur_competition_platform/settings.py 中，找到 DATABASES 配置项，修改为您本地 MySQL 的真实用户名和密码。

5.数据库迁移（生成表结构）：

python manage.py makemigrations

python manage.py migrate

6.启动后端服务：

python manage.py runserver
默认后端访问地址为：http://localhost:8000

