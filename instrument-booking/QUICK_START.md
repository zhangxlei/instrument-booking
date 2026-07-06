# 快速启动指南

## 你需要安装的软件

| 软件 | 用途 | 下载 |
|------|------|------|
| Docker Desktop | 运行 PostgreSQL、Redis、Backend 容器 | https://www.docker.com/products/docker-desktop/ |
| Python 3.12 | 后端开发（本地调试用） | https://www.python.org/downloads/ |
| Node.js 20 LTS | 前端开发 | https://nodejs.org/ |

> **Windows 注意**：安装 Docker Desktop 后确保 WSL2 已启用（Docker Desktop 首次启动会提示你安装）。

---

## 一键启动（推荐）

### 首次使用

1. **启动 Docker Desktop**（确保任务栏右下角有 Docker 图标）

2. **初始化数据库**（只需执行一次）：
   ```bash
   cd E:\agent\instrument_system\instrument-booking
   docker-compose up -d postgres redis backend
   docker-compose exec backend alembic upgrade head
   docker-compose exec backend pip install redis[hiredis]
   ```

3. **双击桌面快捷方式**：
   - 文件位置：`C:\Users\l\Desktop\启动仪器预约系统.bat`
   - 自动启动后端（Docker）+ 前端（npm dev）

4. **浏览器访问**：http://localhost:5173

### 日常使用

只需双击 `启动仪器预约系统.bat` 即可，无需重复初始化。

---

## 手动启动

如果你需要更精细的控制，可以按以下步骤手动启动：

### 第一步：确认环境正常

打开 PowerShell 或 CMD，分别运行以下命令，确认都有输出而不是报错：

```bash
docker --version
python --version
node --version
npm --version
```

### 第二步：启动数据库和缓存

```bash
cd E:\agent\instrument_system\instrument-booking
docker-compose up -d postgres redis
```

第一次运行会下载镜像，需要等几分钟。下载完以后，以后每次启动都很快。

验证：

```bash
docker ps
```

你应该看到 `postgres` 和 `redis` 两个容器的状态是 `Up`。

> 以后不需要数据库/缓存了就 `docker-compose stop`，不想用了就 `docker-compose down`。数据存在 Docker 卷里，`stop` 不会丢，`down -v` 会清理干净。

### 第三步：启动后端

**方式一：Docker 启动（推荐）**

```bash
cd E:\agent\instrument_system\instrument-booking
docker-compose up -d backend
```

后端代码修改会自动热更新（Docker 挂载了 volumes）。

**方式二：本地启动（调试用）**

```bash
cd E:\agent\instrument_system\instrument-booking\backend

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

> **Windows 注意**：不要在本地执行 `pip install`，编译型包（如 asyncpg）需要 Rust/MSVC 编译环境，请使用 Docker。

验证：浏览器打开 http://localhost:8000/health，显示 `{"status":"ok"}` 即成功。

查看 API 文档：http://localhost:8000/docs（FastAPI 自动生成的 Swagger 界面）

### 第四步：启动前端

新开一个终端窗口：

```bash
cd E:\agent\instrument_system\instrument-booking\frontend

# 安装依赖（只需要做一次）
npm install

# 启动开发服务器
npm run dev -- --host
```

验证：浏览器打开 http://localhost:5173，能看到登录/注册页面即成功。

---

## 创建第一个用户

方式一（推荐）：通过前端页面 http://localhost:5173/register 注册一个账号。

方式二：通过后端 Swagger UI http://localhost:8000/docs 调用 `POST /api/v1/auth/register`。

**要让这个用户成为管理员**，用管理员账号登录后，在"管理后台 → 用户管理"页面可以直接修改角色。

## 账号信息

- 超级管理员：`oeinoadmin` / `oeinoadmin`
- 普通管理员：`admin` / `admin123`（如果没被修改）
- 普通用户：需注册

---

## 日常开发流程

每次你回来继续开发时，只需要：

```bash
# 1. 启动 Docker Desktop

# 2. 双击桌面 "启动仪器预约系统.bat"
```

或者手动启动：

```bash
# 1. 启动所有服务
cd E:\agent\instrument_system\instrument-booking
docker-compose up -d

# 2. 启动前端（在 frontend 目录，新开终端）
cd frontend
npm run dev -- --host
```

前端改代码会自动刷新浏览器，后端改代码会自动重启服务（Docker 挂载了 volumes）。

---

## 常见问题

**Q: Docker Desktop 报错 "WSL 2 installation is incomplete"**

A: 以管理员身份打开 PowerShell，执行 `wsl --install`，然后重启电脑。

**Q: 端口 8000 / 5432 / 6379 被占用**

A: 修改 `docker-compose.yml` 和 `frontend/vite.config.ts` 中的端口号。被占用常见原因是电脑里已经装了 PostgreSQL 或 Redis。

**Q: `alembic upgrade head` 报错**

A: 检查 `docker-compose up -d postgres` 是否成功启动了。检查 `.env` 文件中的 `DATABASE_URL` 是否正确（如果改了密码要同步改）。

**Q: `pip install` 报错 "Microsoft Visual C++ 14.0 is required"**

A: 有些包（如 asyncpg）依赖 C++ 编译工具。请使用 Docker 启动后端，不要在本地 pip install。

**Q: 前端 `npm install` 报错**

A: 检查 Node.js 版本是否 >= 20（`node --version`）。试试删除 `node_modules` 和 `package-lock.json`，重新 `npm install`。

**Q: 双击 .bat 文件后闪退**

A: 右键 .bat 文件 → 编辑，检查路径是否正确。确保 Docker Desktop 已启动。

**Q: 如何停止所有服务**

A: 在 `instrument-booking` 目录执行 `docker-compose down`。或者直接关闭 Docker Desktop。

---

## 项目目录结构

```
E:\agent\instrument_system\instrument-booking\
├── backend/                 # Python FastAPI 后端
│   ├── app/
│   │   ├── core/            # 配置、数据库、安全、依赖、Redis
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 模型
│   │   ├── services/        # 业务逻辑层
│   │   └── api/v1/          # 路由层
│   ├── alembic/             # 数据库迁移
│   ├── uploads/             # 上传文件存储
│   ├── Dockerfile           # 后端 Docker 镜像
│   └── requirements.txt     # Python 依赖
├── frontend/                # Vue 3 + TypeScript 前端
│   ├── src/
│   │   ├── api/             # Axios API 调用
│   │   ├── components/      # UI 组件
│   │   ├── views/           # 页面组件
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   └── composables/     # 组合式函数
│   ├── Dockerfile           # 前端 Docker 镜像
│   └── nginx.conf           # Nginx 配置
├── docker-compose.yml       # Docker 编排
├── HANDOVER.md              # 项目交接文档（详细）
└── QUICK_START.md           # 快速启动指南（本文档）
```
