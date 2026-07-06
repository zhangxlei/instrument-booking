<template>
  <div class="admin-instruments">
    <div class="page-header">
      <h2>仪器管理</h2>
      <div class="header-actions">
        <a href="/api/v1/admin/export/instruments" class="btn-export" target="_blank">导出 Excel</a>
        <button class="btn-add" @click="$router.push('/admin/instruments/new')">+ 新增仪器</button>
      </div>
    </div>

    <LoadingSpinner v-if="loading" text="加载中..." />

    <EmptyState v-else-if="instruments.length === 0" title="暂无仪器" description="点击上方按钮添加第一台仪器" />

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>名称</th>
          <th>位置</th>
          <th>状态</th>
          <th>价格</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in instruments" :key="item.id">
          <td>{{ item.name }}</td>
          <td>{{ item.location || '-' }}</td>
          <td>
            <span class="status-badge" :class="item.status">{{ statusMap[item.status] }}</span>
          </td>
          <td>{{ item.price_per_hour ? '¥' + item.price_per_hour + '/小时' : '-' }}</td>
          <td class="actions">
            <button class="btn-edit" @click="$router.push(`/admin/instruments/${item.id}/edit`)">编辑</button>
            <button class="btn-delete" @click="handleDelete(item.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getInstruments, deleteInstrument, type InstrumentRead } from '../../api/instruments'
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

async function handleDelete(id: string) {
  if (!confirm('确定删除该仪器？')) return
  try {
    await deleteInstrument(id)
    instruments.value = instruments.value.filter((i) => i.id !== id)
  } catch {}
}

onMounted(load)
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.page-header h2 {
  font-size: 22px;
  color: #1e293b;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
.btn-add {
  padding: 8px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}
.btn-export {
  padding: 8px 20px;
  background: white;
  color: #3b82f6;
  border: 1px solid #3b82f6;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}
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
.status-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
}
.status-badge.available { background: #dcfce7; color: #166534; }
.status-badge.maintenance { background: #fef9c3; color: #854d0e; }
.status-badge.retired { background: #f1f5f9; color: #64748b; }
.actions {
  display: flex;
  gap: 8px;
}
.btn-edit, .btn-delete {
  padding: 4px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 13px;
}
.btn-delete { color: #dc2626; border-color: #fecaca; }
</style>
