<template>
  <form class="auth-form" @submit.prevent="handleSubmit">
    <ErrorAlert :message="error" />
    <div class="form-group">
      <label>用户名</label>
      <input v-model="form.username" placeholder="请输入用户名" required />
    </div>
    <div class="form-group">
      <label>姓名</label>
      <input v-model="form.fullName" placeholder="请输入真实姓名" required />
    </div>
    <div class="form-group">
      <label>密码</label>
      <input v-model="form.password" type="password" placeholder="请输入密码（至少 6 位）" required />
    </div>
    <button type="submit" class="btn-primary" :disabled="loading">
      {{ loading ? '注册中...' : '注册' }}
    </button>
    <p class="form-footer">
      已有账号？<router-link to="/login">立即登录</router-link>
    </p>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { register } from '../../api/auth'
import ErrorAlert from '../common/ErrorAlert.vue'

const router = useRouter()
const authStore = useAuthStore()
const error = ref<string | null>(null)
const loading = ref(false)
const form = reactive({
  username: '',
  fullName: '',
  password: '',
})

async function handleSubmit() {
  error.value = null
  loading.value = true
  try {
    const data = await register({
      username: form.username,
      full_name: form.fullName,
      password: form.password,
    })
    authStore.setAuth(data)
    router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-form {
  width: 100%;
}
.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  font-size: 14px;
  color: #374151;
  margin-bottom: 6px;
  font-weight: 500;
}
.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}
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
.btn-primary:hover { background: #2563eb; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.form-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #6b7280;
}
.form-footer a {
  color: #3b82f6;
  text-decoration: none;
}
</style>
