# 系统架构说明

## 整体架构

```
浏览器 ──HTTP──> Nginx (:80)
                    ├── / ──────────> 前端静态文件 (Vue SPA)
                    └── /api/v1/ ──> 后端 FastAPI (:8000)
                                        ├── PostgreSQL (:5432)
                                        └── Redis (:6379)
```

- **前端**：Vue 3 SPA，通过 Nginx 反向代理调用后端 API
- **后端**：FastAPI + SQLAlchemy async，按 `model → schema → service → router` 分层
- **数据库**：PostgreSQL 16，通过 Alembic 管理迁移

---

## 后端架构（`backend/app/`）

### 目录结构

```
app/
├── main.py              # 应用入口：FastAPI 实例、CORS、中间件
├── core/                # 核心基础设施
│   ├── config.py        # Pydantic Settings（所有配置项集中管理）
│   ├── database.py      # SQLAlchemy async engine + session 工厂
│   ├── security.py      # JWT 生成/验证、密码哈希
│   ├── deps.py          # 依赖注入（get_current_user、require_admin）
│   └── rate_limiter.py  # 登录限流中间件
│
├── models/              # SQLAlchemy ORM 模型（数据库表定义）
│   ├── base.py          # Base + TimestampMixin（所有模型继承）
│   ├── user.py
│   ├── instrument.py
│   ├── instrument_attachment.py
│   ├── booking.py
│   └── notification.py
│
├── schemas/             # Pydantic 模型（API 请求/响应定义）
│   ├── common.py        # MessageResponse、PaginatedResponse
│   ├── auth.py          # Login、Register、Token
│   ├── user.py
│   ├── instrument.py
│   ├── attachment.py
│   ├── booking.py
│   └── notification.py
│
├── services/            # 业务逻辑层（所有数据库操作在此）
│   ├── auth_service.py
│   ├── instrument_service.py
│   ├── booking_service.py
│   ├── notification_service.py
│   └── export_service.py
│
└── api/
    ├── router.py        # 聚合所有子路由
    └── v1/              # API v1 路由层（只做请求分发）
        ├── auth.py
        ├── instruments.py
        ├── bookings.py
        ├── admin.py
        └── notifications.py
```

### 分层职责（从内到外）

```
Model → Schema → Service → Router
  │        │        │         │
  │        │        │         └── HTTP 请求入口，验证参数，调用 Service，返回响应
  │        │        └──────────── 纯业务逻辑，接收 AsyncSession 作为第一参数
  │        └───────────────────── 请求/响应数据格式定义
  └────────────────────────────── 数据库表结构定义
```

**关键规则**：
- Service 层**不依赖** Request 对象，只接收 `AsyncSession` + 参数，方便测试
- Router 层**不包含**业务逻辑，只做参数提取和响应返回
- Model 只定义表结构和关系，**不包含**业务逻辑
- 所有依赖通过 FastAPI 的 `Depends()` 注入

### 数据流示例（创建预约）

```
1. 前端 POST /api/v1/bookings
2. Router (bookings.py) 接收请求
3. Depends(get_db) → 创建 AsyncSession
4. Depends(get_current_user) → 解析 JWT → 获取 User
5. 调用 booking_service.create_booking(db, user_id, data)
6. Service 内部：
   a. 查询 Instrument 是否存在
   b. 检查冲突（booking + maintenance）
   c. 创建 Booking 记录
   d. 创建 Notification 记录
   e. 返回 Booking ORM 对象
7. Router 返回响应 → Pydantic 自动序列化为 JSON
```

---

## 前端架构（`frontend/src/`）

### 目录结构

```
src/
├── main.ts              # 入口：注册 Pinia + Router
├── App.vue              # 根组件（自动加载用户信息）
├── types.ts             # TypeScript 类型定义
│
├── api/                 # 后端 API 调用层
│   ├── client.ts        # Axios 实例（JWT 拦截器、401 刷新）
│   ├── auth.ts
│   ├── instruments.ts
│   ├── bookings.ts
│   ├── admin.ts
│   └── notifications.ts
│
├── stores/              # Pinia 全局状态
│   └── auth.ts          # 用户登录状态 + token 持久化
│
├── router/
│   └── index.ts         # 路由定义 + 守卫（auth guard + admin guard）
│
├── composables/         # 可复用组合式函数
│   └── useNotification.ts  # 未读通知轮询
│
├── components/          # 可复用组件
│   ├── layout/          # AppNavbar、AppSidebar、AppLayout、AdminLayout
│   ├── common/          # LoadingSpinner、Pagination、ConfirmDialog、EmptyState、ErrorAlert、StatusBadge
│   ├── auth/            # LoginForm、RegisterForm
│   ├── instruments/     # InstrumentCard、InstrumentForm、InstrumentFilters
│   ├── bookings/        # BookingForm、BookingCalendar
│   ├── admin/           # StatsCards、BookingApprovalTable
│   └── notifications/   # NotificationBell、NotificationList
│
└── views/               # 页面级组件（关联路由）
    ├── auth/            # LoginView、RegisterView
    ├── instruments/     # InstrumentListView、InstrumentDetailView
    ├── bookings/        # MyBookingsView、BookingDetailView
    └── admin/           # AdminDashboard、AdminInstruments、AdminInstrumentForm、AdminBookings
```

### 页面路由

| 路径 | 组件 | 说明 | 权限 |
|------|------|------|------|
| /login | LoginView | 登录 | 游客 |
| /register | RegisterView | 注册 | 游客 |
| /instruments | InstrumentListView | 仪器列表 | 登录 |
| /instruments/:id | InstrumentDetailView | 仪器详情 + 预约 | 登录 |
| /bookings | MyBookingsView | 我的预约 | 登录 |
| /bookings/:id | BookingDetailView | 预约详情 | 登录 |
| /admin | AdminDashboardView | 仪表盘 | 管理员 |
| /admin/instruments | AdminInstrumentsView | 仪器管理 | 管理员 |
| /admin/instruments/new | AdminInstrumentFormView | 新增仪器 | 管理员 |
| /admin/instruments/:id/edit | AdminInstrumentFormView | 编辑仪器 | 管理员 |
| /admin/bookings | AdminBookingsView | 预约管理 | 管理员 |

### 数据流示例

```
1. 组件 mounted → 调用 api 函数（如 getInstruments()）
2. api/client.ts 的 Axios 拦截器自动附加 JWT token
3. 后端处理 → 返回 JSON
4. 组件接收数据 → 响应式更新模板
5. 401 错误时 → 拦截器自动尝试 refresh token
6. refresh 也失败 → 清除登录态 → 跳转 /login
```

---

## 数据库表关系

```
users
  ├── bookings (user_id) ── 用户的预约
  ├── bookings (approved_by) ── 管理员审批的预约
  ├── notifications (user_id) ── 用户的通知
  └── instrument_attachments (uploaded_by) ── 用户上传的附件

instruments
  ├── bookings (instrument_id) ── 仪器的预约记录
  ├── instrument_attachments (instrument_id) ── 仪器的附件
  └── instrument_maintenance (instrument_id) ── 仪器的维护计划

bookings
  └── notifications (related_booking_id) ── 预约相关的通知
```

---

## 关键架构决策

1. **异步 SQLAlchemy** — 所有数据库操作用 `await`，使用 `create_async_engine` + `async_sessionmaker`
2. **Service 层模式** — services 中的函数接收 `AsyncSession` 作为第一参数，不依赖 request，可单独测试
3. **字符串引用关系** — Model 之间的 relationship 使用字符串（如 `"Booking"`），避免循环导入
4. **UUID 主键** — 所有表使用 UUID 主键，`server_default=func.gen_random_uuid()`
5. **`from_attributes` + `field_serializer`** — Pydantic schema 使用 `from_attributes=True` 配合 `@field_serializer` 处理 UUID/datetime 序列化
6. **JWT 双令牌** — access_token（30 分钟）+ refresh_token（7 天），前端 Axios 拦截器自动刷新
7. **附件存储** — 本地文件系统，UUID 重命名防冲突，Docker volume 持久化
8. **站内通知** — 在 booking_service 的每个操作后自动创建通知，不依赖邮件
