<template>
  <div class="admin-users">
    <div class="page-header">
      <h2>用户管理</h2>
      <button class="btn-add" @click="showCreateDialog = true">+ 新增用户</button>
    </div>

    <LoadingSpinner v-if="loading" text="加载中..." />
    <EmptyState v-else-if="users.length === 0" title="暂无用户" />

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>用户名</th>
          <th>姓名</th>
          <th>角色</th>
          <th>状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>{{ u.username }}</td>
          <td>{{ u.full_name }}</td>
          <td>
            <select :value="u.role" @change="handleRoleChange(u.id, ($event.target as HTMLSelectElement).value)">
              <option value="user">用户</option>
              <option value="admin">管理员</option>
            </select>
          </td>
          <td>
            <span class="status-text" :class="u.is_active ? 'active' : 'inactive'">
              {{ u.is_active ? '启用' : '禁用' }}
            </span>
          </td>
          <td class="actions">
            <button class="btn-toggle" @click="handleToggleActive(u.id)">
              {{ u.is_active ? '禁用' : '启用' }}
            </button>
            <button class="btn-action" @click="openResetPassword(u.id)">重置密码</button>
            <button class="btn-delete" @click="handleDelete(u.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Create User Dialog -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
      <div class="dialog">
        <h3>新增用户</h3>
        <div class="form-group">
          <label>用户名 <span class="required">*</span></label>
          <input v-model="createForm.username" placeholder="用户名" />
        </div>
        <div class="form-group">
          <label>姓名 <span class="required">*</span></label>
          <input v-model="createForm.full_name" placeholder="真实姓名" />
        </div>
        <div class="form-group">
          <label>密码 <span class="required">*</span></label>
          <input v-model="createForm.password" type="password" placeholder="密码" />
        </div>
        <div class="form-group">
          <label>角色</label>
          <select v-model="createForm.role">
            <option value="user">用户</option>
            <option value="admin">管理员</option>
          </select>
        </div>
        <ErrorAlert :message="createError" />
        <div class="form-actions">
          <button class="btn-cancel" @click="showCreateDialog = false">取消</button>
          <button class="btn-primary" :disabled="createSaving" @click="handleCreate">
            {{ createSaving ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <ChangePasswordDialog :visible="showPasswordDialog" :is-admin="true" :user-id="resetUserId" @close="showPasswordDialog = false" @saved="load" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getUsers, createUser, changeUserRole, toggleUserActive, deleteUser, type UserAdmin } from '../../api/admin'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import EmptyState from '../../components/common/EmptyState.vue'
import ErrorAlert from '../../components/common/ErrorAlert.vue'
import ChangePasswordDialog from '../../components/auth/ChangePasswordDialog.vue'

const users = ref<UserAdmin[]>([])
const loading = ref(true)
const showCreateDialog = ref(false)
const createSaving = ref(false)
const createError = ref<string | null>(null)
const createForm = ref({ username: '', full_name: '', password: '', role: 'user' })
const showPasswordDialog = ref(false)
const resetUserId = ref('')

function openResetPassword(userId: string) {
  resetUserId.value = userId
  showPasswordDialog.value = true
}

async function load() {
  loading.value = true
  try {
    users.value = await getUsers()
  } catch {}
  loading.value = false
}

async function handleRoleChange(userId: string, role: string) {
  try {
    await changeUserRole(userId, role)
    await load()
  } catch (e: any) {
    alert(e.response?.data?.detail || '修改失败')
  }
}

async function handleToggleActive(userId: string) {
  try {
    await toggleUserActive(userId)
    await load()
  } catch {}
}

async function handleDelete(userId: string) {
  if (!confirm('确定删除该用户？')) return
  try {
    await deleteUser(userId)
    await load()
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

async function handleCreate() {
  if (!createForm.value.username || !createForm.value.full_name || !createForm.value.password) return
  createSaving.value = true
  createError.value = null
  try {
    await createUser(createForm.value)
    showCreateDialog.value = false
    createForm.value = { username: '', full_name: '', password: '', role: 'user' }
    await load()
  } catch (e: any) {
    createError.value = e.response?.data?.detail || '创建失败'
  } finally {
    createSaving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.page-header h2 { font-size: 22px; color: #1e293b; margin: 0; }
.btn-add {
  padding: 8px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}
.data-table th {
  background: #f8fafc;
  padding: 10px 16px;
  text-align: left;
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
  border-bottom: 1px solid #e2e8f0;
}
.data-table td {
  padding: 10px 16px;
  font-size: 14px;
  border-bottom: 1px solid #f1f5f9;
}
.data-table select {
  padding: 4px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 13px;
}
.status-text { font-size: 13px; font-weight: 500; }
.status-text.active { color: #166534; }
.status-text.inactive { color: #dc2626; }
.actions { display: flex; gap: 6px; }
.btn-toggle, .btn-action, .btn-delete {
  padding: 4px 12px;
  border: 1px solid;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 13px;
}
.btn-toggle { color: #3b82f6; border-color: #bfdbfe; }
.btn-delete { color: #dc2626; border-color: #fecaca; }
.dialog-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.3);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.dialog {
  background: white; border-radius: 8px; padding: 24px; width: 400px; max-width: 90vw;
}
.dialog h3 { margin: 0 0 16px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; font-size: 13px; color: #374151; margin-bottom: 4px; font-weight: 500; }
.required { color: #dc2626; }
.form-group input, .form-group select {
  width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; box-sizing: border-box;
}
.form-actions { display: flex; gap: 8px; margin-top: 16px; }
.btn-primary {
  padding: 8px 20px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;
}
.btn-primary:disabled { opacity: 0.6; }
.btn-cancel { padding: 8px 20px; background: white; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; }
</style>
