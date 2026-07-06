<template>
  <div class="my-bookings">
    <h2 class="page-title">我的预约</h2>

    <div class="tabs">
      <button
        v-for="t in tabs" :key="t.key"
        class="tab"
        :class="{ active: activeTab === t.key }"
        @click="activeTab = t.key; load()"
      >
        {{ t.label }}
      </button>
    </div>

    <LoadingSpinner v-if="loading" text="加载中..." />
    <EmptyState v-else-if="bookings.length === 0" title="暂无预约" />

    <div v-else class="booking-list">
      <div v-for="b in bookings" :key="b.id" class="booking-card" @click="$router.push(`/bookings/${b.id}`)">
        <div class="booking-header">
          <StatusBadge :status="b.status" />
          <span class="booking-time">{{ formatTime(b.start_time) }} ~ {{ formatTime(b.end_time) }}</span>
        </div>
        <p v-if="b.purpose" class="booking-purpose">{{ b.purpose }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getBookings, type BookingRead } from '../../api/bookings'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import EmptyState from '../../components/common/EmptyState.vue'
import StatusBadge from '../../components/common/StatusBadge.vue'

const tabs = [
  { key: '', label: '全部' },
  { key: 'pending', label: '待审批' },
  { key: 'approved', label: '已批准' },
  { key: 'rejected', label: '已拒绝' },
  { key: 'cancelled', label: '已取消' },
]

const activeTab = ref('')
const bookings = ref<BookingRead[]>([])
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    bookings.value = await getBookings(activeTab.value || undefined)
  } catch {}
  loading.value = false
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(load)
</script>

<style scoped>
.page-title {
  font-size: 22px;
  color: #1e293b;
  margin-bottom: 16px;
}
.tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}
.tab {
  padding: 8px 16px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  color: #64748b;
  border-bottom: 2px solid transparent;
}
.tab.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
  font-weight: 500;
}
.booking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.booking-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
}
.booking-card:hover {
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.booking-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.booking-time {
  font-size: 14px;
  color: #475569;
}
.booking-purpose {
  margin: 8px 0 0;
  font-size: 14px;
  color: #64748b;
}
</style>
