# 实验室仪器预约系统 — 开发计划

## 项目概况

在 Docker 中开发的实验室仪器预约系统，支持仪器管理、预约审批、站内通知、附件和数据导出。

**部署方式**：开发完成后，将整个项目目录拷贝到另一台 Windows 服务器，安装 Docker Desktop，执行 `docker-compose up -d` 即可。局域网内通过 `http://<服务器IP>` 访问（80 端口，无需加端口号）。

**默认管理员账号**：用户名 `admin`，密码 `admin123`（需先执行 `docker-compose exec backend alembic upgrade head` 初始化数据库）。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + TypeScript + Pinia + Axios |
| 后端 | Python 3.12 + FastAPI + SQLAlchemy 2.0 (async) |
| 数据库 | PostgreSQL 16 (asyncpg) |
| 缓存/限流 | Redis 7 |
| 容器 | Docker Compose（Nginx + Uvicorn + PostgreSQL + Redis） |
| Excel 导出 | openpyxl |
| 文件上传 | python-multipart（仪器附件） |

---

## 项目结构

```
instrument-booking/
├── docker-compose.yml          # 一键启动所有服务
├── .env.example                # 环境变量模板
├── DEVELOPMENT_PLAN.md         # 本文件
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt        # Python 依赖
│   ├── .env                    # 环境变量（不提交）
│   ├── alembic.ini             # 数据库迁移配置
│   ├── alembic/                # 迁移脚本目录
│   │   ├── env.py
│   │   └── versions/
│   ├── uploads/                # 附件存储目录（Docker volume 挂载）
│   │   └── attachments/
│   └── app/
│       ├── __init__.py
│       ├── main.py             # 应用入口：FastAPI 实例、CORS、lifespan
│       ├── core/               # 核心配置
│       │   ├── config.py       # Pydantic Settings（所有环境变量）
│       │   ├── database.py     # SQLAlchemy async engine + session 工厂
│       │   ├── security.py     # JWT 生成/验证、密码哈希
│       │   └── deps.py         # 依赖注入：get_current_user、require_admin
│       ├── models/             # SQLAlchemy ORM 模型
│       │   ├── base.py         # Base + TimestampMixin
│       │   ├── user.py
│       │   ├── instrument.py
│       │   ├── instrument_attachment.py
│       │   ├── booking.py
│       │   └── notification.py
│       ├── schemas/            # Pydantic 请求/响应模型
│       │   ├── common.py       # MessageResponse、PaginatedResponse
│       │   ├── auth.py         # Login、Register、Token
│       │   ├── user.py
│       │   ├── instrument.py
│       │   ├── attachment.py
│       │   ├── booking.py
│       │   └── notification.py
│       ├── services/           # 业务逻辑层（所有数据库操作在此）
│       │   ├── auth_service.py
│       │   ├── user_service.py
│       │   ├── instrument_service.py
│       │   ├── booking_service.py
│       │   ├── notification_service.py
│       │   └── export_service.py
│       └── api/                # 路由层
│           ├── router.py       # 聚合所有子路由
│           └── v1/
│               ├── auth.py
│               ├── users.py
│               ├── instruments.py
│               ├── bookings.py
│               ├── admin.py
│               └── notifications.py
│
└── frontend/
    ├── Dockerfile              # 多阶段构建：npm build + nginx
    ├── nginx.conf              # SPA 路由 + /api 反向代理
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts          # 开发代理到 backend:8000
    ├── index.html
    └── src/
        ├── main.ts
        ├── App.vue
        ├── router/
        │   └── index.ts        # 路由定义 + 守卫
        ├── api/                # 后端 API 调用
        │   ├── client.ts       # Axios 实例（JWT 拦截器、401 刷新）
        │   ├── auth.ts
        │   ├── instruments.ts
        │   ├── bookings.ts
        │   ├── admin.ts
        │   └── notifications.ts
        ├── stores/
        │   └── auth.ts         # Pinia：用户登录状态管理
        ├── composables/        # 可复用逻辑
        │   ├── useAuth.ts
        │   ├── usePagination.ts
        │   └── useNotification.ts
        ├── components/
        │   ├── layout/         # AppNavbar、AppSidebar、AppLayout、AdminLayout
        │   ├── common/         # LoadingSpinner、Pagination、ConfirmDialog、EmptyState、ErrorAlert、StatusBadge
        │   ├── auth/           # LoginForm、RegisterForm
        │   ├── instruments/    # InstrumentCard、InstrumentForm、InstrumentFilters
        │   ├── bookings/       # BookingForm、BookingCard、BookingCalendar
        │   ├── admin/          # StatsCards、BookingApprovalTable、UserTable、ExportButton
        │   └── notifications/  # NotificationBell、NotificationList
        └── views/
            ├── auth/           # LoginView、RegisterView
            ├── instruments/    # InstrumentListView、InstrumentDetailView
            ├── bookings/       # MyBookingsView、BookingDetailView
            ├── admin/          # AdminDashboard、AdminInstruments、AdminBookings、AdminUsers
            └── NotFoundView.vue
```

---

## 数据库设计

### users（用户表）

| 列 | 类型 | 约束 | 说明 |
|----|------|------|------|
| id | UUID | PK | 自动生成 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 用于登录 |
| username | VARCHAR(100) | UNIQUE, NOT NULL | |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt 哈希 |
| full_name | VARCHAR(200) | NOT NULL | 真实姓名 |
| phone | VARCHAR(50) | NULLABLE | |
| role | ENUM('admin','user') | NOT NULL, DEFAULT 'user' | 角色 |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 软禁用 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

### instruments（仪器表）

| 列 | 类型 | 约束 | 说明 |
|----|------|------|------|
| id | UUID | PK | |
| name | VARCHAR(200) | NOT NULL | 仪器名称 |
| description | TEXT | NULLABLE | 仪器描述 |
| location | VARCHAR(255) | NULLABLE | 存放位置 |
| category | VARCHAR(100) | NULLABLE | 分类 |
| image_url | VARCHAR(500) | NULLABLE | 图片 URL |
| status | ENUM('available','maintenance','retired') | NOT NULL, DEFAULT 'available' | |
| requires_approval | BOOLEAN | NOT NULL, DEFAULT TRUE | 是否需要管理员审批 |
| max_booking_duration_minutes | INTEGER | NOT NULL, DEFAULT 120 | 单次最大预约时长 |
| min_notice_minutes | INTEGER | NOT NULL, DEFAULT 60 | 最少提前多久预约 |
| cleanup_time_minutes | INTEGER | NOT NULL, DEFAULT 15 | 两段预约间的缓冲时间 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

### instrument_attachments（仪器附件表）

| 列 | 类型 | 约束 | 说明 |
|----|------|------|------|
| id | UUID | PK | |
| instrument_id | UUID | FK → instruments, ON DELETE CASCADE | 所属仪器 |
| filename | VARCHAR(500) | NOT NULL | 服务器存储的文件名（UUID 重命名） |
| original_filename | VARCHAR(500) | NOT NULL | 用户上传时的原始文件名 |
| file_size | INTEGER | NOT NULL | 文件大小（字节） |
| file_type | VARCHAR(100) | NULLABLE | MIME 类型 |
| uploaded_by | UUID | FK → users, NOT NULL | 上传者 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

### bookings（预约表）

| 列 | 类型 | 约束 | 说明 |
|----|------|------|------|
| id | UUID | PK | |
| user_id | UUID | FK → users, NOT NULL | 预约人 |
| instrument_id | UUID | FK → instruments, NOT NULL | 预约的仪器 |
| start_time | TIMESTAMPTZ | NOT NULL | |
| end_time | TIMESTAMPTZ | NOT NULL | CHECK: end_time > start_time |
| status | ENUM('pending','approved','rejected','cancelled','completed') | NOT NULL, DEFAULT 'pending' | |
| purpose | TEXT | NULLABLE | 使用目的 |
| notes | TEXT | NULLABLE | 备注 |
| approved_by | UUID | FK → users, NULLABLE | 审批人 |
| approved_at | TIMESTAMPTZ | NULLABLE | 审批时间 |
| rejection_reason | VARCHAR(500) | NULLABLE | 拒绝原因 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

### notifications（站内通知表）

| 列 | 类型 | 约束 | 说明 |
|----|------|------|------|
| id | UUID | PK | |
| user_id | UUID | FK → users, NOT NULL | 接收者 |
| type | ENUM('booking_pending','booking_approved','booking_rejected','booking_cancelled') | NOT NULL | |
| title | VARCHAR(200) | NOT NULL | |
| message | TEXT | NOT NULL | |
| is_read | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| related_booking_id | UUID | FK → bookings, NULLABLE | 关联预约 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | |

---

## API 端点

所有接口前缀 `/api/v1`。

### 认证（auth）

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | /auth/register | 否 | 注册新用户（直接激活） |
| POST | /auth/login | 否 | 登录，返回 access_token + refresh_token |
| POST | /auth/refresh | 否 | 用 refresh_token 换新 access_token |
| GET | /auth/me | 是 | 获取当前用户信息 |
| PUT | /auth/me | 是 | 更新个人信息（姓名、电话） |
| PUT | /auth/me/password | 是 | 修改密码 |

### 仪器（instruments）

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | /instruments | 否 | 仪器列表（支持 category/status/search 筛选，分页） |
| GET | /instruments/{id} | 否 | 仪器详情 |
| GET | /instruments/{id}/availability | 是 | 查询可用时段（参数：date, days） |
| POST | /instruments | 管理员 | 创建仪器 |
| PUT | /instruments/{id} | 管理员 | 更新仪器 |
| DELETE | /instruments/{id} | 管理员 | 删除仪器 |
| POST | /instruments/{id}/attachments | 管理员 | 上传附件 |
| GET | /instruments/{id}/attachments | 否 | 列出仪器附件 |
| GET | /instruments/{id}/attachments/{aid} | 否 | 下载附件 |
| DELETE | /instruments/{id}/attachments/{aid} | 管理员 | 删除附件 |

### 预约（bookings）

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | /bookings | 是 | 我的预约列表（可筛选 status、日期范围） |
| GET | /bookings/{id} | 是 | 预约详情（仅限本人） |
| POST | /bookings | 是 | 创建预约（冲突检测 → 409） |
| PUT | /bookings/{id} | 是 | 修改预约（仅 pending 状态） |
| DELETE | /bookings/{id} | 是 | 取消预约 |

### 管理后台（admin）

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | /admin/bookings | 管理员 | 所有预约列表（支持多条件筛选，分页） |
| PUT | /admin/bookings/{id}/approve | 管理员 | 批准预约 |
| PUT | /admin/bookings/{id}/reject | 管理员 | 拒绝预约（请求体含 reason） |
| GET | /admin/dashboard/stats | 管理员 | 仪表盘统计 |
| GET | /admin/export/bookings | 管理员 | 导出预约为 Excel（支持筛选参数） |
| GET | /admin/export/instruments | 管理员 | 导出仪器列表为 Excel |

### 通知（notifications）

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | /notifications | 是 | 我的通知列表（分页） |
| PUT | /notifications/{id}/read | 是 | 标记单条已读 |
| PUT | /notifications/read-all | 是 | 全部标记已读 |
| GET | /notifications/unread-count | 是 | 未读数量 |

---

## Docker 配置

### docker-compose.yml 服务一览

```
服务        镜像              端口映射      说明
──────────────────────────────────────────────────────
postgres    postgres:16-alpine  5432:5432    数据库（持久化卷 pgdata）
redis       redis:7-alpine      6379:6379    缓存（持久化卷 redisdata）
backend     本地构建 Dockerfile  8000:8000    FastAPI + Uvicorn（--reload 热更新）
frontend    本地构建 Dockerfile  80:80       Nginx 提供前端 + API 反向代理
```

### Docker 卷

| 卷名 | 挂载路径 | 用途 |
|------|----------|------|
| pgdata | /var/lib/postgresql/data | 数据库持久化 |
| redisdata | /data | Redis 持久化 |
| uploads | backend/./uploads:/app/uploads | 附件文件持久化 |

### 关键环境变量（.env）

```
DATABASE_URL=postgresql+asyncpg://app:changeme@postgres:5432/instrument_booking
REDIS_URL=redis://redis:6379/0
SECRET_KEY=<随机生成的 32 位以上密钥>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173,http://localhost
```

---

## 开发步骤

按顺序执行，每步完成后验证通过再进行下一步。

---

### 第一步：后端脚手架 + Docker 启动

**要创建的文件**：
- `docker-compose.yml`（postgres + redis 两个服务）
- `backend/Dockerfile`
- `backend/.env`
- `backend/app/__init__.py`
- `backend/app/main.py`（最小 FastAPI 应用，含健康检查端点 `GET /health`）
- `backend/app/core/__init__.py`
- `backend/app/core/config.py`（Pydantic Settings）
- `backend/app/core/database.py`（create_async_engine + async_sessionmaker + get_db）

**验证方式**：
```bash
# 启动基础服务
docker-compose up -d postgres redis
# 进入 backend 目录
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# 浏览器打开 http://localhost:8000/health → 返回 200 OK
```

---

### 第二步：用户认证 + 数据库迁移

**要创建的文件**：
- `backend/app/models/__init__.py`
- `backend/app/models/base.py`
- `backend/app/models/user.py`
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/auth.py`
- `backend/app/schemas/user.py`
- `backend/app/schemas/common.py`
- `backend/app/core/security.py`（create_access_token + verify_password + hash_password）
- `backend/app/core/deps.py`（get_current_user + require_admin）
- `backend/app/services/__init__.py`
- `backend/app/services/auth_service.py`
- `backend/app/api/__init__.py`
- `backend/app/api/router.py`
- `backend/app/api/v1/__init__.py`
- `backend/app/api/v1/auth.py`
- `alembic.ini` + `alembic/env.py`（配置 async 模式）
- `alembic/versions/001_create_users.py`（自动生成）

**验证方式**：
```
POST /api/v1/auth/register → 201，用户创建成功
POST /api/v1/auth/login    → 200，返回 access_token
GET  /api/v1/auth/me       → 200，返回当前用户信息（需要 Bearer Token）
```

---

### 第三步：前端脚手架 + 登录注册

**要创建的文件**：
- `frontend/package.json`
- `frontend/vite.config.ts`（配置 /api 代理到 localhost:8000）
- `frontend/tsconfig.json`
- `frontend/index.html`
- `frontend/src/main.ts`
- `frontend/src/App.vue`
- `frontend/src/api/client.ts`（Axios 实例，自动附加 JWT，401 刷新）
- `frontend/src/api/auth.ts`（login, register, getMe）
- `frontend/src/stores/auth.ts`（Pinia：登录状态 + token 持久化）
- `frontend/src/router/index.ts`（路由守卫：未登录 → /login，已登录 → /）
- `frontend/src/components/common/LoadingSpinner.vue`
- `frontend/src/components/common/ErrorAlert.vue`
- `frontend/src/components/layout/AppLayout.vue`
- `frontend/src/components/layout/AppNavbar.vue`
- `frontend/src/components/auth/LoginForm.vue`
- `frontend/src/components/auth/RegisterForm.vue`
- `frontend/src/views/auth/LoginView.vue`
- `frontend/src/views/auth/RegisterView.vue`
- `frontend/Dockerfile`（多阶段：npm build → nginx）
- `frontend/nginx.conf`（SPA + /api 反向代理）

**验证方式**：
```bash
cd frontend
npm install
npm run dev
# 浏览器打开 http://localhost:5173
# 注册 → 登录 → 跳转首页 → 刷新页面仍保持登录状态
# 未登录访问 / → 自动跳转到 /login
```

---

### 第四步：仪器模型 + API + 附件

**要创建的文件**：
- `backend/app/models/instrument.py`
- `backend/app/models/instrument_attachment.py`
- `backend/app/schemas/instrument.py`
- `backend/app/schemas/attachment.py`
- `backend/app/services/instrument_service.py`（CRUD + 可用时段查询 + 附件管理）
- `backend/app/api/v1/instruments.py`（仪器 CRUD + 附件上传/列表/下载/删除）
- `alembic/versions/002_create_instruments.py`

**附件存储规则**：
- 上传文件重命名为 `{UUID}.{ext}` 存入 `backend/uploads/attachments/`
- 数据库中记录原始文件名、文件大小、MIME 类型
- 下载时使用原始文件名返回

**验证方式**：
- Swagger UI 中 CRUD 仪器、上传附件、下载附件全部正常
- `GET /instruments` 支持 ?category=&status=&search= 筛选

---

### 第五步：前端仪器列表 + 详情

**要创建的文件**：
- `frontend/src/api/instruments.ts`
- `frontend/src/components/common/EmptyState.vue`
- `frontend/src/components/common/Pagination.vue`
- `frontend/src/components/instruments/InstrumentCard.vue`
- `frontend/src/components/instruments/InstrumentFilters.vue`
- `frontend/src/views/instruments/InstrumentListView.vue`
- `frontend/src/views/instruments/InstrumentDetailView.vue`

**验证方式**：
- 仪器列表页面正常展示，支持分类/状态筛选和搜索
- 点击仪器卡片进入详情页，展示仪器完整信息

---

### 第六步：前端仪器管理（管理员）

**要创建的文件**：
- `frontend/src/components/layout/AdminLayout.vue`
- `frontend/src/components/layout/AppSidebar.vue`
- `frontend/src/components/instruments/InstrumentForm.vue`（含附件上传区域）
- `frontend/src/views/admin/AdminInstrumentsView.vue`
- `frontend/src/views/admin/AdminInstrumentFormView.vue`
- 更新 `router/index.ts`：添加 /admin 路由组（requireAdmin 守卫）

**验证方式**：
- 管理员登录 → 侧边栏出现管理入口
- 新增/编辑仪器，上传附件 → 成功
- 仪器详情页显示附件列表，可下载
- 非管理员访问 /admin → 显示无权限提示

---

### 第七步：预约模型 + 创建/取消 API

**要创建的文件**：
- `backend/app/models/booking.py`
- `backend/app/schemas/booking.py`
- `backend/app/services/booking_service.py`（create_booking、cancel_booking、冲突检测）
- `backend/app/api/v1/bookings.py`
- `alembic/versions/003_create_bookings.py`

**冲突检测逻辑**：
1. 查询同一仪器、相同时段内（start_time 到 end_time 区间重叠）的所有 pending/approved 预约
2. 排除该仪器的维护时间段
3. 有重叠 → 返回 409，附带冲突的预约信息
4. 仪器设置了 requires_approval → 新预约状态为 pending，否则直接 approved

**验证方式**：
```
POST /bookings 创建预约 → 201
POST /bookings 重叠时段再次创建 → 409 Conflict
DELETE /bookings/{id} → 200，状态变为 cancelled
```

---

### 第八步：审批工作流 API

**要创建/修改的文件**：
- `backend/app/services/booking_service.py` — 增加 approve_booking、reject_booking
- `backend/app/schemas/booking.py` — 增加 BookingRejectRequest
- `backend/app/api/v1/admin.py` — 审批端点 + dashboard 统计端点
- 更新 `backend/app/api/router.py` — 注册 admin 路由

**审批流程**：
```
批准：status → 'approved', approved_by → admin_id, approved_at → now()
拒绝：status → 'rejected', approved_by → admin_id, rejection_reason → 请求体中的 reason
```

**验证方式**：
- 管理员 PUT /admin/bookings/{id}/approve → 状态变为 approved
- 管理员 PUT /admin/bookings/{id}/reject（带 reason）→ 状态变为 rejected

---

### 第九步：前端预约流程 + 管理审批

**要创建的文件**：
- `frontend/src/api/bookings.ts`
- `frontend/src/api/admin.ts`
- `frontend/src/components/common/ConfirmDialog.vue`
- `frontend/src/components/common/StatusBadge.vue`
- `frontend/src/components/bookings/BookingForm.vue`（日期 + 时段选择）
- `frontend/src/components/bookings/BookingCalendar.vue`
- `frontend/src/components/bookings/BookingCard.vue`
- `frontend/src/views/bookings/MyBookingsView.vue`（按状态 Tab 筛选）
- `frontend/src/views/bookings/BookingDetailView.vue`
- `frontend/src/components/admin/BookingApprovalTable.vue`
- `frontend/src/views/admin/AdminBookingsView.vue`

**预约表单流程**：
1. 选择日期 → 调用 /instruments/{id}/availability 获取可用时段
2. 用户选择时段 → 填写使用目的 → 提交
3. 冲突 → 显示错误提示
4. 成功 → 跳转到"我的预约"页面

**审批页面流程**：
1. 管理员看到"待审批"标签页，列出所有 pending 预约
2. 点击"批准" → 确认对话框 → 批准
3. 点击"拒绝" → 输入理由 → 确认对话框 → 拒绝

**验证方式**：
- 完整流程：用户预约 → 管理员审批 → 状态实时更新

---

### 第十步：站内通知

**要创建的文件**：
- `backend/app/models/notification.py`
- `backend/app/schemas/notification.py`
- `backend/app/services/notification_service.py`
- `backend/app/api/v1/notifications.py`
- `alembic/versions/004_create_notifications.py`
- 更新 booking_service.py：创建/审批/拒绝/取消预约时自动创建通知

**验证方式**：
```
GET /notifications → 返回通知列表
GET /notifications/unread-count → 返回未读数量
PUT /notifications/{id}/read → 标记已读
```

---

### 第十一步：前端通知系统

**要创建的文件**：
- `frontend/src/api/notifications.ts`
- `frontend/src/composables/useNotification.ts`（定时轮询未读数，间隔 30 秒）
- `frontend/src/components/notifications/NotificationBell.vue`（铃铛图标 + 未读数角标）
- `frontend/src/components/notifications/NotificationList.vue`（下拉菜单）
- 更新 AppNavbar.vue：加入 NotificationBell

**验证方式**：
- 触发通知 → 铃铛角标数字更新
- 点击铃铛 → 下拉列表显示通知
- 点击通知项 → 标记已读 + 跳转到相关预约

---

### 第十二步：管理仪表盘

**要创建/修改的文件**：
- `backend/app/api/v1/admin.py` — 完善 GET /dashboard/stats 返回数据
- `frontend/src/components/admin/StatsCards.vue`
- `frontend/src/views/admin/AdminDashboardView.vue`

**统计指标**：
- 仪器总数、今日活跃预约数、待审批数、用户总数
- 各状态预约数量分布
- 热门仪器 TOP5（按预约次数）

**验证方式**：仪表盘数据与数据库中实际数据一致

---

### 第十三步：仪器维护管理

**要创建/修改的文件**：
- `backend/app/models/instrument.py` — 增加 InstrumentMaintenance 模型
- `backend/app/schemas/instrument.py` — 增加维护相关 schema
- `backend/app/api/v1/admin.py` — 增加维护 CRUD 端点
- `backend/app/services/instrument_service.py` — 维护逻辑（冲突检测纳入维护期）
- 前端维护界面（页面或弹窗）

**验证方式**：
- 安排维护时段 → 该时段内无法预约
- 维护期间仪器状态显示为 maintenance
- 维护结束后恢复正常

---

### 第十四步：数据导出 Excel

**要创建/修改的文件**：
- `backend/requirements.txt` — 增加 `openpyxl`
- `backend/app/services/export_service.py` — 生成 .xlsx
- `backend/app/api/v1/admin.py` — 导出端点
- 前端 AdminBookingsView 和 AdminInstrumentsView — 添加"导出 Excel"按钮

**导出功能**：
- 预约导出：支持按日期范围、仪器、状态筛选，导出列包括（预约人、仪器、开始时间、结束时间、状态、目的、备注）
- 仪器导出：导出列包括（名称、分类、位置、状态、创建时间）
- 以 StreamingResponse 返回，Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

**验证方式**：
- 筛选条件 → 点击导出 → 下载 .xlsx → 用 Excel 打开检查数据正确

---

### 第十五步：Docker 存储卷 + 部署校验

**要创建/修改的文件**：
- `docker-compose.yml` — 增加 uploads 卷挂载配置
- 确认以下持久化卷配置完整：
  - pgdata → 数据库不丢失
  - redisdata → 缓存可恢复
  - ./backend/uploads → 附件不丢失

**验证方式**：
```bash
docker-compose down
docker-compose up -d
# 验证：之前的数据、附件全部保留
```

---

### 第十六步：缓存、限流、错误处理、Docker 收尾

**后端**：
- Redis 登录限流：同一 IP 每分钟最多 5 次登录尝试
- 仪器列表 Redis 缓存：TTL 60 秒
- 请求 ID 中间件（便于日志追踪）

**前端**：
- 全局 axios 错误拦截器：429（限流提示）、403（权限不足）、500（服务器错误）
- refresh_token 过期 → 清除登录状态 → 跳转登录页
- 列表页加载骨架屏（Skeleton Loading）
- 页面切换过渡动画

**Docker**：
- 完整 `docker-compose up --build` 测试
- 健康检查端点（backend: /health, frontend: Nginx 返回 200）

**最终验收**：
```bash
# 1. 清理并全新构建
docker-compose down -v
docker-compose up --build -d

# 2. 功能验收清单
#    □ 注册 → 登录 → 首页
#    □ 浏览仪器列表 → 查看详情
#    □ 创建预约 → 冲突检测（409）
#    □ 管理员审批 → 预约状态更新
#    □ 通知铃铛显示未读数，点击查看通知
#    □ 上传仪器附件 → 下载 → 删除
#    □ 导出预约/仪器 Excel → 用 Excel 打开检查
#    □ 非管理员访问 /admin 被拦截
#    □ docker-compose down && up → 数据不丢失
```

---

## V2 功能改进（2026-07-03）

### V2 改动清单

| # | 内容 | 涉及范围 |
|---|------|----------|
| 1 | **认证改造**：注册/登录去掉邮箱字段，改为用户名+密码+姓名；去掉手机号；后端自动生成占位邮箱 | schemas/auth.py, services/auth_service.py, api/v1/auth.py, schemas/user.py + 前端 LoginForm, RegisterForm, types.ts |
| 2 | **移除分类(category)**：从后端到前端完全移除 | schemas/instrument.py, services/instrument_service.py, api/v1/instruments.py, export_service.py + 前端 InstrumentCard, Filters, Form, AdminInstrumentsView, ListView |
| 3 | **移除单次最长**：从 schema 和前端移除，数据库列保留 | schemas/instrument.py + 前端 InstrumentForm |
| 4 | **计费功能(price_per_hour)**：数据库加字段、迁移、模型、schema、前端显示 | models/instrument.py, 迁移 a1b2c3d4e5f6, schemas/instrument.py + 前端 InstrumentForm, Card, DetailView |
| 5 | **仪器图片上传**：后端上传/删除 API，`/uploads/images/` 存储，静态文件挂载 | api/v1/instruments.py, main.py + 前端 InstrumentForm |
| 6 | **仪器卡片显示图片**：卡片左侧缩略图或占位 SVG | 前端 InstrumentCard.vue |
| 7 | **预约日历重做**：可视化日历网格，点选/Shift 连选/跨天选择，已约时段灰色+显示用户名，进页面直接显示，底部填写目的提交 | api/v1/instruments.py (availability 改造), schemas/booking.py (BookingUpdate), services/booking_service.py (update_booking), api/v1/bookings.py (PUT) + 前端 BookingCalendar.vue 重写, InstrumentDetailView.vue 重写 |
| 8 | **仪表盘可点击**：四个统计卡片跳转到对应管理页 | 前端 StatsCards.vue, AdminDashboardView.vue |
| 9 | **预约管理显示用户信息**：BookingRead 增加 user_username/user_full_name/instrument_name，查询时 JOIN User/Instrument 表填充 | schemas/booking.py, models/booking.py (ClassVar), services/booking_service.py (_enrich_bookings) + 前端 AdminBookingsView, BookingApprovalTable |
| 10 | **用户管理页面**：列表/新增/改角色/启用禁用/删除 | api/v1/admin.py (5 个新端点), services/booking_service.py + 前端 AdminUsersView.vue (新建), router/index.ts, AppSidebar.vue |
| 11 | **管理员改期/取消/代预约**：后端 reschedule/cancel/create API + 前端弹窗 | api/v1/admin.py, services/booking_service.py (admin_reschedule/cancel/create) + 前端 AdminBookingsView (改期/取消弹窗+代预约弹窗) |
| 12 | **付费价格显示**：预约时根据所选时段和 price_per_hour 显示预估费用 | 前端 BookingCalendar.vue (estimatedCost 计算) |

### V2 新增迁移

- `a1b2c3d4e5f6_add_price_per_hour.py` — instruments 表增加 `price_per_hour` 列

### V2 新增前端页面

- `views/admin/AdminUsersView.vue` — 用户管理页面

---

## 关键架构决策

1. **异步 SQLAlchemy** — 所有数据库操作使用 await，需 async_sessionmaker
2. **Service 层模式** — 业务逻辑在 services 中，API 层只做路由转发，service 函数接收 AsyncSession 作为第一参数
3. **前端状态** — Pinia 管理 auth 状态，其他页面级状态用 composable
4. **附件存储** — 本地文件系统，UUID 重命名防冲突，Docker volume 持久化
5. **角色权限** — admin 和 user 两个角色，API 层通过 require_admin 依赖控制

## 部署到另一台服务器

1. 将整个 `instrument-booking` 目录拷贝到目标 Windows 服务器
2. 目标服务器安装 Docker Desktop
3. 复制 `.env.example` 为 `.env`，修改 SECRET_KEY
4. 执行 `docker-compose up -d`
5. 局域网内其他电脑浏览器访问 `http://<服务器IP>` 即可
6. 附件文件在 `backend/uploads/` 目录下，备份时一并拷贝
