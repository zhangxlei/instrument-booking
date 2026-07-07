<template>
  <div class="detail-page">
    <button class="btn-back" @click="$router.push('/bookings')">← 返回列表</button>

    <LoadingSpinner v-if="loading" text="加载中..." />
    <div v-else-if="error" class="error-msg">{{ error }}</div>

    <div v-else-if="booking" class="detail-card">
      <div class="detail-header">
        <h1>预约详情</h1>
        <StatusBadge :status="booking.status" />
      </div>

      <div class="detail-section">
        <h3>审批流程</h3>
        <BookingFlowStatus :status="booking.status" :review="review" />
      </div>

      <div class="detail-info">
        <div class="info-row"><span class="label">时间</span><span>{{ formatTime(booking.start_time) }} ~ {{ formatTime(booking.end_time) }}</span></div>
        <div class="info-row"><span class="label">目的</span><span>{{ booking.purpose || '-' }}</span></div>
        <div class="info-row"><span class="label">备注</span><span>{{ booking.notes || '-' }}</span></div>
        <div v-if="booking.message" class="info-row"><span class="label">捎话</span><span>{{ booking.message }}</span></div>
        <div v-if="booking.probe_type" class="info-row"><span class="label">探针类型</span><span>{{ booking.probe_type }}</span></div>
        <div v-if="booking.rejection_reason" class="info-row"><span class="label">拒绝原因</span><span class="reject">{{ booking.rejection_reason }}</span></div>
      </div>

      <div class="detail-section">
        <h3>测试需求文档</h3>
        <div v-if="documents.length === 0" class="no-data">暂无文档</div>
        <div v-for="doc in documents" :key="doc.id" class="doc-item">
          <a :href="`/api/v1/bookings/${route.params.id}/documents/${doc.id}`" target="_blank">{{ doc.original_filename }}</a>
          <span class="doc-size">({{ (doc.file_size / 1024).toFixed(1) }} KB)</span>
        </div>
        <div class="upload-area">
          <input type="file" @change="handleDocUpload" accept=".pdf,.doc,.docx,.txt,.zip" />
        </div>
      </div>

      <div class="actions">
        <ConfirmDialog
          :visible="showCancelConfirm"
          title="取消预约"
          message="确定要取消这个预约吗？"
          confirm-text="确定取消"
          :danger="true"
          @confirm="handleCancel"
          @cancel="showCancelConfirm = false"
        />
        <button
          v-if="booking.status === 'pending' || booking.status === 'approved'"
          class="btn-cancel"
          @click="showCancelConfirm = true"
        >
          取消预约
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getBooking, cancelBooking, type BookingRead } from '../../api/bookings'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import StatusBadge from '../../components/common/StatusBadge.vue'
import ConfirmDialog from '../../components/common/ConfirmDialog.vue'
import BookingFlowStatus from '../../components/bookings/BookingFlowStatus.vue'
import client from '../../api/client'

const route = useRoute()
const router = useRouter()
const booking = ref<BookingRead | null>(null)
const review = ref<{ status: string; reviewer_id?: string | null; tester_id?: string | null; reviewer_comment?: string | null } | null>(null)
const documents = ref<{ id: string; original_filename: string; file_size: number }[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const showCancelConfirm = ref(false)

async function loadDocuments() {
  try {
    const res = await client.get(`/bookings/${route.params.id}/documents`)
    documents.value = res.data
  } catch {}
}

async function handleDocUpload(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    await client.post(`/bookings/${route.params.id}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    await loadDocuments()
  } catch { alert('上传失败') }
  input.value = ''
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function handleCancel() {
  try {
    await cancelBooking(route.params.id as string)
    showCancelConfirm.value = false
    router.push('/bookings')
  } catch {}
}

onMounted(async () => {
  try {
    booking.value = await getBooking(route.params.id as string)
    try {
      const res = await client.get(`/booking-reviews/${route.params.id}`)
      review.value = res.data
    } catch {}
    await loadDocuments()
  } catch { error.value = '加载失败' }
  finally { loading.value = false }
})
</script>

<style scoped>
.detail-page {
  max-width: 600px;
  animation: fadeIn var(--transition-slow) ease;
}

.btn-back {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  padding: 0;
  margin-bottom: var(--space-md);
  transition: color var(--transition-fast);
}

.btn-back:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.detail-card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.detail-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.detail-header h1 {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text);
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.info-row {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.label {
  color: var(--color-text-muted);
  margin-right: var(--space-sm);
  font-weight: 500;
}

.reject {
  color: var(--color-danger);
}

.detail-section {
  margin-bottom: var(--space-lg);
}

.detail-section h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-sm);
}

.actions {
  margin-top: var(--space-lg);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border-light);
}

.btn-cancel {
  padding: 10px 24px;
  border: 1px solid var(--color-danger-bg);
  color: var(--color-danger);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-cancel:hover {
  background: var(--color-danger-bg);
  box-shadow: var(--shadow-sm);
}

.error-msg {
  text-align: center;
  color: var(--color-danger);
  padding: var(--space-2xl);
}

.no-data {
  color: var(--color-text-muted);
  font-size: 13px;
  padding: var(--space-sm) 0;
}

.doc-item {
  font-size: 13px;
  padding: var(--space-xs) 0;
}

.doc-item a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.doc-item a:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.doc-size {
  color: var(--color-text-muted);
  font-size: 12px;
}

.upload-area {
  margin-top: var(--space-sm);
}

.upload-area input {
  font-size: 13px;
}
</style>
