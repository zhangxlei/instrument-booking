<template>
  <div class="booking-overview">
    <div class="page-header">
      <h2>{{ selectedInstrument ? selectedInstrument.name + ' - 预约日历' : '设备预约总览' }}</h2>
      <button v-if="selectedInstrument" class="btn-back" @click="selectedInstrument = null">← 返回列表</button>
    </div>

    <LoadingSpinner v-if="loading" text="加载中..." />

    <!-- Instrument list -->
    <div v-else-if="!selectedInstrument" class="instrument-grid">
      <div v-for="inst in instruments" :key="inst.id" class="instrument-card" @click="selectInstrument(inst)">
        <div class="inst-name">{{ inst.name }}</div>
        <div class="inst-status" :class="inst.status">{{ statusMap[inst.status] || inst.status }}</div>
        <div v-if="inst.manager_name" class="inst-manager">管理人：{{ inst.manager_name }}</div>
        <div v-if="inst.probe_type" class="inst-probe">探针：{{ inst.probe_type }}</div>
      </div>
      <EmptyState v-if="instruments.length === 0" title="暂无仪器" />
    </div>

    <!-- Calendar view for selected instrument -->
    <div v-else class="calendar-section">
      <div class="cal-nav">
        <button class="btn-nav" @click="prevWeek">‹ 上一周</button>
        <span class="cal-title">{{ calTitle }}</span>
        <button class="btn-nav" @click="nextWeek">下一周 ›</button>
        <button class="btn-today" @click="goToday">今天</button>
      </div>

      <div class="calendar-grid">
        <div class="cal-header-row">
          <div class="cal-time-header">时间</div>
          <div v-for="day in weekDays" :key="day.date" class="cal-day-header" :class="{ today: day.isToday }">
            <div class="day-name">{{ day.weekday }}</div>
            <div class="day-date">{{ day.monthDay }}</div>
          </div>
        </div>
        <div v-for="hour in hours" :key="hour" class="cal-row">
          <div class="cal-time">{{ String(hour).padStart(2, '0') }}:00</div>
          <div v-for="day in weekDays" :key="day.date + '-' + hour" class="cal-slot" :class="slotClass(day, hour)">
            <div v-if="getSlotBooking(day.date, hour)" class="slot-info">
              <div class="slot-user">{{ getSlotBooking(day.date, hour)?.user_name }}</div>
              <div class="slot-status">{{ getSlotBooking(day.date, hour)?.status_label }}</div>
            </div>
          </div>
        </div>
      </div>
      <EmptyState v-if="!loading && bookings.length === 0" title="该仪器本周暂无预约" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import client from '../../api/client'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import EmptyState from '../../components/common/EmptyState.vue'

interface InstrumentItem {
  id: string
  name: string
  status: string
  manager_name?: string | null
  probe_type?: string | null
}

interface BookingItem {
  id: string
  instrument_id: string
  user_name: string
  start_time: string
  end_time: string
  status: string
  status_label: string
}

const loading = ref(true)
const instruments = ref<InstrumentItem[]>([])
const selectedInstrument = ref<InstrumentItem | null>(null)
const bookings = ref<BookingItem[]>([])
const weekOffset = ref(0)

const hours = Array.from({ length: 24 }, (_, i) => i)

const statusMap: Record<string, string> = {
  available: '可用', maintenance: '维护中', retired: '已报废',
}

const statusLabel: Record<string, string> = {
  pending: '待审批', approved: '已通过', rejected: '已拒绝',
  cancelled: '已取消', completed: '已完成',
}

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
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const start = new Date(weekStart.value)
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    const dateStr = d.toISOString().split('T')[0]
    return {
      date: dateStr,
      weekday: weekdays[d.getDay()],
      monthDay: `${d.getMonth() + 1}/${d.getDate()}`,
      isToday: d.getTime() === today.getTime(),
    }
  })
})

const calTitle = computed(() => {
  const start = weekDays.value[0]
  const end = weekDays.value[6]
  return `${start.date} ~ ${end.date}`
})

function prevWeek() { weekOffset.value-- }
function nextWeek() { weekOffset.value++ }
function goToday() { weekOffset.value = 0 }

function getSlotBooking(date: string, hour: number): BookingItem | undefined {
  const time = `${String(hour).padStart(2, '0')}:00`
  return bookings.value.find((b) => {
    const bDate = b.start_time.slice(0, 10)
    const bHour = b.start_time.slice(11, 13)
    return bDate === date && bHour === time
  })
}

function slotClass(day: { date: string; isToday: boolean }, hour: number): string {
  const booking = getSlotBooking(day.date, hour)
  if (!booking) return 'empty'
  return booking.status
}

function selectInstrument(inst: InstrumentItem) {
  selectedInstrument.value = inst
  weekOffset.value = 0
}

watch([selectedInstrument, weekOffset], fetchBookings)

async function fetchBookings() {
  if (!selectedInstrument.value) return
  loading.value = true
  try {
    const start = getWeekStart(weekOffset.value)
    const end = new Date(start)
    end.setDate(start.getDate() + 7)
    const res = await client.get('/admin/bookings', {
      params: {
        instrument_id: selectedInstrument.value.id,
        page: 1,
        per_page: 100,
      },
    })
    bookings.value = res.data
      .filter((b: any) => {
        const bs = b.start_time.slice(0, 10)
        const be = b.end_time.slice(0, 10)
        const startStr = start.toISOString().split('T')[0]
        const endStr = end.toISOString().split('T')[0]
        return bs >= startStr && bs < endStr
      })
      .map((b: any) => ({
        id: b.id,
        instrument_id: b.instrument_id,
        user_name: b.user_full_name || b.user_username || b.user_id.slice(0, 6),
        start_time: b.start_time,
        end_time: b.end_time,
        status: b.status,
        status_label: statusLabel[b.status] || b.status,
      }))
  } catch {}
  loading.value = false
}

onMounted(async () => {
  try {
    const res = await client.get('/instruments', { params: { per_page: 100 } })
    instruments.value = res.data.map((i: any) => ({
      id: i.id, name: i.name, status: i.status,
      manager_name: i.manager_name, probe_type: i.probe_type,
    }))
  } catch {}
  loading.value = false
})
</script>

<style scoped>
.page-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
}
.page-header h2 { font-size: 22px; color: #1e293b; margin: 0; }
.btn-back { padding: 8px 16px; background: white; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; font-size: 14px; }

.instrument-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
}
.instrument-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.instrument-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.inst-name { font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 6px; }
.inst-status { font-size: 12px; padding: 2px 8px; border-radius: 10px; display: inline-block; margin-bottom: 6px; }
.inst-status.available { background: #dcfce7; color: #166534; }
.inst-status.maintenance { background: #fef9c3; color: #854d0e; }
.inst-status.retired { background: #f1f5f9; color: #64748b; }
.inst-manager, .inst-probe { font-size: 13px; color: #64748b; }

.cal-nav {
  display: flex; align-items: center; gap: 8px; margin-bottom: 12px;
}
.cal-title { flex: 1; text-align: center; font-size: 14px; font-weight: 600; color: #1e293b; }
.btn-nav, .btn-today {
  padding: 6px 14px; background: white; border: 1px solid #d1d5db;
  border-radius: 6px; cursor: pointer; font-size: 13px;
}
.btn-nav:hover, .btn-today:hover { background: #f8fafc; }

.calendar-grid {
  display: grid;
  grid-template-columns: 60px repeat(7, 1fr);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: auto;
  background: white;
  max-height: 600px;
}
.cal-header-row { display: contents; }
.cal-time-header, .cal-day-header {
  padding: 8px 4px; text-align: center; font-size: 12px;
  background: #f8fafc; border-bottom: 1px solid #e2e8f0;
  font-weight: 600; color: #475569; position: sticky; top: 0; z-index: 2;
}
.cal-day-header.today { color: #3b82f6; }
.day-name { font-size: 11px; color: #94a3b8; font-weight: 400; }
.day-date { font-size: 13px; }
.cal-row { display: contents; }
.cal-time {
  padding: 8px 4px; font-size: 11px; color: #94a3b8;
  text-align: center; border-right: 1px solid #f1f5f9;
  border-bottom: 1px solid #f1f5f9; background: #fafafa;
}
.cal-slot {
  padding: 4px; border-right: 1px solid #f1f5f9;
  border-bottom: 1px solid #f1f5f9; min-height: 36px;
  cursor: default; font-size: 11px;
}
.cal-slot.empty { background: #fafafa; }
.cal-slot.pending { background: #fef9c3; }
.cal-slot.approved { background: #dcfce7; }
.cal-slot.rejected { background: #fef2f2; }
.cal-slot.cancelled { background: #f1f5f9; }
.cal-slot.completed { background: #e0e7ff; }
.slot-info { display: flex; flex-direction: column; gap: 1px; }
.slot-user { font-weight: 500; color: #1e293b; }
.slot-status { font-size: 10px; opacity: 0.7; }
</style>
