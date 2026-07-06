# 仪器预约系统 - 交接文档

## 项目概述

上海光电科技创新中心硅光实验室仪表预约系统。基于 FastAPI + Vue 3 + PostgreSQL 的全栈项目，Docker 容器化部署。

## 当前进度

### ✅ 已完成（28项全部完成）

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

### ⏳ 新增待办（需求新增2.txt）

| # | 需求 | 说明 |
|---|------|------|
| 29 | 预约系统的日期不太对 | 需排查时区/日期显示问题 |
| 30 | 增加其它用户在线状态查看 | 需新增在线状态追踪功能 |

## 项目结构

```
E:\agent\instrument_system\
├── instrument-booking/          # 主项目目录
│   ├── backend/                 # Python FastAPI 后端
│   │   ├── app/
│   │   │   ├── core/            # 配置、数据库、安全、依赖
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
│   │       ├── views/           # 页面组件（11个）
│   │       ├── router/          # 路由配置
│   │       ├── stores/          # Pinia 状态管理
│   │       └── composables/     # 组合式函数
│   └── docker-compose.yml       # Docker 编排
├── 需求新增1.txt                # 原始28项需求
├── 需求新增2.txt                # 新发现需求
└── 图片1.png                    # 架构图
```

## 数据库模型

9 张表：users, instruments, instrument_maintenance, instrument_attachments, bookings, booking_reviews, booking_documents, lab_documents, notifications

## 启动方式

```bash
# 1. 启动数据库和后端
cd instrument-booking
docker compose up -d postgres redis backend

# 2. 数据库迁移
docker compose exec backend alembic upgrade head

# 3. 启动前端
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

## 已知问题

- 无
