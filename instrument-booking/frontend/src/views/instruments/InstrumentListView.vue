<template>
  <div class="instrument-list-page">
    <h2 class="page-title">仪器列表</h2>

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

const instruments = ref<InstrumentRead[]>([])
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

onMounted(loadInstruments)
</script>

<style scoped>
.page-title {
  font-size: 22px;
  color: #1e293b;
  margin-bottom: 20px;
}
.instrument-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
</style>
