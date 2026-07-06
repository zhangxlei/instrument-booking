<template>
  <div class="detail-page">
    <button class="btn-back" @click="$router.push('/instruments')">← 返回列表</button>

    <LoadingSpinner v-if="loading" text="加载中..." />

    <div v-else-if="error" class="error-msg">{{ error }}</div>

    <div v-else-if="instrument" class="detail-card">
      <div class="detail-header">
        <h1>{{ instrument.name }}</h1>
        <span class="status-badge" :class="instrument.status">{{ statusText }}</span>
      </div>

      <img v-if="instrument.image_url" :src="instrument.image_url" class="instrument-img" alt="仪器图片" />

      <div class="detail-info">
        <div class="info-row"><span class="label">位置</span><span>{{ instrument.location || '-' }}</span></div>
        <div class="info-row"><span class="label">预约审批</span><span>{{ instrument.requires_approval ? '需要审批' : '自动批准' }}</span></div>
        <div v-if="instrument.price_per_hour" class="info-row"><span class="label">价格</span><span class="price">¥{{ instrument.price_per_hour }}/小时</span></div>
        <div v-if="instrument.manager_name" class="info-row"><span class="label">管理人</span><span>{{ instrument.manager_name }}{{ instrument.manager_phone ? '（' + instrument.manager_phone + '）' : '' }}</span></div>
        <div v-if="instrument.probe_type" class="info-row"><span class="label">探针类型</span><span>{{ instrument.probe_type }}</span></div>
      </div>

      <div v-if="instrument.description" class="detail-section">
        <h3>描述</h3>
        <p>{{ instrument.description }}</p>
      </div>

      <div class="detail-section">
        <h3>预约日历</h3>
        <p class="hint">选择可用时间段，按 Shift 可连续选择，可跨天</p>
        <BookingCalendar
          :instrument-id="instrument.id"
          :price-per-hour="instrument.price_per_hour"
          :instrument-status="instrument.status"
          @saved="onBookingSaved"
        />
      </div>

      <div class="detail-section">
        <h3>我的预约（本仪器）</h3>
        <LoadingSpinner v-if="myBookingsLoading" text="加载中..." />
        <div v-else-if="myBookings.length === 0" class="no-data">暂无预约记录</div>
        <div v-else class="my-bookings">
          <div v-for="b in myBookings" :key="b.id" class="my-booking-item">
            <div class="booking-info">
              <StatusBadge :status="b.status" />
              <span class="booking-time">{{ formatTime(b.start_time) }} ~ {{ formatTime(b.end_time) }}</span>
              <span v-if="b.purpose" class="booking-purpose">{{ b.purpose }}</span>
            </div>
            <div class="booking-actions">
              <button
                v-if="b.status === 'pending' || b.status === 'approved'"
                class="btn-modify"
                @click="startModify(b)"
              >修改时间</button>
              <button
                v-if="b.status === 'pending' || b.status === 'approved'"
                class="btn-cancel"
                @click="handleCancel(b.id)"
              >取消</button>
            </div>
          </div>
        </div>
      </div>

      <div class="detail-section">
        <h3>附件</h3>
        <div v-if="attachments.length === 0" class="no-data">暂无附件</div>
        <ul v-else class="attachment-list">
          <li v-for="att in attachments" :key="att.id">
            <a :href="getAttachmentUrl(instrument.id, att.id)" target="_blank">{{ att.original_filename }}</a>
            <span class="file-size">({{ (att.file_size / 1024).toFixed(1) }} KB)</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getInstrument, getAttachments, getAttachmentUrl, type AttachmentInfo, type InstrumentRead } from '../../api/instruments'
import { getBookings, cancelBooking, updateBooking, type BookingRead } from '../../api/bookings'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import BookingCalendar from '../../components/bookings/BookingCalendar.vue'
import StatusBadge from '../../components/common/StatusBadge.vue'

const route = useRoute()
const router = useRouter()
const instrument = ref<InstrumentRead | null>(null)
const attachments = ref<AttachmentInfo[]>([])
const myBookings = ref<BookingRead[]>([])
const loading = ref(true)
const myBookingsLoading = ref(true)
const error = ref<string | null>(null)

async function loadMyBookings() {
  myBookingsLoading.value = true
  try {
    const all = await getBookings(undefined)
    myBookings.value = all.filter((b) => b.instrument_id === route.params.id as string)
  } catch {
    myBookings.value = []
  } finally {
    myBookingsLoading.value = false
  }
}

function onBookingSaved() {
  loadMyBookings()
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function handleCancel(bookingId: string) {
  if (!confirm('确定取消这个预约？')) return
  try {
    await cancelBooking(bookingId)
    await loadMyBookings()
  } catch {}
}

function startModify(booking: BookingRead) {
  const newStart = prompt('修改开始时间 (格式: MM/DD HH:MM)：', formatTime(booking.start_time))
  if (!newStart) return
  const newEnd = prompt('修改结束时间 (格式: MM/DD HH:MM)：', formatTime(booking.end_time))
  if (!newEnd) return

  const now = new Date()
  const startParts = newStart.split(/[\/ ]/)
  const endParts = newEnd.split(/[\/ ]/)
  const year = now.getFullYear()

  const startDt = new Date(`${year}-${startParts[0]}-${startParts[1]}T${startParts[2]}:00`)
  const endDt = new Date(`${year}-${endParts[0]}-${endParts[1]}T${endParts[2]}:00`)

  updateBooking(booking.id, {
    start_time: startDt.toISOString(),
    end_time: endDt.toISOString(),
  }).then(() => {
    loadMyBookings()
  }).catch((e) => {
    alert(e.response?.data?.detail || '修改失败')
  })
}

const statusText = computed(() => {
  const map: Record<string, string> = {
    available: '可用',
    maintenance: '维护中',
    retired: '已报废',
  }
  return map[instrument.value?.status || ''] || instrument.value?.status || ''
})

onMounted(async () => {
  try {
    const id = route.params.id as string
    instrument.value = await getInstrument(id)
    attachments.value = await getAttachments(id)
    await loadMyBookings()
  } catch {
    error.value = '加载仪器信息失败'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page { max-width: 900px; }
.btn-back { background: none; border: none; color: #3b82f6; cursor: pointer; font-size: 14px; padding: 0; margin-bottom: 16px; }
.btn-back:hover { text-decoration: underline; }
.detail-card { background: white; border-radius: 8px; padding: 24px; border: 1px solid #e2e8f0; }
.detail-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.detail-header h1 { font-size: 22px; margin: 0; color: #1e293b; }
.instrument-img { max-width: 100%; border-radius: 8px; margin-bottom: 16px; max-height: 300px; object-fit: cover; }
.status-badge { font-size: 12px; padding: 2px 8px; border-radius: 10px; font-weight: 500; }
.status-badge.available { background: #dcfce7; color: #166534; }
.status-badge.maintenance { background: #fef9c3; color: #854d0e; }
.status-badge.retired { background: #f1f5f9; color: #64748b; }
.detail-info { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
.info-row { font-size: 14px; color: #475569; }
.label { color: #94a3b8; margin-right: 8px; }
.price { color: #059669; font-weight: 600; }
.detail-section { margin-top: 20px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
.detail-section h3 { font-size: 16px; color: #1e293b; margin: 0 0 12px; }
.detail-section p { font-size: 14px; color: #475569; line-height: 1.6; }
.hint { font-size: 13px; color: #94a3b8; margin-bottom: 12px; }
.no-data { font-size: 14px; color: #94a3b8; }
.my-bookings { display: flex; flex-direction: column; gap: 8px; }
.my-booking-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 12px; background: #f8fafc; border-radius: 6px;
}
.booking-info { display: flex; align-items: center; gap: 8px; flex: 1; }
.booking-time { font-size: 13px; color: #475569; }
.booking-purpose { font-size: 13px; color: #94a3b8; }
.booking-actions { display: flex; gap: 6px; }
.btn-modify, .btn-cancel {
  padding: 4px 12px; border-radius: 4px; border: 1px solid; cursor: pointer; font-size: 12px; background: white;
}
.btn-modify { color: #3b82f6; border-color: #bfdbfe; }
.btn-cancel { color: #dc2626; border-color: #fecaca; }
.attachment-list { list-style: none; padding: 0; margin: 0; }
.attachment-list li { padding: 6px 0; font-size: 14px; }
.attachment-list a { color: #3b82f6; text-decoration: none; }
.file-size { color: #94a3b8; margin-left: 4px; }
.error-msg { text-align: center; color: #dc2626; padding: 48px; font-size: 16px; }
</style>
