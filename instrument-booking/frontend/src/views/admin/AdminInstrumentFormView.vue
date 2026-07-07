<template>
  <div class="admin-form-page">
    <h2>{{ isEdit ? '编辑仪器' : '新增仪器' }}</h2>
    <InstrumentForm
      v-if="ready"
      :instrument-id="instrumentId"
      :initial="initialData"
      @saved="onSaved"
    />
    <div v-if="isEdit && ready" class="delete-section">
      <button class="btn-delete" @click="handleDelete">删除此仪器</button>
    </div>
    <LoadingSpinner v-else text="加载中..." />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getInstrument, deleteInstrument } from '../../api/instruments'
import InstrumentForm from '../../components/instruments/InstrumentForm.vue'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const isEdit = route.name === 'AdminInstrumentEdit'
const instrumentId = route.params.id as string | undefined
const ready = ref(!isEdit)
const initialData = ref<any>(null)

onMounted(async () => {
  if (isEdit && instrumentId) {
    try {
      const inst = await getInstrument(instrumentId)
      initialData.value = inst
    } catch {}
    ready.value = true
  }
})

function onSaved() {
  router.push('/admin/instruments')
}

async function handleDelete() {
  if (!instrumentId || !confirm('确定删除此仪器？此操作不可撤销。')) return
  try {
    await deleteInstrument(instrumentId)
    router.push('/admin/instruments')
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}
</script>

<style scoped>
.admin-form-page {
  max-width: 700px;
  animation: fadeIn var(--transition-slow) ease;
}

.admin-form-page h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-lg);
}

.delete-section {
  margin-top: var(--space-xl);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border);
}

.btn-delete {
  padding: 10px 24px;
  background: var(--color-surface);
  color: var(--color-danger);
  border: 1px solid var(--color-danger-bg);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-delete:hover {
  background: var(--color-danger-bg);
  box-shadow: var(--shadow-sm);
}
</style>
