# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 构建与运行

### 开发环境（容器内数据库 + 本地热更新）

```bash
# 启动数据库和缓存
docker-compose up -d postgres redis

# 后端（backend/ 目录）
docker-compose exec backend alembic upgrade head  # 数据库迁移
docker-compose up -d backend                       # 或通过 Docker 跑后端
# 注：Windows 上不要本地 pip install（asyncpg/pydantic-core 需 Rust/MSVC 编译）

# 前端（frontend/ 目录）
npm install    # 首次
npm run dev    # 热更新开发服务器（默认 :5173）
```

### 数据库迁移

```bash
docker-compose exec backend alembic revision --autogenerate -m "说明"
docker-compose exec backend alembic upgrade head
```

### 生产构建

```bash
docker-compose up --build -d  # 构建并启动所有服务
```

## 项目结构概要

```
instrument-booking/
├── docker-compose.yml         # PostgreSQL + Redis + Backend + Frontend
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini + alembic/ # 数据库迁移
│   ├── uploads/attachments/   # 附件文件存储（Docker volume）
│   └── app/
│       ├── main.py            # FastAPI 入口
│       ├── core/              # config, database, security, deps, redis
│       ├── models/            # SQLAlchemy ORM（User, Instrument, Booking, Notification 等）
│       ├── schemas/           # Pydantic 请求/响应
│       ├── services/          # 业务逻辑层
│       └── api/v1/            # 路由层
└── frontend/
    ├── Dockerfile + nginx.conf
    └── src/
        ├── api/               # 后端 API 调用（Axios + JWT 拦截器）
        ├── stores/            # Pinia 状态管理
        ├── router/            # Vue Router + 守卫
        ├── composables/       # 可复用组合式函数
        ├── components/        # 可复用 UI 组件
        └── views/             # 页面组件
```

## 后端分层模式（由内到外）

```
Model → Schema → Service → Router
  │        │        │         └── HTTP 入口，调用 Service，返回响应
  │        │        └──────────── 纯业务逻辑，接收 AsyncSession 作为第一参数
  │        └───────────────────── Pydantic 请求/响应格式
  └────────────────────────────── SQLAlchemy 表定义
```

- Service 函数**不依赖** Request 对象，只接收 `AsyncSession` + 参数
- Router 函数**不包含**业务逻辑
- UUID 主键一律加 `@field_serializer` 转换，datetime 同理
- relationship 使用字符串引用（`"Booking"`），避免循环导入
- Model 之间互相引用的 relationship 在**所有 Model 都定义后**再加，或直接使用字符串

## 新增功能流程

**后端**：新建 model → schema → service → 在 `api/v1/` 新建 router → 在 `api/router.py` 注册 → 生成迁移

**前端**：在 `api/` 加接口函数 → 在 `views/` 新建页面 → 在 `router/index.ts` 注册路由

## 关键注意事项

- **Windows 本地不要 `pip install`** — 编译型包无预编译 wheel 会失败。使用 Docker 运行后端
- **bcrypt 版本锁死** — `bcrypt==4.1.3`（passlib 与 bcrypt 5.x 不兼容）
- **Schema 的 UUID 序列化** — 每个 schema 需要显式加 `@field_serializer`
- **附件存储** — `backend/uploads/attachments/`，UUID 重命名，Docker volume 挂载
- **仪器图片存储** — `backend/uploads/images/`，以 `{instrument_id}.{ext}` 命名
- **站内通知** — 在 booking_service 各操作后自动创建，不依赖邮件系统
- **Model 临时字段** — Booking 模型上的 `user_username`、`user_full_name`、`instrument_name` 使用 `ClassVar` 声明，不在数据库持久化，在 `_enrich_bookings()` 中查询时填充
- **Redis 在线状态** — 使用 Redis 追踪用户在线状态（key: `online:{user_id}`, TTL: 5分钟），每次认证请求自动刷新
- **时区处理** — 数据库存储 UTC 时间，通知显示时使用 `utc_to_beijing()` 转换为北京时间
- **当前状态** — 已完成 30 项需求，详见 `HANDOVER.md`

## Git 工作流程（必须遵守）

### 每日备份规则

**每天下班前必须执行一次推送**，确保代码备份到GitHub：

```bash
# 如果有未提交的改动
git add . && git commit -m "daily: 每日备份" && git push

# 如果没有改动，也确认一下状态
git status
```

### 提交规范

每次完成一个功能或修复bug后，立即提交并推送：

```bash
git add . && git commit -m "feat: 新增xxx功能" && git push
git add . && git commit -m "fix: 修复xxx问题" && git push
git add . && git commit -m "docs: 更新xxx文档" && git push
```

### 新接手开发者入门

1. 克隆项目：`git clone https://github.com/zhangxlei/instrument-booking.git`
2. 阅读 `QUICK_START.md` 和 `HANDOVER.md`
3. 双击桌面 `启动仪器预约系统.bat` 启动项目
4. 开发前执行 `git pull` 获取最新代码
5. 开发完成后提交并推送，通知Shelley审核合并
