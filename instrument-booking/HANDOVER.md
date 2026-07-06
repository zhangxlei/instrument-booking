# 仪器预约系统 - 交接文档

## 项目概述

上海光电科技创新中心硅光实验室仪表预约系统。基于 FastAPI + Vue 3 + PostgreSQL 的全栈项目，Docker 容器化部署。

## 当前进度

### ✅ 已完成（30项需求全部完成）

| # | 需求 | 说明 |
|---|------|------|
| 1 | 批量取消预约 | 管理员勾选多条预约后批量取消 |
| 2 | 捎话功能 | 预约时填写留言，审核人/测试老师可见 |
| 3 | 修复 Excel 导出 | 改用 Axios blob 下载，修复 401 问题 |
| 4 | 代外部客户预约 | 按钮改名，下拉选择用户/仪器，补全冲突检测和仪器状态校验 |
| 5 | 仪器管理操作 | 整行可点击进入编辑，删除按钮在编辑页内 |
| 6 | 仪表盘图表 | 环形图（仪器使用率/人员分布）、折线图（30天趋势）、柱状图（时段热度） |
| 7 | 修改用户名/密码 | 用户自己修改、管理员可重置他人 |
| 8 | 全天预约 | 0:00-23:59 可预约 |
| 9 | 日历 2030 | 周导航，支持到 2030 年 |
| 10 | 页脚联系信息 | 管理员邮箱/电话 |
| 11 | 普通用户无管理后台 | 导航栏条件渲染 `v-if="authStore.isAdmin()"` |
| 12 | 灰色不可预约 | 维护/报废仪器日历灰色覆盖层提示 |
| 13 | 去掉缓冲功能 | 从 schema 和表单中移除 min_notice/cleanup_time |
| 14 | 友情链接 | 页脚右下角：`友情链接：FTP文件库` |
| 15 | 显示用户名 | 导航栏退出按钮旁显示 |
| 16 | 管理员删除用户 | 后端添加"不能删除自己"检查 |
| 17 | 超级管理员 | 启动时自动创建 `oeinoadmin / oeinoadmin` |
| 18 | 密码不限长度 | 改 placeholder，后端无长度限制 |
| 19 | 标题修改 | "上海光电科技创新中心硅光实验室仪表预约系统" |
| 20 | 仪器管理人/联系方式 | 字段 + 表单 + 详情页显示 |
| 21 | 图片预览修复 | vite.config.ts 添加 `/uploads` proxy |
| 22 | 吸顶标题 | navbar 添加 sticky CSS |
| 23 | 审批流程图 | BookingReview 模型+API，预约人可选审核人，管理员分配测试老师 |
| 24 | 测试需求文档上传 | 预约时可上传 PDF/doc 等文件 |
| 25 | 通知文档区 | LabDocument 模型+API，管理员后台管理，首页展示 |
| 26 | 登录须知弹窗 | 每次登录弹出，点"我已了解"关闭 |
| 27 | 探针选择 | GSG/GSSG/GSGSG 下拉，仪器和预约都关联 |
| 28 | 预约总览 | 仪器卡片列表 → 点击进入周历视图 |
| 29 | 修复通知日期显示 | 通知消息中的时间从UTC转换为北京时间（UTC+8） |
| 30 | 管理员在线状态查看 | Redis追踪用户在线状态，管理员可查看所有人IP、最后活跃时间、浏览器信息 |

### 🔧 近期修复

| # | 问题 | 修复方案 |
|---|------|----------|
| 1 | 通知日期显示偏差8小时 | `booking_service.py` 添加 `utc_to_beijing()` 函数，替换6处 `strftime` 调用 |
| 2 | 仪表盘图表不显示 | `admin.py` 缺少 `timedelta` 导入，导致图表接口报错 |
| 3 | 管理后台侧边栏命名调整 | "预约总览" → "仪表预约管理"，"预约管理" → "审批管理" |

## 项目结构

```
E:\agent\instrument_system\
├── instrument-booking/          # 主项目目录
│   ├── backend/                 # Python FastAPI 后端
│   │   ├── app/
│   │   │   ├── core/            # 配置、数据库、安全、依赖、Redis
│   │   │   ├── models/          # SQLAlchemy 模型（9个）
│   │   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   │   ├── services/        # 业务逻辑层
│   │   │   └── api/v1/          # 路由层（8个路由模块）
│   │   ├── alembic/             # 数据库迁移
│   │   └── uploads/             # 上传文件存储
│   ├── frontend/                # Vue 3 + TypeScript 前端
│   │   └── src/
│   │       ├── api/             # Axios API 调用
│   │       ├── components/      # UI 组件
│   │       ├── views/           # 页面组件（12个）
│   │       ├── router/          # 路由配置
│   │       ├── stores/          # Pinia 状态管理
│   │       └── composables/     # 组合式函数
│   ├── docker-compose.yml       # Docker 编排（4个服务）
│   └── requirements.txt         # Python 依赖（含 redis[hiredis]）
├── 需求新增1.txt                # 原始28项需求
├── 需求新增2.txt                # 新发现需求
└── 图片1.png                    # 架构图
```

## 数据库模型

9 张表：users, instruments, instrument_maintenance, instrument_attachments, bookings, booking_reviews, booking_documents, lab_documents, notifications

## 技术栈

### 后端
- Python 3.12 + FastAPI
- SQLAlchemy 2.0 (async) + asyncpg
- Alembic 数据库迁移
- Redis 用于用户在线状态追踪

### 前端
- Vue 3 + TypeScript
- Pinia 状态管理
- Chart.js 图表
- Axios HTTP 客户端

### 基础设施
- Docker Compose（PostgreSQL 16 + Redis 7 + Backend + Frontend）

## 启动方式

### 方式一：一键启动（推荐）

双击桌面 `启动仪器预约系统.bat` 文件，自动启动：
1. 后端服务（Docker Compose）
2. 前端开发服务器（npm run dev）

### 方式二：手动启动

```bash
# 1. 启动数据库和后端
cd instrument-booking
docker compose up -d

# 2. 数据库迁移（首次）
docker compose exec backend alembic upgrade head

# 3. 安装 Redis 依赖（首次）
docker compose exec backend pip install redis[hiredis]

# 4. 启动前端（新开终端）
cd frontend
npm run dev -- --host
# 访问 http://localhost:5173
```

## 账号

- 超级管理员：`oeinoadmin` / `oeinoadmin`
- 普通管理员：`admin` / `admin123`（如果没被修改）
- 普通用户：需注册

## 关键注意事项

1. **Windows 不要本地 pip install** — 编译型包无预编译 wheel，使用 Docker
2. **bcrypt 版本锁死** — `bcrypt==4.1.3`（passlib 与 5.x 不兼容）
3. **UUID 序列化** — Pydantic schema 需加 `@field_serializer`
4. **上传文件** — 存在 Docker 容器内，迁移需打包 `uploads/` 目录
5. **CORS** — 开发环境已设为允许所有来源
6. **审批流程** — 预约时自动创建 BookingReview，状态流转：pending_review → review_approved → testing → completed
7. **Redis** — 已部署但之前未使用，现用于用户在线状态追踪（5分钟过期）
8. **时区** — 数据库存UTC，通知显示转北京时间（UTC+8）

## 桌面快捷方式说明

`C:\Users\l\Desktop\启动仪器预约系统.bat` 内容：

```batch
@echo off
cd /d E:\agent\instrument_system\instrument-booking

echo [1/2] 启动后端服务...
docker-compose up -d

echo [2/2] 启动前端服务...
cd /d E:\agent\instrument_system\instrument-booking\frontend
npm run dev -- --host

pause
```

## 新增功能开发记录

### 1. 通知日期修复（2026-07-06）

**问题**：通知消息中的时间比实际北京时间晚8小时

**原因**：`booking_service.py` 直接使用 `strftime` 格式化UTC时间

**修复**：
- 文件：`backend/app/services/booking_service.py`
- 新增 `BEIJING_TZ` 常量和 `utc_to_beijing()` 函数
- 替换6处 `strftime('%m/%d %H:%M')` 为 `utc_to_beijing()`

### 2. 用户在线状态查看（2026-07-06）

**需求**：管理员可查看所有用户的在线状态、IP、最后活跃时间、浏览器信息

**实现**：
- 后端：Redis存储在线状态（5分钟过期）
- API：`GET /admin/online-status`（仅管理员可访问）
- 前端：`AdminOnlineStatusView.vue` 页面，30秒自动刷新

**改动文件**：
| 文件 | 改动 |
|------|------|
| `backend/requirements.txt` | 新增 `redis[hiredis]>=5.0` |
| `backend/app/core/redis.py` | 新建，Redis连接池+在线状态读写 |
| `backend/app/main.py` | lifespan初始化/关闭Redis |
| `backend/app/core/deps.py` | `get_current_user`更新Redis在线状态 |
| `backend/app/api/v1/admin.py` | 新增 `/admin/online-status` 端点 |
| `frontend/src/api/admin.ts` | 新增 `getOnlineStatus()` |
| `frontend/src/views/admin/AdminOnlineStatusView.vue` | 新建，在线状态页面 |
| `frontend/src/router/index.ts` | 注册路由 |
| `frontend/src/components/layout/AppSidebar.vue` | 添加"在线用户"菜单 |

## 已知问题

- 前端 `DashboardCharts.vue` 有一个 TypeScript 类型错误（`keyof ChartTypeRegistry`），不影响功能
