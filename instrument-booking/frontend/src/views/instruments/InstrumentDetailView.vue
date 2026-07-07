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
.detail-page {
  max-width: 900px;
  animation: fadeIn var(--transition-slow) ease;
}

.btn-back {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  padding: 0;
  margin-bottom: var(--space-md);
  transition: color var(--transition-fast);
}

.btn-back:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.detail-card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.detail-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.detail-header h1 {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text);
}

.instrument-img {
  max-width: 100%;
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-lg);
  max-height: 320px;
  object-fit: cover;
}

.status-badge {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-weight: 500;
}

.status-badge.available { 
  background: var(--color-success-bg); 
  color: #047857; 
}

.status-badge.maintenance { 
  background: var(--color-warning-bg); 
  color: #B45309; 
}

.status-badge.retired { 
  background: var(--color-bg); 
  color: var(--color-text-secondary); 
}

.detail-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.info-row {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.label {
  color: var(--color-text-muted);
  margin-right: var(--space-sm);
  font-weight: 500;
}

.price {
  color: var(--color-success);
  font-weight: 600;
}

.detail-section {
  margin-top: var(--space-lg);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border-light);
}

.detail-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 var(--space-md);
}

.detail-section p {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.hint {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-md);
}

.no-data {
  font-size: 14px;
  color: var(--color-text-muted);
}

.my-bookings {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.my-booking-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.my-booking-item:hover {
  background: var(--color-primary-50);
}

.booking-info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex: 1;
}

.booking-time {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.booking-purpose {
  font-size: 13px;
  color: var(--color-text-muted);
}

.booking-actions {
  display: flex;
  gap: var(--space-xs);
}

.btn-modify,
.btn-cancel {
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  background: var(--color-surface);
  transition: all var(--transition-fast);
}

.btn-modify {
  color: var(--color-primary);
  border-color: var(--color-primary-100);
}

.btn-modify:hover {
  background: var(--color-primary-50);
}

.btn-cancel {
  color: var(--color-danger);
  border-color: var(--color-danger-bg);
}

.btn-cancel:hover {
  background: var(--color-danger-bg);
}

.attachment-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.attachment-list li {
  padding: var(--space-sm) 0;
  font-size: 14px;
  border-bottom: 1px solid var(--color-border-light);
}

.attachment-list li:last-child {
  border-bottom: none;
}

.attachment-list a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.attachment-list a:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.file-size {
  color: var(--color-text-muted);
  margin-left: var(--space-xs);
  font-size: 12px;
}

.error-msg {
  text-align: center;
  color: var(--color-danger);
  padding: var(--space-2xl);
  font-size: 16px;
}
</style>
