<template>
  <div class="booking-overview">
    <div class="page-header">
      <h2>设备预约总览</h2>
      <div class="cal-nav">
        <button class="btn-nav" @click="prevWeek">‹ 上一周</button>
        <span class="cal-title">{{ calTitle }}</span>
        <button class="btn-nav" @click="nextWeek">下一周 ›</button>
        <button class="btn-today" @click="goToday">今天</button>
      </div>
    </div>

    <LoadingSpinner v-if="loading" text="加载中..." />

    <div v-else class="overview-grid">
      <div class="grid-header">
        <div class="row-label">仪器</div>
        <div v-for="day in weekDays" :key="day.date" class="day-header" :class="{ today: day.isToday }">
          <div class="day-name">{{ day.weekday }}</div>
          <div class="day-date">{{ day.monthDay }}</div>
        </div>
      </div>
      <div v-for="inst in instruments" :key="inst.id" class="grid-row">
        <div class="row-label" :title="inst.name">{{ inst.name }}</div>
        <div v-for="day in weekDays" :key="day.date + '-' + inst.id" class="day-cell" :class="{ today: day.isToday }">
          <div v-if="day.bookings?.[inst.id]" class="booking-list">
            <div v-for="bk in day.bookings[inst.id]" :key="bk.id" class="booking-chip" :class="bk.status">
              <span class="bk-time">{{ formatHour(bk.start_time) }}</span>
              <span class="bk-user">{{ bk.user_name }}</span>
            </div>
          </div>
          <div v-else class="no-booking">-</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import client from '../../api/client'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'

interface BookingItem {
  id: string
  instrument_id: string
  user_name: string
  start_time: string
  end_time: string
  status: string
}

interface DayBookings {
  date: string
  bookings: Record<string, BookingItem[]>
}

const loading = ref(true)
const instruments = ref<{ id: string; name: string }[]>([])
const weekOffset = ref(0)
const weekData = ref<DayBookings[]>([])

const weekDays = computed(() => {
  const start = getWeekStart(weekOffset.value)
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const days: { date: string; weekday: string; monthDay: string; isToday: boolean; bookings: Record<string, BookingItem[]> }[] = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    const dateStr = d.toISOString().split('T')[0]
    const existing = weekData.value.find((wd) => wd.date === dateStr)
    days.push({
      date: dateStr,
      weekday: weekdays[d.getDay()],
      monthDay: `${d.getMonth() + 1}/${d.getDate()}`,
      isToday: d.getTime() === today.getTime(),
      bookings: existing?.bookings || {},
    })
  }
  return days
})

const calTitle = computed(() => {
  const start = weekDays.value[0]
  const end = weekDays.value[6]
  return `${start.date} ~ ${end.date}`
})

function getWeekStart(offset: number): Date {
  const now = new Date()
  const dayOfWeek = now.getDay()
  const monday = new Date(now)
  monday.setDate(now.getDate() - ((dayOfWeek + 6) % 7) + offset * 7)
  monday.setHours(0, 0, 0, 0)
  return monday
}

function prevWeek() { weekOffset.value--; fetchWeek() }
function nextWeek() { weekOffset.value++; fetchWeek() }
function goToday() { weekOffset.value = 0; fetchWeek() }

function formatHour(iso: string): string {
  const d = new Date(iso)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function fetchWeek() {
  loading.value = true
  try {
    const start = getWeekStart(weekOffset.value)
    const end = new Date(start)
    end.setDate(start.getDate() + 6)

    if (instruments.value.length === 0) {
      const instRes = await client.get('/instruments')
      instruments.value = instRes.data.map((i: any) => ({ id: i.id, name: i.name }))
    }

    const res = await client.get('/admin/bookings', {
      params: {
        page: 1,
        per_page: 500,
      },
    })
    const allBookings: any[] = res.data

    const days: DayBookings[] = []
    const today = new Date(start)
    for (let i = 0; i < 7; i++) {
      const d = new Date(today)
      d.setDate(today.getDate() + i)
      const dateStr = d.toISOString().split('T')[0]
      const dayBookings: Record<string, BookingItem[]> = {}

      for (const inst of instruments.value) {
        const bkList = allBookings
          .filter((b: any) => b.instrument_id === inst.id)
          .filter((b: any) => {
            const bs = b.start_time.slice(0, 10)
            return bs === dateStr
          })
          .map((b: any) => ({
            id: b.id,
            instrument_id: b.instrument_id,
            user_name: b.user_full_name || b.user_username || b.user_id.slice(0, 6),
            start_time: b.start_time,
            end_time: b.end_time,
            status: b.status,
          }))
        if (bkList.length > 0) {
          dayBookings[inst.id] = bkList
        }
      }
      days.push({ date: dateStr, bookings: dayBookings })
    }
    weekData.value = days
  } catch {}
  loading.value = false
}

onMounted(fetchWeek)
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.page-header h2 { font-size: 22px; color: #1e293b; margin: 0; }
.cal-nav { display: flex; align-items: center; gap: 8px; }
.btn-nav, .btn-today {
  padding: 6px 14px; background: white; border: 1px solid #d1d5db;
  border-radius: 6px; cursor: pointer; font-size: 13px;
}
.btn-nav:hover, .btn-today:hover { background: #f8fafc; }
.cal-title { font-size: 14px; font-weight: 600; color: #1e293b; min-width: 180px; text-align: center; }

.overview-grid {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}
.grid-header, .grid-row {
  display: grid;
  grid-template-columns: 120px repeat(7, 1fr);
}
.grid-header {
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 56px;
  z-index: 2;
}
.grid-row + .grid-row {
  border-top: 1px solid #f1f5f9;
}
.row-label {
  padding: 8px 10px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  border-right: 1px solid #e2e8f0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.day-header {
  padding: 8px 4px;
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  border-right: 1px solid #e2e8f0;
}
.day-header:last-child { border-right: none; }
.day-header.today { color: #3b82f6; }
.day-name { font-size: 11px; font-weight: 400; color: #94a3b8; }
.day-date { font-size: 13px; }
.day-cell {
  padding: 4px;
  min-height: 60px;
  border-right: 1px solid #f1f5f9;
  background: #fafafa;
}
.day-cell:last-child { border-right: none; }
.day-cell.today { background: #eff6ff; }
.booking-list { display: flex; flex-direction: column; gap: 2px; }
.booking-chip {
  font-size: 11px;
  padding: 2px 4px;
  border-radius: 3px;
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}
.booking-chip.pending { background: #fef9c3; color: #854d0e; }
.booking-chip.approved { background: #dcfce7; color: #166534; }
.booking-chip.rejected { background: #fef2f2; color: #991b1b; }
.booking-chip.cancelled { background: #f1f5f9; color: #64748b; }
.booking-chip.completed { background: #e0e7ff; color: #3730a3; }
.bk-time { font-weight: 500; }
.bk-user { opacity: 0.8; }
.no-booking { color: #e2e8f0; font-size: 12px; text-align: center; padding-top: 20px; }
</style>
