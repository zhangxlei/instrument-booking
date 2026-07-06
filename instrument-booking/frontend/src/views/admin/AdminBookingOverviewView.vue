<template>
  <div class="booking-overview">
    <div class="page-header">
      <h2>预约总览</h2>
    </div>
    <LoadingSpinner v-if="loading" text="加载中..." />
    <table v-else class="data-table">
      <thead>
        <tr>
          <th>仪器名称</th>
          <th>状态</th>
          <th>待审批</th>
          <th>已通过</th>
          <th>已取消</th>
          <th>近期预约</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in list" :key="item.id">
          <td>{{ item.name }}</td>
          <td><span class="status-badge" :class="item.status">{{ statusMap[item.status] }}</span></td>
          <td>{{ item.pending_count }}</td>
          <td>{{ item.approved_count }}</td>
          <td>{{ item.cancelled_count }}</td>
          <td>
            <div v-if="item.next_bookings.length === 0" class="no-bookings">暂无</div>
            <div v-for="b in item.next_bookings" :key="b.start_time" class="next-booking">
              <StatusBadge :status="b.status" />
              <span class="booking-time">{{ formatTime(b.start_time) }} ~ {{ formatTime(b.end_time) }}</span>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <EmptyState v-if="!loading && list.length === 0" title="暂无仪器数据" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '../../api/client'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import EmptyState from '../../components/common/EmptyState.vue'
import StatusBadge from '../../components/common/StatusBadge.vue'

interface OverviewItem {
  id: string
  name: string
  status: string
  pending_count: number
  approved_count: number
  cancelled_count: number
  next_bookings: { start_time: string; end_time: string; status: string }[]
}

const list = ref<OverviewItem[]>([])
const loading = ref(true)

const statusMap: Record<string, string> = {
  available: '可用',
  maintenance: '维护中',
  retired: '已报废',
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function load() {
  loading.value = true
  try {
    const res = await client.get('/admin/instruments/booking-overview')
    list.value = res.data
  } catch {}
  loading.value = false
}

onMounted(load)
</script>

<style scoped>
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 22px; color: #1e293b; margin: 0; }
.data-table {
  width: 100%; border-collapse: collapse; background: white;
  border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;
}
.data-table th {
  background: #f8fafc; padding: 10px 12px; text-align: left;
  font-size: 13px; color: #64748b; font-weight: 600; border-bottom: 1px solid #e2e8f0;
}
.data-table td {
  padding: 10px 12px; font-size: 13px; border-bottom: 1px solid #f1f5f9;
}
.status-badge { font-size: 12px; padding: 2px 8px; border-radius: 10px; }
.status-badge.available { background: #dcfce7; color: #166534; }
.status-badge.maintenance { background: #fef9c3; color: #854d0e; }
.status-badge.retired { background: #f1f5f9; color: #64748b; }
.next-booking { display: flex; align-items: center; gap: 6px; margin: 2px 0; }
.booking-time { font-size: 12px; color: #475569; }
.no-bookings { color: #94a3b8; font-size: 12px; }
</style>
