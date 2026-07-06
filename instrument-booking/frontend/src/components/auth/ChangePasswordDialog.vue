<template>
  <div v-if="visible" class="dialog-overlay" @click.self="$emit('close')">
    <div class="dialog-box">
      <h3>{{ isAdmin ? '重置用户密码' : '修改密码' }}</h3>
      <ErrorAlert :message="error" />
      <div class="form-group">
        <label>{{ isAdmin ? '新密码' : '原密码' }}</label>
        <input v-model="oldPassword" type="password" :placeholder="isAdmin ? '请输入新密码' : '请输入原密码'" />
      </div>
      <div v-if="!isAdmin" class="form-group">
        <label>新密码</label>
        <input v-model="newPassword" type="password" placeholder="请输入新密码" />
      </div>
      <div class="dialog-actions">
        <button class="btn-cancel" @click="$emit('close')">取消</button>
        <button class="btn-primary" :disabled="!canSubmit" @click="handleSubmit">确认</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { changePassword } from '../../api/auth'
import { adminSetUserPassword } from '../../api/admin'
import ErrorAlert from '../common/ErrorAlert.vue'

const props = defineProps<{
  visible: boolean
  isAdmin?: boolean
  userId?: string
}>()

const emit = defineEmits<{ close: []; saved: [] }>()

const oldPassword = ref('')
const newPassword = ref('')
const error = ref<string | null>(null)

const canSubmit = computed(() => props.isAdmin ? !!oldPassword.value : (!!oldPassword.value && !!newPassword.value))

async function handleSubmit() {
  error.value = null
  try {
    if (props.isAdmin && props.userId) {
      await adminSetUserPassword(props.userId, oldPassword.value)
    } else {
      await changePassword(oldPassword.value, newPassword.value)
    }
    oldPassword.value = ''
    newPassword.value = ''
    emit('saved')
    emit('close')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '操作失败'
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.dialog-box {
  background: white;
  border-radius: 8px;
  padding: 24px;
  width: 360px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.dialog-box h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #1e293b;
}
.form-group {
  margin-bottom: 12px;
}
.form-group label {
  display: block;
  font-size: 13px;
  color: #374151;
  margin-bottom: 4px;
}
.form-group input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
}
.btn-cancel {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}
.btn-primary {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
