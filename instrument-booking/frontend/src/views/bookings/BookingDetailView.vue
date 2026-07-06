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

      <div class="detail-info">
        <div class="info-row"><span class="label">时间</span><span>{{ formatTime(booking.start_time) }} ~ {{ formatTime(booking.end_time) }}</span></div>
        <div class="info-row"><span class="label">目的</span><span>{{ booking.purpose || '-' }}</span></div>
        <div class="info-row"><span class="label">备注</span><span>{{ booking.notes || '-' }}</span></div>
        <div v-if="booking.rejection_reason" class="info-row"><span class="label">拒绝原因</span><span class="reject">{{ booking.rejection_reason }}</span></div>
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

const route = useRoute()
const router = useRouter()
const booking = ref<BookingRead | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const showCancelConfirm = ref(false)

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
  } catch { error.value = '加载失败' }
  finally { loading.value = false }
})
</script>

<style scoped>
.detail-page { max-width: 600px; }
.btn-back { background: none; border: none; color: #3b82f6; cursor: pointer; font-size: 14px; padding: 0; margin-bottom: 16px; }
.detail-card { background: white; border-radius: 8px; padding: 24px; border: 1px solid #e2e8f0; }
.detail-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.detail-header h1 { font-size: 20px; margin: 0; color: #1e293b; }
.detail-info { display: flex; flex-direction: column; gap: 10px; }
.info-row { font-size: 14px; color: #475569; }
.label { color: #94a3b8; margin-right: 8px; }
.reject { color: #dc2626; }
.actions { margin-top: 20px; padding-top: 16px; border-top: 1px solid #f1f5f9; }
.btn-cancel { padding: 8px 20px; border: 1px solid #fecaca; color: #dc2626; background: white; border-radius: 6px; cursor: pointer; font-size: 14px; }
.error-msg { text-align: center; color: #dc2626; padding: 48px; }
</style>
