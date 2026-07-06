<template>
  <div class="filters">
    <input v-model="search" placeholder="搜索仪器名称..." class="filter-input" @input="onFilter" />
    <select v-model="status" class="filter-select" @change="onFilter">
      <option value="">全部状态</option>
      <option value="available">可用</option>
      <option value="maintenance">维护中</option>
      <option value="retired">已报废</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  filter: [params: { search: string; status: string }]
}>()

const search = ref('')
const status = ref('')

function onFilter() {
  emit('filter', {
    search: search.value,
    status: status.value,
  })
}
</script>

<style scoped>
.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.filter-input {
  flex: 1;
  min-width: 200px;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}
.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}
</style>
