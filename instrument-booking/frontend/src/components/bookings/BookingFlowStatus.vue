<template>
  <div class="flow-status">
    <div class="flow-steps">
      <div v-for="(step, i) in steps" :key="i" class="flow-step" :class="{ active: step.active, done: step.done }">
        <div class="step-dot">{{ step.done ? '✓' : step.active ? '●' : '○' }}</div>
        <div class="step-label">{{ step.label }}</div>
      </div>
    </div>
    <div v-if="review" class="flow-detail">
      <div v-if="review.reviewer_id" class="flow-info">审核人已分配</div>
      <div v-if="review.tester_id" class="flow-info">测试老师已分配</div>
      <div v-if="review.reviewer_comment" class="flow-info">审核意见：{{ review.reviewer_comment }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status?: string
  review?: { status: string; reviewer_id?: string | null; tester_id?: string | null; reviewer_comment?: string | null } | null
}>()

const statusMap: Record<string, string> = {
  pending: 'pending_review',
  approved: 'review_approved',
  rejected: 'review_rejected',
  cancelled: 'cancelled',
}

const currentStatus = computed(() => props.review?.status || statusMap[props.status || ''] || 'pending_review')

const steps = computed(() => [
  { label: '提交预约', done: true, active: false },
  { label: '审核中', done: ['review_approved', 'testing', 'completed'].includes(currentStatus.value), active: currentStatus.value === 'pending_review' },
  { label: '测试中', done: currentStatus.value === 'completed', active: currentStatus.value === 'testing' || currentStatus.value === 'review_approved' },
  { label: '已完成', done: false, active: currentStatus.value === 'completed' },
])
</script>

<style scoped>
.flow-steps {
  display: flex;
  gap: 0;
  margin-bottom: 12px;
}
.flow-step {
  flex: 1;
  text-align: center;
  position: relative;
}
.flow-step + .flow-step::before {
  content: '';
  position: absolute;
  top: 12px;
  left: -50%;
  width: 100%;
  height: 2px;
  background: #e2e8f0;
  z-index: 0;
}
.flow-step.done + .flow-step::before { background: #3b82f6; }
.step-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  margin: 0 auto 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  position: relative;
  z-index: 1;
  background: #e2e8f0;
  color: #94a3b8;
}
.flow-step.active .step-dot { background: #3b82f6; color: white; }
.flow-step.done .step-dot { background: #3b82f6; color: white; }
.step-label { font-size: 12px; color: #64748b; }
.flow-step.active .step-label { color: #3b82f6; font-weight: 500; }
.flow-detail { font-size: 13px; color: #475569; padding: 8px 12px; background: #f8fafc; border-radius: 6px; }
.flow-info { margin: 2px 0; }
</style>
