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
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.page-header h2 { font-size: 22px; color: #1e293b; margin: 0; }
.header-right { display: flex; align-items: center; gap: 12px; }
.last-refresh { font-size: 13px; color: #94a3b8; }
.btn-refresh {
  padding: 6px 16px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}
.btn-refresh:hover { background: #f8fafc; }
.btn-refresh:disabled { opacity: 0.6; }
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}
.data-table th {
  background: #f8fafc;
  padding: 10px 16px;
  text-align: left;
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
  border-bottom: 1px solid #e2e8f0;
}
.data-table td {
  padding: 10px 16px;
  font-size: 14px;
  border-bottom: 1px solid #f1f5f9;
}
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
}
.status-dot.online { background: #22c55e; }
.status-dot.offline { background: #d1d5db; }
.status-label { font-size: 13px; color: #475569; }
.browser-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
  color: #64748b;
}
</style>
