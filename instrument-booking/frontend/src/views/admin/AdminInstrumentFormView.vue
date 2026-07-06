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
}
.delete-section { margin-top: 24px; padding-top: 16px; border-top: 1px solid #e2e8f0; }
.btn-delete {
  padding: 8px 24px;
  background: white;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}
.btn-delete:hover { background: #fef2f2; }
.admin-form-page h2 {
  font-size: 22px;
  color: #1e293b;
  margin-bottom: 20px;
}
</style>
