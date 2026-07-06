<template>
  <div v-if="visible" class="dialog-overlay" @click.self="$emit('cancel')">
    <div class="dialog-box">
      <p class="dialog-title">{{ title }}</p>
      <p v-if="message" class="dialog-msg">{{ message }}</p>
      <div class="dialog-actions">
        <button class="btn-cancel" @click="$emit('cancel')">取消</button>
        <button class="btn-confirm" :class="{ danger }" @click="$emit('confirm')">
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  title: string
  message?: string
  confirmText?: string
  danger?: boolean
}>()

defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.dialog-box {
  background: white;
  border-radius: 8px;
  padding: 24px;
  width: 360px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}
.dialog-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px;
}
.dialog-msg {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 20px;
}
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.btn-cancel, .btn-confirm {
  padding: 8px 20px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: white;
  cursor: pointer;
  font-size: 14px;
}
.btn-confirm {
  background: #3b82f6;
  color: white;
  border: none;
}
.btn-confirm.danger {
  background: #dc2626;
}
</style>
