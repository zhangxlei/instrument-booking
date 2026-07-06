<template>
  <nav class="navbar">
    <router-link to="/" class="navbar-brand">上海光电科技创新中心硅光实验室仪表预约系统</router-link>
    <div class="navbar-menu">
      <router-link to="/bookings" class="nav-link">我的预约</router-link>
      <router-link v-if="authStore.isAdmin()" to="/admin" class="nav-link">管理后台</router-link>
      <a href="http://10.201.5.107:8000/" target="_blank" class="nav-link">FTP文件库</a>
      <NotificationBell :unread-count="unreadCount" @refresh="refreshUnread" />
      <span class="user-name">{{ authStore.user?.username || authStore.user?.full_name }}</span>
      <button class="btn-link" @click="showPasswordDialog = true">修改密码</button>
      <button class="btn-link" @click="handleLogout">退出</button>
    </div>
  </nav>
  <ChangePasswordDialog :visible="showPasswordDialog" @close="showPasswordDialog = false" @saved="onPasswordChanged" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import NotificationBell from '../notifications/NotificationBell.vue'
import ChangePasswordDialog from '../auth/ChangePasswordDialog.vue'
import { useNotification } from '../../composables/useNotification'

const router = useRouter()
const authStore = useAuthStore()
const { unreadCount, refresh: refreshUnread } = useNotification()
const showPasswordDialog = ref(false)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function onPasswordChanged() {
  // 密码修改成功后可以给提示
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 24px;
  background: #1e293b;
  color: white;
  position: sticky;
  top: 0;
  z-index: 100;
}
.user-name {
  color: #e2e8f0;
  font-size: 14px;
}
.navbar-brand {
  font-size: 15px;
  font-weight: 600;
  color: white;
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 16px;
}
.navbar-brand:hover {
  color: #e2e8f0;
}
.navbar-menu {
  display: flex;
  align-items: center;
  gap: 16px;
}
.nav-link {
  color: #94a3b8;
  text-decoration: none;
  font-size: 14px;
}
.nav-link:hover {
  color: white;
}
.btn-link {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 14px;
}
.btn-link:hover {
  color: white;
}
</style>
