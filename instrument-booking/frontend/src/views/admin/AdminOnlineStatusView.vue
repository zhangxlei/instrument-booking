<template>
  <div class="admin-online-status">
    <div class="page-header">
      <h2>在线用户</h2>
      <div class="header-right">
        <span class="last-refresh">最后刷新：{{ lastRefresh }}</span>
        <button class="btn-refresh" @click="load" :disabled="loading">
          {{ loading ? '刷新中...' : '刷新' }}
        </button>
      </div>
    </div>

    <LoadingSpinner v-if="loading && users.length === 0" text="加载中..." />
    <EmptyState v-else-if="users.length === 0" title="暂无用户" />

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>状态</th>
          <th>用户名</th>
          <th>姓名</th>
          <th>IP 地址</th>
          <th>最后活跃</th>
          <th>浏览器信息</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.user_id">
          <td>
            <span class="status-dot" :class="u.is_online ? 'online' : 'offline'" />
            <span class="status-label">{{ u.is_online ? '在线' : '离线' }}</span>
          </td>
          <td>{{ u.username }}</td>
          <td>{{ u.full_name }}</td>
          <td>{{ u.is_online ? (u.ip || '—') : '—' }}</td>
          <td>{{ u.last_active || '—' }}</td>
          <td class="browser-cell">{{ u.is_online ? parseBrowser(u.browser) : '—' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { getOnlineStatus, type UserOnlineStatus } from '../../api/admin'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import EmptyState from '../../components/common/EmptyState.vue'

const users = ref<UserOnlineStatus[]>([])
const loading = ref(false)
const lastRefresh = ref('')
let timer: ReturnType<typeof setInterval> | null = null

async function load() {
  loading.value = true
  try {
    users.value = await getOnlineStatus()
    const now = new Date()
    lastRefresh.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  } catch {}
  loading.value = false
}

function parseBrowser(ua: string | null): string {
  if (!ua) return '—'
  if (ua.includes('Edg/')) return 'Edge'
  if (ua.includes('Chrome/')) return 'Chrome'
  if (ua.includes('Firefox/')) return 'Firefox'
  if (ua.includes('Safari/')) return 'Safari'
  return ua.substring(0, 30)
}

onMounted(() => {
  load()
  timer = setInterval(load, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.admin-online-status {
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

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.last-refresh {
  font-size: 13px;
  color: var(--color-text-muted);
}

.btn-refresh {
  padding: 8px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-refresh:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-text-muted);
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: var(--space-sm);
  vertical-align: middle;
}

.status-dot.online { 
  background: var(--color-success);
  box-shadow: 0 0 0 2px var(--color-success-bg);
}

.status-dot.offline { 
  background: var(--color-text-muted); 
}

.status-label { 
  font-size: 13px; 
  color: var(--color-text-secondary); 
}

.browser-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
  color: var(--color-text-muted);
}
</style>
