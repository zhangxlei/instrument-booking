<template>
  <div class="admin-bookings">
    <div class="page-header">
      <h2>预约管理</h2>
      <div class="header-actions">
        <button class="btn-book-for" @click="showBookForDialog = true">+ 代外部客户预约</button>
        <button class="btn-export" @click="handleExport">导出 Excel</button>
      </div>
    </div>

    <div v-if="pending.length > 0" class="section">
      <h3>待审批（{{ pending.length }}）</h3>
      <BookingApprovalTable
        :bookings="pending"
        :processing="processing"
        @approve="handleApprove"
        @reject="handleReject"
      />
    </div>
    <div v-else class="section">
      <h3>待审批</h3>
      <EmptyState title="暂无待审批预约" />
    </div>

    <ConfirmDialog
      :visible="showRejectDialog"
      title="拒绝预约"
      :message="'请输入拒绝原因'"
      confirm-text="确认拒绝"
      :danger="true"
      @confirm="confirmReject"
      @cancel="showRejectDialog = false"
    />

    <div class="section">
      <h3>全部预约</h3>
      <div v-if="allBookings.length > 0" class="batch-bar">
        <label class="checkbox-label">
          <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" /> 全选
        </label>
        <span class="selected-count">已选 {{ selectedIds.length }} 项</span>
        <button class="btn-batch-cancel" :disabled="selectedIds.length === 0" @click="handleBatchCancel">批量取消</button>
      </div>
      <LoadingSpinner v-if="loading" text="加载中..." />
      <table v-else-if="allBookings.length > 0" class="data-table">
        <thead>
          <tr><th style="width:36px"></th><th>用户</th><th>仪器</th><th>时间段</th><th>目的</th><th>状态</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="b in allBookings" :key="b.id" :class="{ 'row-selected': selectedIds.includes(b.id) }">
            <td><input type="checkbox" :checked="selectedIds.includes(b.id)" @change="toggleSelect(b.id)" /></td>
            <td>{{ b.user_full_name || b.user_username || b.user_id.slice(0, 8) }}</td>
            <td>{{ b.instrument_name || b.instrument_id.slice(0, 8) }}</td>
            <td>{{ formatTime(b.start_time) }} ~ {{ formatTime(b.end_time) }}</td>
            <td>{{ b.purpose || '-' }}</td>
            <td><StatusBadge :status="b.status" /></td>
            <td class="actions">
              <button class="btn-modify" @click="startReschedule(b)">改期</button>
              <button class="btn-cancel" @click="handleAdminCancel(b.id)">取消</button>
            </td>
          </tr>
        </tbody>
      </table>
      <EmptyState v-else title="暂无预约记录" />
    </div>

    <!-- Reschedule Dialog -->
    <div v-if="rescheduleTarget" class="dialog-overlay" @click.self="rescheduleTarget = null">
      <div class="dialog">
        <h3>修改预约时间</h3>
        <p>用户：{{ rescheduleTarget.user_full_name || rescheduleTarget.user_username }}</p>
        <div class="form-group">
          <label>开始时间</label>
          <input v-model="rescheduleStart" type="datetime-local" />
        </div>
        <div class="form-group">
          <label>结束时间</label>
          <input v-model="rescheduleEnd" type="datetime-local" />
        </div>
        <div class="form-actions">
          <button class="btn-cancel" @click="rescheduleTarget = null">取消</button>
          <button class="btn-primary" @click="confirmReschedule">确认改期</button>
        </div>
      </div>
    </div>

    <!-- Book for Others Dialog -->
    <div v-if="showBookForDialog" class="dialog-overlay" @click.self="showBookForDialog = false">
      <div class="dialog">
        <h3>代外部客户预约</h3>
        <div class="form-group">
          <label>选择用户</label>
          <select v-model="bookForUserId">
            <option value="">请选择用户</option>
            <option v-for="u in users" :key="u.id" :value="u.id">{{ u.full_name }}({{ u.username }})</option>
          </select>
        </div>
        <div class="form-group">
          <label>选择仪器</label>
          <select v-model="bookForInstrumentId">
            <option value="">请选择仪器</option>
            <option v-for="inst in instruments" :key="inst.id" :value="inst.id">{{ inst.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>开始时间</label>
          <input v-model="bookForStart" type="datetime-local" />
        </div>
        <div class="form-group">
          <label>结束时间</label>
          <input v-model="bookForEnd" type="datetime-local" />
        </div>
        <div class="form-group">
          <label>使用目的</label>
          <textarea v-model="bookForPurpose" rows="2" />
        </div>
        <div class="form-actions">
          <button class="btn-cancel" @click="showBookForDialog = false">取消</button>
          <button class="btn-primary" :disabled="bookForSubmitting" @click="confirmBookFor">
            {{ bookForSubmitting ? '提交中...' : '确认预约' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAdminBookings, approveBooking, rejectBooking, adminRescheduleBooking, adminCancelBooking, adminCreateBooking, exportBookingsExcel, batchCancelBookings, getUsers, type UserAdmin } from '../../api/admin'
import { getInstruments, type InstrumentRead } from '../../api/instruments'
import type { BookingRead } from '../../api/bookings'
import BookingApprovalTable from '../../components/admin/BookingApprovalTable.vue'
import ConfirmDialog from '../../components/common/ConfirmDialog.vue'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import EmptyState from '../../components/common/EmptyState.vue'
import StatusBadge from '../../components/common/StatusBadge.vue'

const pending = ref<BookingRead[]>([])
const allBookings = ref<BookingRead[]>([])
const users = ref<UserAdmin[]>([])
const instruments = ref<InstrumentRead[]>([])
const loading = ref(true)
const processing = ref(false)
const showRejectDialog = ref(false)
const selectedBooking = ref<BookingRead | null>(null)

// Reschedule
const rescheduleTarget = ref<BookingRead | null>(null)
const rescheduleStart = ref('')
const rescheduleEnd = ref('')

// Book for others
const showBookForDialog = ref(false)
const bookForUserId = ref('')
const bookForInstrumentId = ref('')
const bookForStart = ref('')
const bookForEnd = ref('')
const bookForPurpose = ref('')
const bookForSubmitting = ref(false)

// Batch cancel
const selectedIds = ref<string[]>([])
const selectAll = ref(false)

function toggleSelect(id: string) {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

function toggleSelectAll() {
  if (selectAll.value) {
    selectedIds.value = allBookings.value.map((b) => b.id)
  } else {
    selectedIds.value = []
  }
}

async function handleBatchCancel() {
  if (!confirm(`确定取消选中的 ${selectedIds.value.length} 条预约？`)) return
  try {
    await batchCancelBookings(selectedIds.value)
    selectedIds.value = []
    selectAll.value = false
    await load()
  } catch (e: any) {
    alert(e.response?.data?.detail || '批量取消失败')
  }
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function load() {
  loading.value = true
  try {
    const [p, all] = await Promise.all([
      getAdminBookings({ status: 'pending' }),
      getAdminBookings(),
    ])
    pending.value = p
    allBookings.value = all
    const [u, inst] = await Promise.all([getUsers(), getInstruments()])
    users.value = u
    instruments.value = inst
  } catch {}
  loading.value = false
}

async function handleApprove(id: string) {
  processing.value = true
  try {
    await approveBooking(id)
    await load()
  } finally { processing.value = false }
}

function handleReject(booking: BookingRead) {
  selectedBooking.value = booking
  showRejectDialog.value = true
}

async function confirmReject() {
  if (!selectedBooking.value) return
  const reason = prompt('请输入拒绝原因：')
  if (!reason) return
  processing.value = true
  try {
    await rejectBooking(selectedBooking.value.id, reason)
    showRejectDialog.value = false
    await load()
  } finally { processing.value = false }
}

function startReschedule(booking: BookingRead) {
  rescheduleTarget.value = booking
  rescheduleStart.value = new Date(booking.start_time).toISOString().slice(0, 16)
  rescheduleEnd.value = new Date(booking.end_time).toISOString().slice(0, 16)
}

async function confirmReschedule() {
  if (!rescheduleTarget.value || !rescheduleStart.value || !rescheduleEnd.value) return
  try {
    await adminRescheduleBooking(rescheduleTarget.value.id, {
      start_time: new Date(rescheduleStart.value).toISOString(),
      end_time: new Date(rescheduleEnd.value).toISOString(),
    })
    rescheduleTarget.value = null
    await load()
  } catch (e: any) {
    alert(e.response?.data?.detail || '改期失败')
  }
}

async function handleAdminCancel(id: string) {
  if (!confirm('确定取消该预约？')) return
  try {
    await adminCancelBooking(id)
    await load()
  } catch {}
}

async function confirmBookFor() {
  if (!bookForUserId.value || !bookForInstrumentId.value || !bookForStart.value || !bookForEnd.value) return
  bookForSubmitting.value = true
  try {
    await adminCreateBooking({
      user_id: bookForUserId.value,
      instrument_id: bookForInstrumentId.value,
      start_time: new Date(bookForStart.value).toISOString(),
      end_time: new Date(bookForEnd.value).toISOString(),
      purpose: bookForPurpose.value || undefined,
    })
    showBookForDialog.value = false
    bookForUserId.value = ''
    bookForInstrumentId.value = ''
    bookForStart.value = ''
    bookForEnd.value = ''
    bookForPurpose.value = ''
    await load()
  } catch (e: any) {
    alert(e.response?.data?.detail || '预约失败')
  } finally {
    bookForSubmitting.value = false
  }
}

async function handleExport() {
  try {
    await exportBookingsExcel()
  } catch (e: any) {
    alert(e.response?.data?.detail || '导出失败')
  }
}

onMounted(load)
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.page-header h2 { margin: 0; }
h2 { font-size: 22px; color: #1e293b; }
.header-actions { display: flex; gap: 8px; }
.btn-export {
  padding: 8px 20px;
  background: white;
  color: #3b82f6;
  border: 1px solid #3b82f6;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}
.btn-book-for {
  padding: 8px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}
.section { margin-bottom: 32px; }
.section h3 { font-size: 16px; margin: 0 0 12px; color: #475569; }
.batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
}
.checkbox-label { cursor: pointer; user-select: none; }
.selected-count { color: #64748b; }
.btn-batch-cancel {
  padding: 4px 12px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.btn-batch-cancel:disabled { opacity: 0.5; cursor: not-allowed; }
.row-selected { background: #eff6ff; }
.data-table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; }
.data-table th { background: #f8fafc; padding: 10px 12px; text-align: left; font-size: 13px; color: #64748b; font-weight: 600; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 10px 12px; font-size: 13px; border-bottom: 1px solid #f1f5f9; }
.actions { display: flex; gap: 4px; }
.btn-modify, .btn-cancel { padding: 4px 10px; border-radius: 4px; border: 1px solid; cursor: pointer; font-size: 12px; background: white; }
.btn-modify { color: #3b82f6; border-color: #bfdbfe; }
.btn-cancel { color: #dc2626; border-color: #fecaca; }
.dialog-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.3);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.dialog {
  background: white; border-radius: 8px; padding: 24px; width: 420px; max-width: 90vw;
}
.dialog h3 { margin: 0 0 16px; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; font-size: 13px; color: #374151; margin-bottom: 4px; font-weight: 500; }
.form-group input, .form-group textarea {
  width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; box-sizing: border-box;
}
.form-group textarea { resize: vertical; }
.form-actions { display: flex; gap: 8px; margin-top: 16px; }
.btn-primary {
  padding: 8px 20px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;
}
.btn-primary:disabled { opacity: 0.6; }
.btn-cancel { padding: 8px 20px; background: white; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; }
</style>
