<template>
  <div class="booking-calendar">
    <div v-if="instrumentUnavailable" class="unavailable-notice">
      {{ instrumentUnavailable }}
    </div>

    <template v-else>
      <div class="cal-nav">
        <button class="btn-nav" @click="prevWeek">‹ 上一周</button>
        <span class="cal-nav-title">{{ calTitle }}</span>
        <button class="btn-nav" @click="nextWeek">下一周 ›</button>
        <button class="btn-today" @click="goToToday">今天</button>
      </div>

      <div class="calendar-grid">
        <div class="cal-header-row">
          <div class="cal-time-header">时间</div>
          <div v-for="day in weekDays" :key="day.date" class="cal-day-header">
            <div class="day-name">{{ day.weekday }}</div>
            <div class="day-date">{{ day.monthDay }}</div>
          </div>
        </div>
        <div v-for="hour in hours" :key="hour" class="cal-row">
          <div class="cal-time">{{ String(hour).padStart(2, '0') }}:00</div>
          <div
            v-for="day in weekDays"
            :key="day.date + '-' + hour"
            class="cal-slot"
            :class="slotClass(day.date, hour)"
            @click="toggleSlot(day.date, hour)"
          >
            <div v-if="getSlot(day.date, hour)?.booked_by" class="slot-booked-by">
              {{ getSlot(day.date, hour)?.booked_by?.username }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedSlots.length > 0" class="booking-form">
        <div class="selected-info">
          已选择：{{ formatSlotRange(selectedSlots) }}
          <span v-if="estimatedCost" class="cost">预估费用：¥{{ estimatedCost }}</span>
        </div>
        <div class="form-group">
          <label>使用目的</label>
          <textarea v-model="purpose" placeholder="简述需要使用仪器的目的" rows="2" />
        </div>
        <div class="form-group">
          <label>捎话（给测试老师）</label>
          <textarea v-model="message" placeholder="有什么需要告知测试老师的内容" rows="2" />
        </div>
        <div class="form-group">
          <label>选择审核人</label>
          <select v-model="reviewerId">
            <option value="">请选择审核人</option>
            <option v-for="u in userList" :key="u.id" :value="u.id">{{ u.full_name }}({{ u.username }})</option>
          </select>
        </div>
        <div class="form-group">
          <label>测试需求文档（选填）</label>
          <input type="file" ref="docInput" @change="onDocSelect" accept=".pdf,.doc,.docx,.txt,.zip" />
        </div>
        <ErrorAlert :message="error" />
        <div class="form-actions">
          <button class="btn-cancel" @click="clearSelection">取消选择</button>
          <button class="btn-primary" :disabled="submitting" @click="handleSubmit">
            {{ submitting ? '提交中...' : '提交预约' }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { getAvailability } from '../../api/instruments'
import { createBooking } from '../../api/bookings'
import client from '../../api/client'
import ErrorAlert from '../common/ErrorAlert.vue'

interface UserItem {
  id: string
  username: string
  full_name: string
}

const props = defineProps<{
  instrumentId: string
  pricePerHour?: number | null
  instrumentStatus?: string
}>()

const emit = defineEmits<{ saved: [] }>()

interface SlotInfo {
  start: string
  end: string
  available: boolean
  booked_by: { username: string; full_name: string } | null
}

interface DaySlots {
  date: string
  slots: SlotInfo[]
}

const allDays = ref<DaySlots[]>([])
const loading = ref(true)
const selectedSlots = ref<{ date: string; hour: number }[]>([])
const purpose = ref('')
const message = ref('')
const reviewerId = ref('')
const userList = ref<UserItem[]>([])
const docFile = ref<File | null>(null)
const submitting = ref(false)
const error = ref<string | null>(null)
const shiftAnchor = ref<{ date: string; hour: number } | null>(null)
const weekOffset = ref(0)

const hours = Array.from({ length: 24 }, (_, i) => i)

const instrumentUnavailable = computed(() => {
  if (props.instrumentStatus === 'maintenance') return '该仪器当前处于维护中，暂不可预约'
  if (props.instrumentStatus === 'retired') return '该仪器已报废，不可预约'
  return ''
})

function getWeekStart(offset: number): Date {
  const now = new Date()
  const dayOfWeek = now.getDay()
  const monday = new Date(now)
  monday.setDate(now.getDate() - ((dayOfWeek + 6) % 7) + offset * 7)
  monday.setHours(0, 0, 0, 0)
  return monday
}

const weekStart = computed(() => getWeekStart(weekOffset.value))

const weekDays = computed(() => {
  const days: { date: string; weekday: string; monthDay: string }[] = []
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const start = new Date(weekStart.value)
  for (let i = 0; i < 7; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    const dateStr = d.toISOString().split('T')[0]
    days.push({
      date: dateStr,
      weekday: weekdays[d.getDay()],
      monthDay: `${d.getMonth() + 1}/${d.getDate()}`,
    })
  }
  return days
})

const calTitle = computed(() => {
  const start = weekDays.value[0]
  const end = weekDays.value[6]
  return `${start.date} ~ ${end.date}`
})

function prevWeek() {
  weekOffset.value--
}

function nextWeek() {
  weekOffset.value++
}

function goToToday() {
  weekOffset.value = 0
}

const daysToFetch = computed(() => {
  const start = weekStart.value
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  if (start <= today) {
    return 7
  }
  const maxDate = new Date(2030, 0, 1)
  const diff = Math.ceil((end.getTime() - today.getTime()) / 86400000)
  return Math.min(diff + 1, 3650)
})

async function fetchAvailability() {
  loading.value = true
  try {
    const days = daysToFetch.value
    allDays.value = await getAvailability(props.instrumentId, days)
  } catch {}
  loading.value = false
}

watch(weekOffset, fetchAvailability)

function getSlot(date: string, hour: number): SlotInfo | undefined {
  const day = allDays.value.find((d) => d.date === date)
  if (!day) return undefined
  const time = `${String(hour).padStart(2, '0')}:00`
  return day.slots.find((s) => s.start === time)
}

function slotClass(date: string, hour: number): string {
  if (instrumentUnavailable.value) return 'hidden'
  const slot = getSlot(date, hour)
  if (!slot) return 'hidden'
  if (!slot.available) return 'booked'
  const isSelected = selectedSlots.value.some((s) => s.date === date && s.hour === hour)
  if (isSelected) return 'selected'
  return 'available'
}

function toggleSlot(date: string, hour: number) {
  if (instrumentUnavailable.value) return
  const slot = getSlot(date, hour)
  if (!slot || !slot.available) return

  const index = selectedSlots.value.findIndex((s) => s.date === date && s.hour === hour)
  if (index >= 0) {
    selectedSlots.value.splice(index, 1)
    return
  }

  if (shiftAnchor.value) {
    const sorted = sortSlots([shiftAnchor.value, { date, hour }])
    const newSlots: { date: string; hour: number }[] = []
    for (const d of allDays.value) {
      for (const h of hours) {
        const s = getSlot(d.date, h)
        if (!s || !s.available) continue
        const pos = { date: d.date, hour: h }
        if (compareSlots(pos, sorted[0]) >= 0 && compareSlots(pos, sorted[1]) <= 0) {
          if (!selectedSlots.value.some((sel) => sel.date === d.date && sel.hour === h)) {
            newSlots.push(pos)
          }
        }
      }
    }
    selectedSlots.value.push(...newSlots)
    shiftAnchor.value = null
  } else {
    shiftAnchor.value = { date, hour }
    selectedSlots.value.push({ date, hour })
  }
}

function sortSlots(slots: { date: string; hour: number }[]): { date: string; hour: number }[] {
  return [...slots].sort((a, b) => {
    if (a.date !== b.date) return a.date.localeCompare(b.date)
    return a.hour - b.hour
  })
}

function compareSlots(a: { date: string; hour: number }, b: { date: string; hour: number }): number {
  if (a.date !== b.date) return a.date.localeCompare(b.date)
  return a.hour - b.hour
}

const selectedRange = computed(() => {
  if (selectedSlots.value.length === 0) return null
  const sorted = sortSlots(selectedSlots.value)
  const first = sorted[0]
  const last = sorted[sorted.length - 1]
  return {
    start: `${first.date}T${String(first.hour).padStart(2, '0')}:00:00Z`,
    end: `${last.date}T${String(last.hour + 1).padStart(2, '0')}:00:00Z`,
  }
})

const estimatedCost = computed(() => {
  if (!props.pricePerHour || !selectedRange.value) return null
  const start = new Date(selectedRange.value.start)
  const end = new Date(selectedRange.value.end)
  const hours = (end.getTime() - start.getTime()) / 3600000
  return (hours * props.pricePerHour).toFixed(2)
})

function formatSlotRange(slots: { date: string; hour: number }[]): string {
  const sorted = sortSlots(slots)
  if (sorted.length === 0) return ''
  const first = sorted[0]
  const last = sorted[sorted.length - 1]
  const fmt = (d: string) => {
    const dt = new Date(d + 'T00:00:00')
    return `${dt.getMonth() + 1}/${dt.getDate()}`
  }
  return `${fmt(first.date)} ${String(first.hour).padStart(2, '0')}:00 ~ ${fmt(last.date)} ${String(last.hour + 1).padStart(2, '0')}:00`
}

function clearSelection() {
  selectedSlots.value = []
  shiftAnchor.value = null
  purpose.value = ''
  message.value = ''
  reviewerId.value = ''
  docFile.value = null
}

function onDocSelect(e: Event) {
  const target = e.target as HTMLInputElement
  docFile.value = target.files?.[0] || null
}

async function handleSubmit() {
  if (!selectedRange.value) return
  error.value = null
  submitting.value = true
  try {
    const booking = await createBooking({
      instrument_id: props.instrumentId,
      start_time: selectedRange.value.start,
      end_time: selectedRange.value.end,
      purpose: purpose.value || undefined,
      message: message.value || undefined,
      reviewer_id: reviewerId.value || undefined,
    })
    if (docFile.value && booking.id) {
      const formData = new FormData()
      formData.append('file', docFile.value)
      await client.post(`/bookings/${booking.id}/documents`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    }
    clearSelection()
    emit('saved')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '预约失败，请重试'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await fetchAvailability()
  try {
    const res = await client.get('/auth/users')
    userList.value = res.data
  } catch {}
})
</script>

<style scoped>
.unavailable-notice {
  padding: 20px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  text-align: center;
  font-size: 15px;
}
.cal-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.cal-nav-title {
  flex: 1;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}
.btn-nav, .btn-today {
  padding: 6px 14px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}
.btn-nav:hover, .btn-today:hover {
  background: #f8fafc;
}
.calendar-grid {
  display: grid;
  grid-template-columns: 60px repeat(7, 1fr);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: visible;
  background: white;
}
.cal-header-row {
  display: contents;
}
.cal-time-header, .cal-day-header {
  padding: 8px 4px;
  text-align: center;
  font-size: 12px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 600;
  color: #475569;
  position: sticky;
  top: 0;
  z-index: 2;
}
.day-name { font-size: 11px; color: #94a3b8; font-weight: 400; }
.day-date { font-size: 13px; }
.cal-row { display: contents; }
.cal-time {
  padding: 8px 4px;
  font-size: 11px;
  color: #94a3b8;
  text-align: center;
  border-right: 1px solid #f1f5f9;
  border-bottom: 1px solid #f1f5f9;
  background: #fafafa;
}
.cal-slot {
  padding: 2px 4px;
  border-right: 1px solid #f1f5f9;
  border-bottom: 1px solid #f1f5f9;
  min-height: 24px;
  cursor: default;
  font-size: 10px;
  line-height: 1.2;
  transition: background 0.1s;
}
.cal-slot.available { background: #f0fdf4; cursor: pointer; }
.cal-slot.available:hover { background: #bbf7d0; }
.cal-slot.booked { background: #f1f5f9; cursor: not-allowed; }
.cal-slot.selected { background: #93c5fd; cursor: pointer; }
.cal-slot.hidden { background: #fafafa; }
.slot-booked-by {
  font-size: 10px;
  color: #94a3b8;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.booking-form {
  margin-top: 20px;
  padding: 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}
.selected-info {
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 12px;
  font-weight: 500;
}
.cost { margin-left: 12px; color: #059669; font-weight: 600; }
.form-group { margin-bottom: 12px; }
.form-group label {
  display: block;
  font-size: 14px;
  color: #374151;
  margin-bottom: 6px;
  font-weight: 500;
}
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  resize: vertical;
}
.form-actions { display: flex; gap: 8px; }
.btn-primary {
  padding: 8px 24px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
}
.btn-primary:disabled { opacity: 0.6; }
.btn-cancel {
  padding: 8px 24px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}
</style>
