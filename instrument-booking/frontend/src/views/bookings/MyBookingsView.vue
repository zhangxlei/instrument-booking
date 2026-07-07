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
.my-bookings {
  animation: fadeIn var(--transition-slow) ease;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-lg);
}

.tabs {
  display: flex;
  gap: var(--space-xs);
  margin-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
}

.tab {
  padding: var(--space-sm) var(--space-md);
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast);
}

.tab:hover {
  color: var(--color-primary);
}

.tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.booking-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.booking-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.booking-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}

.booking-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.booking-time {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.booking-purpose {
  margin: var(--space-sm) 0 0;
  font-size: 14px;
  color: var(--color-text-muted);
}
</style>
