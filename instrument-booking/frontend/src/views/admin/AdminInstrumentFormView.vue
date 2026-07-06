<template>
  <div class="admin-form-page">
    <h2>{{ isEdit ? '编辑仪器' : '新增仪器' }}</h2>
    <InstrumentForm
      v-if="ready"
      :instrument-id="instrumentId"
      :initial="initialData"
      @saved="onSaved"
    />
    <LoadingSpinner v-else text="加载中..." />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getInstrument } from '../../api/instruments'
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
</script>

<style scoped>
.admin-form-page {
  max-width: 700px;
}
.admin-form-page h2 {
  font-size: 22px;
  color: #1e293b;
  margin-bottom: 20px;
}
</style>
