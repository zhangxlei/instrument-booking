<template>
  <div class="stats-grid">
    <div class="stat-card" @click="$emit('navigate', '/admin/instruments')">
      <p class="stat-value">{{ stats.total_instruments }}</p>
      <p class="stat-label">仪器总数</p>
    </div>
    <div class="stat-card" @click="$emit('navigate', '/admin/bookings')">
      <p class="stat-value">{{ stats.today_bookings }}</p>
      <p class="stat-label">今日预约</p>
    </div>
    <div class="stat-card highlight" @click="$emit('navigate', '/admin/bookings?status=pending')">
      <p class="stat-value">{{ stats.pending_approvals }}</p>
      <p class="stat-label">待审批</p>
    </div>
    <div class="stat-card" @click="$emit('navigate', '/admin/users')">
      <p class="stat-value">{{ stats.total_users }}</p>
      <p class="stat-label">用户数</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  stats: {
    total_instruments: number
    total_users: number
    today_bookings: number
    pending_approvals: number
  }
}>()

defineEmits<{
  navigate: [path: string]
}>()
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
}

.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary-light);
}

.stat-card.highlight {
  border-color: var(--color-warning);
  background: var(--color-warning-bg);
}

.stat-card.highlight:hover {
  border-color: var(--color-warning);
  box-shadow: 0 10px 15px -3px rgba(245, 158, 11, 0.2);
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
  line-height: 1;
}

.stat-card.highlight .stat-value {
  color: #B45309;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: var(--space-sm) 0 0;
  font-weight: 500;
}
</style>
