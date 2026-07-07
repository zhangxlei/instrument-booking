<template>
  <div class="instrument-list-page">
    <h2 class="page-title">仪器列表</h2>

    <div v-if="notices.length > 0" class="notice-board">
      <div class="notice-header">📢 通知公告</div>
      <div v-for="n in notices" :key="n.id" class="notice-item">
        <span class="notice-title">{{ n.title }}</span>
        <span v-if="n.content" class="notice-content">{{ n.content }}</span>
      </div>
    </div>

    <InstrumentFilters @filter="onFilter" />

    <LoadingSpinner v-if="loading" text="加载中..." />

    <EmptyState
      v-else-if="instruments.length === 0"
      title="暂无仪器"
      description="当前没有符合筛选条件的仪器"
    />

    <div v-else class="instrument-grid">
      <InstrumentCard v-for="item in instruments" :key="item.id" :instrument="item" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getInstruments, type InstrumentRead } from '../../api/instruments'
import InstrumentCard from '../../components/instruments/InstrumentCard.vue'
import InstrumentFilters from '../../components/instruments/InstrumentFilters.vue'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import EmptyState from '../../components/common/EmptyState.vue'
import client from '../../api/client'

interface LabDoc {
  id: string
  title: string
  content: string | null
  file_url: string | null
  created_at: string
}

const instruments = ref<InstrumentRead[]>([])
const notices = ref<LabDoc[]>([])
const loading = ref(true)

let filterParams = { search: '', status: '' }

async function loadInstruments() {
  loading.value = true
  try {
    instruments.value = await getInstruments(filterParams)
  } catch {
    instruments.value = []
  } finally {
    loading.value = false
  }
}

function onFilter(params: { search: string; status: string }) {
  filterParams = params
  loadInstruments()
}

onMounted(async () => {
  try {
    const res = await client.get('/lab-documents')
    notices.value = res.data
  } catch {}
  await loadInstruments()
})
</script>

<style scoped>
.instrument-list-page {
  animation: fadeIn var(--transition-slow) ease;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-lg);
}

.notice-board {
  background: var(--color-warning-bg);
  border: 1px solid var(--color-warning);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  margin-bottom: var(--space-lg);
}

.notice-header {
  font-size: 15px;
  font-weight: 600;
  color: #B45309;
  margin-bottom: var(--space-sm);
}

.notice-item {
  font-size: 13px;
  color: #92400e;
  padding: var(--space-xs) 0;
  display: flex;
  gap: var(--space-md);
}

.notice-title {
  font-weight: 500;
  white-space: nowrap;
}

.notice-content {
  color: #B45309;
}

.instrument-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--space-md);
}
</style>
