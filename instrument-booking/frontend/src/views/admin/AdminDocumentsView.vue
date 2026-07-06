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
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; color: #1e293b; margin: 0; }
.btn-add { padding: 8px 20px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; }
.data-table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; }
.data-table th { background: #f8fafc; padding: 10px 12px; text-align: left; font-size: 13px; color: #64748b; font-weight: 600; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 10px 12px; font-size: 13px; border-bottom: 1px solid #f1f5f9; }
.actions { display: flex; gap: 6px; }
.btn-edit, .btn-delete { padding: 4px 12px; border: 1px solid; border-radius: 4px; background: white; cursor: pointer; font-size: 13px; }
.btn-edit { color: #3b82f6; border-color: #bfdbfe; }
.btn-delete { color: #dc2626; border-color: #fecaca; }
.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 100; }
.dialog { background: white; border-radius: 8px; padding: 24px; width: 500px; max-width: 90vw; }
.dialog h3 { margin: 0 0 16px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; font-size: 13px; color: #374151; margin-bottom: 4px; font-weight: 500; }
.required { color: #dc2626; }
.form-group input, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; box-sizing: border-box; }
.form-group textarea { resize: vertical; }
.form-row { display: flex; gap: 20px; margin-bottom: 12px; }
.checkbox-label { display: flex; align-items: center; gap: 6px; font-size: 14px; cursor: pointer; }
.form-actions { display: flex; gap: 8px; margin-top: 16px; }
.btn-primary { padding: 8px 20px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; }
.btn-primary:disabled { opacity: 0.6; }
.btn-cancel { padding: 8px 20px; background: white; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; }
</style>
