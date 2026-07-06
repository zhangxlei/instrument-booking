<template>
  <form class="booking-form" @submit.prevent="handleSubmit">
    <ErrorAlert :message="error" />

    <div class="form-group">
      <label>选择日期</label>
      <input v-model="date" type="date" :min="minDate" @change="onDateChange" required />
    </div>

    <div class="form-group">
      <label>开始时间</label>
      <input v-model="startTime" type="time" :min="minStartTime" required />
    </div>

    <div class="form-group">
      <label>结束时间</label>
      <input v-model="endTime" type="time" :min="minEndTime" required />
    </div>

    <div class="form-group">
      <label>使用目的</label>
      <textarea v-model="purpose" placeholder="简述需要使用仪器的目的" rows="2" />
    </div>

    <button type="submit" class="btn-primary" :disabled="loading">
      {{ loading ? '提交中...' : '提交预约' }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { createBooking } from '../../api/bookings'
import ErrorAlert from '../common/ErrorAlert.vue'

const props = defineProps<{
  instrumentId: string
}>()

const emit = defineEmits<{ saved: [] }>()

const date = ref(new Date().toISOString().split('T')[0])
const startTime = ref('09:00')
const endTime = ref('10:00')
const purpose = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

const minDate = computed(() => new Date().toISOString().split('T')[0])
const minStartTime = computed(() => {
  if (date.value === minDate.value) {
    const now = new Date()
    return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  }
  return '00:00'
})
const minEndTime = computed(() => startTime.value || '00:00')

function onDateChange() {
  startTime.value = '09:00'
  endTime.value = '10:00'
}

async function handleSubmit() {
  error.value = null
  loading.value = true
  try {
    await createBooking({
      instrument_id: props.instrumentId,
      start_time: `${date.value}T${startTime.value}:00Z`,
      end_time: `${date.value}T${endTime.value}:00Z`,
      purpose: purpose.value || undefined,
    })
    emit('saved')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '预约失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.booking-form {
  max-width: 400px;
}
.form-group {
  margin-bottom: 14px;
}
.form-group label {
  display: block;
  font-size: 14px;
  color: #374151;
  margin-bottom: 6px;
  font-weight: 500;
}
.form-group input, .form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-group textarea { resize: vertical; }
.btn-primary {
  width: 100%;
  padding: 10px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  cursor: pointer;
  font-weight: 500;
}
.btn-primary:disabled { opacity: 0.6; }
</style>
