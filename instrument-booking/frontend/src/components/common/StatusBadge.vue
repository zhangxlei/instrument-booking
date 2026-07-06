<template>
  <span class="status-badge" :class="status">{{ text }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ status: string }>()

const map: Record<string, string> = {
  pending: '待审批',
  approved: '已批准',
  rejected: '已拒绝',
  cancelled: '已取消',
  completed: '已完成',
}

const text = computed(() => map[props.status] || props.status)
</script>

<style scoped>
.status-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}
.pending { background: #fef9c3; color: #854d0e; }
.approved { background: #dcfce7; color: #166534; }
.rejected { background: #fef2f2; color: #dc2626; }
.cancelled { background: #f1f5f9; color: #64748b; }
.completed { background: #eff6ff; color: #1d4ed8; }
</style>
