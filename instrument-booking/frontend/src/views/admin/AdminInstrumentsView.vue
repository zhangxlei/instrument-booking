<template>
  <div class="admin-instruments">
    <div class="page-header">
      <h2>仪器管理</h2>
      <div class="header-actions">
        <button class="btn-export" @click="handleExport">导出 Excel</button>
        <button class="btn-add" @click="$router.push('/admin/instruments/new')">+ 新增仪器</button>
      </div>
    </div>

    <LoadingSpinner v-if="loading" text="加载中..." />

    <EmptyState v-else-if="instruments.length === 0" title="暂无仪器" description="点击上方按钮添加第一台仪器" />

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>名称</th>
          <th>管理</th>
          <th>位置</th>
          <th>状态</th>
          <th>价格</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in instruments" :key="item.id" class="clickable-row" @click="$router.push(`/admin/instruments/${item.id}/edit`)">
          <td>{{ item.name }}</td>
          <td>{{ item.manager_name || '-' }}</td>
          <td>{{ item.location || '-' }}</td>
          <td>
            <span class="status-badge" :class="item.status">{{ statusMap[item.status] }}</span>
          </td>
          <td>{{ item.price_per_hour ? '¥' + item.price_per_hour + '/小时' : '-' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getInstruments, type InstrumentRead } from '../../api/instruments'
import { exportInstrumentsExcel } from '../../api/admin'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import EmptyState from '../../components/common/EmptyState.vue'

const instruments = ref<InstrumentRead[]>([])
const loading = ref(true)

const statusMap: Record<string, string> = {
  available: '可用',
  maintenance: '维护中',
  retired: '已报废',
}

async function load() {
  loading.value = true
  try {
    instruments.value = await getInstruments()
  } catch {}
  loading.value = false
}

async function handleExport() {
  try {
    await exportInstrumentsExcel()
  } catch (e: any) {
    alert(e.response?.data?.detail || '导出失败')
  }
}

onMounted(load)
</script>

<style scoped>
.admin-instruments {
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

.header-actions {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
}

.btn-add {
  padding: 10px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-add:hover {
  background: var(--color-primary-dark);
  box-shadow: var(--shadow-md);
}

.btn-export {
  padding: 10px 20px;
  background: var(--color-surface);
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-export:hover {
  background: var(--color-primary-50);
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

.status-badge {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-weight: 500;
}

.status-badge.available { 
  background: var(--color-success-bg); 
  color: #047857; 
}

.status-badge.maintenance { 
  background: var(--color-warning-bg); 
  color: #B45309; 
}

.status-badge.retired { 
  background: var(--color-bg); 
  color: var(--color-text-secondary); 
}

.clickable-row {
  cursor: pointer;
}
</style>
