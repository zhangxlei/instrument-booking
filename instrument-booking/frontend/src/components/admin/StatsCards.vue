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
  gap: 16px;
}
.stat-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.stat-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.stat-card.highlight {
  border-color: #fbbf24;
  background: #fffbeb;
}
.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}
.stat-label {
  font-size: 14px;
  color: #64748b;
  margin: 4px 0 0;
}
</style>
