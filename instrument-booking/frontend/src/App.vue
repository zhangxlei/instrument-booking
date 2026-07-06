<template>
  <router-view />
  <div v-if="showNotice" class="notice-overlay" @click.self="dismissNotice">
    <div class="notice-modal">
      <h3>硅光实验室仪表使用须知</h3>
      <div class="notice-content">
        <p>欢迎使用上海光电科技创新中心硅光实验室仪表预约系统。</p>
        <p>使用本系统前，请确认以下事项：</p>
        <ol>
          <li>请提前了解仪器的使用方法和注意事项</li>
          <li>使用仪器前需经过相应培训并取得操作资格</li>
          <li>仪器使用过程中如遇异常情况，请立即停止并联系管理员</li>
          <li>使用完毕后请按规定清洁整理仪器和工作台</li>
          <li>预约后如需取消，请提前通知管理员</li>
          <li>请勿预约超出实际需求的时段，以免影响他人使用</li>
        </ol>
        <p class="notice-footer">感谢您的配合！</p>
      </div>
      <button class="btn-primary" @click="dismissNotice">我已了解</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { getMe } from './api/auth'

const authStore = useAuthStore()
const route = useRoute()
const showNotice = ref(false)

function dismissNotice() {
  showNotice.value = false
  localStorage.setItem('login_notice_read', '1')
}

onMounted(async () => {
  if (authStore.isLoggedIn() && !authStore.user) {
    try {
      const user = await getMe()
      authStore.setUser({
        id: user.id,
        username: user.username,
        full_name: user.full_name,
        role: user.role,
      })
    } catch {
      authStore.logout()
    }
  }

  if (!localStorage.getItem('login_notice_read') && authStore.isLoggedIn()) {
    showNotice.value = true
  }
})
</script>

<style>
.notice-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.notice-modal {
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 500px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}
.notice-modal h3 {
  margin: 0 0 16px;
  font-size: 18px;
  color: #1e293b;
  text-align: center;
}
.notice-content {
  font-size: 14px;
  color: #475569;
  line-height: 1.8;
}
.notice-content ol {
  padding-left: 20px;
}
.notice-footer {
  text-align: right;
  font-weight: 500;
  color: #1e293b;
}
.btn-primary {
  display: block;
  margin: 20px auto 0;
  padding: 10px 40px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
}
.btn-primary:hover { background: #2563eb; }
</style>
