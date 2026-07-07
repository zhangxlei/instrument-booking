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
.admin-users {
  animation: fadeIn var(--transition-slow) ease;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.btn-add {
  padding: 10px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-add:hover {
  background: var(--color-primary-dark);
  box-shadow: var(--shadow-md);
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.data-table th {
  background: var(--color-bg);
  padding: 14px 16px;
  text-align: left;
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--color-border);
}

.data-table td {
  padding: 14px 16px;
  font-size: 14px;
  border-bottom: 1px solid var(--color-border-light);
}

.data-table tbody tr {
  transition: background var(--transition-fast);
}

.data-table tbody tr:hover {
  background: var(--color-primary-50);
}

.data-table tbody tr:nth-child(even) {
  background: var(--color-bg);
}

.data-table tbody tr:nth-child(even):hover {
  background: var(--color-primary-50);
}

.data-table select {
  padding: 6px 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 13px;
  background: var(--color-surface);
  transition: border-color var(--transition-fast);
}

.data-table select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.status-text {
  font-size: 13px;
  font-weight: 500;
}

.status-text.active { color: #047857; }
.status-text.inactive { color: var(--color-danger); }

.actions {
  display: flex;
  gap: var(--space-xs);
}

.btn-toggle,
.btn-action,
.btn-delete {
  padding: 6px 12px;
  border: 1px solid;
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-toggle {
  color: var(--color-primary);
  border-color: var(--color-primary-100);
}

.btn-toggle:hover {
  background: var(--color-primary-50);
}

.btn-action {
  color: var(--color-text-secondary);
  border-color: var(--color-border);
}

.btn-action:hover {
  background: var(--color-surface-hover);
}

.btn-delete {
  color: var(--color-danger);
  border-color: var(--color-danger-bg);
}

.btn-delete:hover {
  background: var(--color-danger-bg);
}

.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn var(--transition-fast) ease;
}

.dialog {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  width: 420px;
  max-width: 90vw;
  box-shadow: var(--shadow-xl);
  animation: slideIn var(--transition-normal) ease;
}

.dialog h3 {
  margin: 0 0 var(--space-lg);
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
}

.form-group {
  margin-bottom: var(--space-md);
}

.form-group label {
  display: block;
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
  font-weight: 500;
}

.required {
  color: var(--color-danger);
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  box-sizing: border-box;
  transition: border-color var(--transition-fast);
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.form-actions {
  display: flex;
  gap: var(--space-sm);
  margin-top: var(--space-lg);
  justify-content: flex-end;
}

.btn-primary {
  padding: 10px 24px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  box-shadow: var(--shadow-md);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  padding: 10px 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-cancel:hover {
  background: var(--color-surface-hover);
}
</style>
