<template>
  <div class="admin-documents">
    <div class="page-header">
      <h2>通知文档管理</h2>
      <button class="btn-add" @click="openCreate">+ 新增文档</button>
    </div>

    <LoadingSpinner v-if="loading" text="加载中..." />
    <EmptyState v-else-if="list.length === 0" title="暂无文档" />

    <table v-else class="data-table">
      <thead>
        <tr><th>标题</th><th>内容</th><th>发布状态</th><th>登录须知</th><th>创建时间</th><th>操作</th></tr>
      </thead>
      <tbody>
        <tr v-for="doc in list" :key="doc.id">
          <td>{{ doc.title }}</td>
          <td>{{ doc.content ? doc.content.slice(0, 50) + (doc.content.length > 50 ? '...' : '') : '-' }}</td>
          <td>{{ doc.is_published ? '已发布' : '未发布' }}</td>
          <td>{{ doc.is_login_notice ? '是' : '否' }}</td>
          <td>{{ formatTime(doc.created_at) }}</td>
          <td class="actions">
            <button class="btn-edit" @click="openEdit(doc)">编辑</button>
            <button class="btn-delete" @click="handleDelete(doc.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="showForm" class="dialog-overlay" @click.self="showForm = false">
      <div class="dialog">
        <h3>{{ editId ? '编辑文档' : '新增文档' }}</h3>
        <div class="form-group">
          <label>标题 <span class="required">*</span></label>
          <input v-model="form.title" placeholder="文档标题" />
        </div>
        <div class="form-group">
          <label>内容</label>
          <textarea v-model="form.content" placeholder="文档内容" rows="4" />
        </div>
        <div class="form-group">
          <label>文件链接（可选）</label>
          <input v-model="form.file_url" placeholder="http://..." />
        </div>
        <div class="form-row">
          <label class="checkbox-label">
            <input v-model="form.is_published" type="checkbox" /> 已发布
          </label>
          <label class="checkbox-label">
            <input v-model="form.is_login_notice" type="checkbox" /> 设为登录须知
          </label>
        </div>
        <ErrorAlert :message="formError" />
        <div class="form-actions">
          <button class="btn-cancel" @click="showForm = false">取消</button>
          <button class="btn-primary" :disabled="!form.title" @click="handleSave">{{ saving ? '保存中...' : '保存' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '../../api/client'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import EmptyState from '../../components/common/EmptyState.vue'
import ErrorAlert from '../../components/common/ErrorAlert.vue'

interface LabDoc {
  id: string
  title: string
  content: string | null
  file_url: string | null
  is_published: boolean
  is_login_notice: boolean
  created_at: string
}

const list = ref<LabDoc[]>([])
const loading = ref(true)
const showForm = ref(false)
const editId = ref<string | null>(null)
const saving = ref(false)
const formError = ref<string | null>(null)
const form = ref({ title: '', content: '', file_url: '', is_published: true, is_login_notice: false })

function formatTime(iso: string): string {
  const d = new Date(iso)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function load() {
  loading.value = true
  try {
    const res = await client.get('/lab-documents')
    list.value = res.data
  } catch {}
  loading.value = false
}

function openCreate() {
  editId.value = null
  form.value = { title: '', content: '', file_url: '', is_published: true, is_login_notice: false }
  formError.value = null
  showForm.value = true
}

function openEdit(doc: LabDoc) {
  editId.value = doc.id
  form.value = {
    title: doc.title,
    content: doc.content || '',
    file_url: doc.file_url || '',
    is_published: doc.is_published,
    is_login_notice: doc.is_login_notice,
  }
  formError.value = null
  showForm.value = true
}

async function handleSave() {
  if (!form.value.title) return
  saving.value = true
  formError.value = null
  try {
    const body = { ...form.value, file_url: form.value.file_url || null, content: form.value.content || null }
    if (editId.value) {
      await client.put(`/lab-documents/${editId.value}`, body)
    } else {
      await client.post('/lab-documents', body)
    }
    showForm.value = false
    await load()
  } catch (e: any) {
    formError.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: string) {
  if (!confirm('确定删除此文档？')) return
  try {
    await client.delete(`/lab-documents/${id}`)
    await load()
  } catch {}
}

onMounted(load)
</script>

<style scoped>
.admin-documents {
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

.actions {
  display: flex;
  gap: var(--space-xs);
}

.btn-edit,
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

.btn-edit {
  color: var(--color-primary);
  border-color: var(--color-primary-100);
}

.btn-edit:hover {
  background: var(--color-primary-50);
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
  width: 520px;
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
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  box-sizing: border-box;
  transition: border-color var(--transition-fast);
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-row {
  display: flex;
  gap: var(--space-lg);
  margin-bottom: var(--space-md);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 14px;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
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
