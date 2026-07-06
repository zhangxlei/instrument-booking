<template>
  <div v-if="totalPages > 1" class="pagination">
    <button :disabled="currentPage <= 1" @click="$emit('page-change', currentPage - 1)">
      上一页
    </button>
    <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
    <button :disabled="currentPage >= totalPages" @click="$emit('page-change', currentPage + 1)">
      下一页
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  currentPage: number
  totalPages: number
}>()

defineEmits<{
  'page-change': [page: number]
}>()
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}
.pagination button {
  padding: 6px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 14px;
}
.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.pagination button:hover:not(:disabled) {
  background: #f1f5f9;
}
.page-info {
  font-size: 14px;
  color: #64748b;
}
</style>
