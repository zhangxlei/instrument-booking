<template>
  <div class="approval-table">
    <table v-if="bookings.length > 0" class="data-table">
      <thead>
        <tr>
          <th>用户</th>
          <th>仪器</th>
          <th>时间段</th>
          <th>目的</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="b in bookings" :key="b.id">
          <td>{{ b.user_full_name || b.user_username || b.user_id.slice(0, 8) }}</td>
          <td>{{ b.instrument_name || b.instrument_id.slice(0, 8) }}</td>
          <td>{{ formatTime(b.start_time) }} ~ {{ formatTime(b.end_time) }}</td>
          <td>{{ b.purpose || '-' }}</td>
          <td class="actions">
            <button class="btn-approve" :disabled="processing" @click="$emit('approve', b.id)">批准</button>
            <button class="btn-reject" :disabled="processing" @click="$emit('reject', b)">拒绝</button>
          </td>
        </tr>
      </tbody>
    </table>
    <EmptyState v-else title="没有待审批的预约" />
  </div>
</template>

<script setup lang="ts">
import type { BookingRead } from '../../api/bookings'
import EmptyState from '../common/EmptyState.vue'

defineProps<{
  bookings: BookingRead[]
  processing?: boolean
}>()

defineEmits<{
  approve: [id: string]
  reject: [booking: BookingRead]
}>()

function formatTime(iso: string): string {
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.data-table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; }
.data-table th { background: #f8fafc; padding: 10px 12px; text-align: left; font-size: 13px; color: #64748b; font-weight: 600; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 10px 12px; font-size: 13px; border-bottom: 1px solid #f1f5f9; }
.actions { display: flex; gap: 6px; }
.btn-approve, .btn-reject { padding: 4px 12px; border-radius: 4px; border: 1px solid; cursor: pointer; font-size: 13px; background: white; }
.btn-approve { color: #166534; border-color: #bbf7d0; }
.btn-reject { color: #dc2626; border-color: #fecaca; }
.btn-approve:disabled, .btn-reject:disabled { opacity: 0.4; }
</style>
