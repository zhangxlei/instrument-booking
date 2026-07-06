# 快速启动指南

## 你需要安装的软件

| 软件 | 用途 | 下载 |
|------|------|------|
| Docker Desktop | 运行 PostgreSQL、Redis 容器 | https://www.docker.com/products/docker-desktop/ |
| Python 3.12 | 后端开发 | https://www.python.org/downloads/ |
| Node.js 20 LTS | 前端开发 | https://nodejs.org/ |

> **Windows 注意**：安装 Docker Desktop 后确保 WSL2 已启用（Docker Desktop 首次启动会提示你安装）。

---

## 第一步：确认环境正常

打开 PowerShell 或 CMD，分别运行以下命令，确认都有输出而不是报错：

```bash
docker --version
python --version
node --version
npm --version
```

---

## 第二步：启动数据库和缓存

在项目根目录（`instrument-booking/`，也就是 docker-compose.yml 所在的目录）执行：

```bash
docker-compose up -d postgres redis
```

第一次运行会下载镜像，需要等几分钟。下载完以后，以后每次启动都很快。

验证：

```bash
docker ps
```

你应该看到 `postgres` 和 `redis` 两个容器的状态是 `Up`。

> 以后不需要数据库/缓存了就 `docker-compose stop`，不想用了就 `docker-compose down`。数据存在 Docker 卷里，`stop` 不会丢，`down -v` 会清理干净。

---

## 第三步：启动后端

```bash
cd backend

# 创建虚拟环境（只需要做一次）
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（创建表结构）
alembic upgrade head

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

验证：浏览器打开 http://localhost:8000/health，显示 `{"status":"ok"}` 即成功。

查看 API 文档：http://localhost:8000/docs（FastAPI 自动生成的 Swagger 界面）

---

## 第四步：启动前端

新开一个终端窗口：

```bash
cd frontend

# 安装依赖（只需要做一次）
npm install

# 启动开发服务器
npm run dev
```

验证：浏览器打开 http://localhost:5173，能看到登录/注册页面即成功。

---

## 第五步：创建第一个用户

方式一（推荐）：通过前端页面 http://localhost:5173/register 注册一个账号。

方式二：通过后端 Swagger UI http://localhost:8000/docs 调用 `POST /api/v1/auth/register`。

**要让这个用户成为管理员**，用管理员账号 `admin` / `admin123` 登录后，在"管理后台 → 用户管理"页面可以直接修改角色。首次使用前需通过 Docker 初始化：

```bash
docker-compose exec backend alembic upgrade head
```

管理员默认账号：
- 用户名：`admin`
- 密码：`admin123`
- 角色：`admin`（拥有全部管理权限）

---

## 日常开发流程

每次你回来继续开发时，只需要：

```bash
# 1. 启动数据库（如果没启动）
docker-compose up -d postgres redis

# 2. 启动后端（在 backend 目录）
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. 启动前端（在 frontend 目录，新开终端）
npm run dev
```

前端改代码会自动刷新浏览器，后端改代码会自动重启服务（--reload 参数）。

---

## 常见问题

**Q: Docker Desktop 报错 "WSL 2 installation is incomplete"**

A: 以管理员身份打开 PowerShell，执行 `wsl --install`，然后重启电脑。

**Q: 端口 8000 / 5432 / 6379 被占用**

A: 修改 `docker-compose.yml` 和 `frontend/vite.config.ts` 中的端口号。被占用常见原因是电脑里已经装了 PostgreSQL 或 Redis。

**Q: `alembic upgrade head` 报错**

A: 检查 `docker-compose up -d postgres` 是否成功启动了。检查 `.env` 文件中的 `DATABASE_URL` 是否正确（如果改了密码要同步改）。

**Q: `pip install` 报错 "Microsoft Visual C++ 14.0 is required"**

A: 有些包（如 asyncpg）依赖 C++ 编译工具。安装 [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)，勾选"Desktop development with C++"。

**Q: 前端 `npm install` 报错**

A: 检查 Node.js 版本是否 >= 20（`node --version`）。试试删除 `node_modules` 和 `package-lock.json`，重新 `npm install`。
