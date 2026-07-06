# 开发规范

## 新增后端功能（四步法）

### 第一步：定义 Model

在 `backend/app/models/` 下新建文件，继承 `Base` 和 `TimestampMixin`：

```python
from app.models.base import Base, TimestampMixin

class MyNewModel(TimestampMixin, Base):
    __tablename__ = "my_new_models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # ... 其他字段

    # relationship 使用字符串引用避免循环导入
    related_items = relationship("OtherModel", back_populates="my_model")
```

然后在 `backend/app/models/__init__.py` 中注册：

```python
from app.models.my_new_model import MyNewModel
__all__.append("MyNewModel")
```

如果需要和其他模型建立关系，在对应的模型文件中添加 `relationship`。

### 第二步：定义 Schema

在 `backend/app/schemas/` 下新建文件：

```python
import uuid
from pydantic import BaseModel, field_serializer

class MyModelCreate(BaseModel):
    name: str

class MyModelRead(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)
```

**注意**：
- `from_attributes = True` 允许从 ORM 对象创建
- `@field_serializer` 处理 UUID、datetime 等类型的序列化
- Create schema 用于接收请求，Read schema 用于返回响应

### 第三步：实现 Service

在 `backend/app/services/` 下新建文件，所有函数接收 `AsyncSession` 作为第一参数：

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def create_item(db: AsyncSession, data: MyModelCreate) -> MyModel:
    item = MyModel(**data.model_dump())
    db.add(item)
    await db.flush()
    return item

async def list_items(db: AsyncSession) -> list[MyModel]:
    result = await db.execute(select(MyModel).order_by(MyModel.created_at.desc()))
    return list(result.scalars().all())
```

### 第四步：创建 Router

在 `backend/app/api/v1/` 下新建文件：

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.schemas.my_model import MyModelCreate, MyModelRead
from app.services import my_model_service

router = APIRouter(prefix="/my-models", tags=["我的模型"])

@router.get("", response_model=list[MyModelRead])
async def list_items(db: AsyncSession = Depends(get_db)):
    return await my_model_service.list_items(db)

@router.post("", response_model=MyModelRead, status_code=201)
async def create_item(
    data: MyModelCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),  # 只有管理员可创建
):
    return await my_model_service.create_item(db, data)
```

最后在 `backend/app/api/router.py` 中注册：

```python
from app.api.v1 import auth, instruments, bookings, admin, notifications, my_model

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
# ... 其他路由
router.include_router(my_model.router)
```

### 生成迁移

```bash
cd instrument-booking
docker-compose exec backend alembic revision --autogenerate -m "描述你的改动"
docker-compose exec backend alembic upgrade head
```

---

## 新增前端页面（四步法）

### 第一步：添加 API 函数

在 `frontend/src/api/` 下找对应文件或新建文件：

```typescript
import client from './client'

export interface MyItemRead {
  id: string
  name: string
}

export async function getItems(): Promise<MyItemRead[]> {
  const res = await client.get('/my-models')
  return res.data
}
```

### 第二步：创建 View 组件

在 `frontend/src/views/` 下新建 `.vue` 文件：

```vue
<template>
  <div class="my-page">
    <h2>页面标题</h2>
    <LoadingSpinner v-if="loading" text="加载中..." />
    <EmptyState v-else-if="items.length === 0" title="暂无数据" />
    <div v-else>
      <div v-for="item in items" :key="item.id">{{ item.name }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getItems, type MyItemRead } from '../../api/my-model'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import EmptyState from '../../components/common/EmptyState.vue'

const items = ref<MyItemRead[]>([])
const loading = ref(true)

onMounted(async () => {
  try { items.value = await getItems() } catch {}
  finally { loading.value = false }
})
</script>
```

### 第三步：通用组件直接使用

| 组件 | 用途 |
|------|------|
| LoadingSpinner | 加载状态 |
| ErrorAlert | 显示错误信息 |
| EmptyState | 空数据占位 |
| StatusBadge | 状态标签（pending/approved/rejected/cancelled 等） |
| ConfirmDialog | 确认对话框 |
| Pagination | 分页 |
| StatusBadge | 状态标签 |

### 第四步：注册路由

在 `frontend/src/router/index.ts` 中注册：

```typescript
{
  path: '/my-page',
  name: 'MyPage',
  component: () => import('../views/MyPageView.vue'),
  meta: { requiresAuth: true },
}
```

**路由守卫说明**：
- `meta: { requiresAuth: true }` — 需要登录
- `meta: { guest: true }` — 仅游客可访问（已登录自动跳首页）
- `meta: { requiresAdmin: true }` — 需要管理员权限（自动加载用户信息）

---

## 通用开发规则

### 后端
1. **不要写注释**，用好的命名表达意图
2. 所有数据库操作使用 `await`，不要用同步方式
3. 错误抛出用 `HTTPException`，不要返回 `None` 或错误码
4. Service 中 `db.add()` 后调用 `await db.flush()` 而不是 `commit()`（`get_db` 会自动 commit）
5. 新字段如果是 `bool` 或 `int` 且排除性，记住加 `server_default`

### 前端
1. **不要写注释**
2. API 函数放在 `src/api/`，不要在组件中直接 `axios.get()`
3. 页面级组件放在 `src/views/`，可复用组件放在 `src/components/`
4. 页面级组件命名以 `View` 结尾（如 `MyPageView.vue`）
5. 所有请求/响应类型定义在 API 文件中或用 `types.ts`
6. 组件中先写 loading/empty/error 状态，再写正常展示

### Alembic 迁移

**不要**直接修改已有的迁移文件。如果数据库表结构改了：

```bash
docker-compose exec backend alembic revision --autogenerate -m "改动说明"
docker-compose exec backend alembic upgrade head
```

### 部署

```bash
# 开发环境（数据库 + 缓存运行在 Docker，前后端本地热更新）
docker-compose up -d postgres redis
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev

# 生产环境（所有服务运行在 Docker，一条命令启动）
docker-compose up --build -d

# 部署到另一台 Windows 服务器
# 1. 拷贝整个 instrument-booking 目录
# 2. 目标服务器安装 Docker Desktop
# 3. 修改 .env 中的 SECRET_KEY
# 4. 执行 docker-compose up -d
```

---

## Git 提交规范

### Commit Message 格式

```
<类型>: <简短描述>
```

**类型说明：**

| 类型 | 使用场景 |
|---|---|
| `feat` | 新功能 |
| `fix` | 修复 Bug |
| `refactor` | 重构代码，不改变功能 |
| `style` | 样式调整、代码格式化 |
| `docs` | 文档变更 |
| `chore` | 配置、依赖、CI 等杂项 |

**示例：**
```
feat: 新增仪器批量导出功能
fix: 修复预约时间冲突检测不准确的问题
refactor: 重构通知服务的发送逻辑
docs: 更新 API 接口文档
chore: 升级 bcrypt 依赖版本
```

### 分支管理

| 分支 | 用途 |
|---|---|
| `main` | 稳定版本，随时可部署的代码 |
| `dev` | 日常开发主分支 |
| `feat/xxx` | 新功能分支，从 `dev` 拉取，完成后合并回 `dev` |
| `fix/xxx` | Bug 修复分支，从 `dev` 拉取，完成后合并回 `dev` |

**分支命名示例：**
```
feat/export-instruments
feat/booking-calendar
fix/conflict-detection
fix/login-error
```

**开发流程：**

```
dev → feat/xxx → 开发完成 → 合并回 dev → 验证稳定后 → 合并到 main
```

## 注意事项

1. **Windows 上不要本地 pip install** — 编译型包（asyncpg、pydantic-core）需要 Rust/MSVC。使用 Docker 容器运行后端
2. **bcrypt 版本** — passlib 与 bcrypt 5.x 不兼容，requirements.txt 中固定了 `bcrypt==4.1.3`
3. **UUID 序列化** — Pydantic 不会自动将 UUID 转字符串，每个 schema 需要手动加 `@field_serializer`
4. **Relationship 字符串引用** — 不同模型间的 relationship 使用字符串（如 `"Booking"`），避免在模型文件顶部 import 其他模型

---

## Git 工作流程规范（必须遵守）

### 提交规范

每次完成一个功能或修复一个bug后，必须立即提交并推送：

```bash
# 1. 查看改动
git status

# 2. 添加所有改动
git add .

# 3. 提交（使用规范的提交信息格式）
git commit -m "feat: 新增xxx功能"      # 新功能
git commit -m "fix: 修复xxx问题"       # 修复bug
git commit -m "docs: 更新xxx文档"      # 文档更新
git commit -m "refactor: 重构xxx"      # 代码重构

# 4. 推送到GitHub
git push
```

### 定期备份规则

**每天下班前必须执行一次推送**，确保代码备份到GitHub：

```bash
# 如果有未提交的改动
git add . && git commit -m "daily: 每日备份" && git push

# 如果没有改动，也确认一下状态
git status
```

### 代码备份检查清单

每次推送前检查：

| 检查项 | 说明 |
|--------|------|
| ✓ 所有改动已提交 | `git status` 显示干净 |
| ✓ 提交信息清晰 | 说明改了什么 |
| ✓ 已推送到远程 | `git push` 成功 |
| ✓ 数据库迁移已包含 | 如有新建表或加字段，迁移文件也要提交 |
| ✓ 环境变量已更新 | `.env.example` 如有变更 |

### 新接手开发者入门

1. **首次克隆项目**：
   ```bash
   git clone https://github.com/zhangxlei/instrument-booking.git
   cd instrument-booking
   ```

2. **阅读文档**：
   - `QUICK_START.md` — 快速启动指南
   - `HANDOVER.md` — 项目交接文档（包含所有需求和开发记录）

3. **启动项目**：
   - 双击桌面 `启动仪器预约系统.bat`（如已配置）
   - 或按 `QUICK_START.md` 手动启动

4. **开始开发前**：
   - 确认在 `main` 分支
   - 执行 `git pull` 获取最新代码
   - 按需创建功能分支：`git checkout -b feat/功能名`

5. **开发完成后**：
   - 提交并推送
   - 通知Shelley审核合并
