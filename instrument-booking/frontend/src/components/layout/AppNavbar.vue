<template>
  <nav class="navbar">
    <router-link to="/" class="navbar-brand">硅光实验室预约管理系统</router-link>
    <div class="navbar-menu">
      <router-link to="/bookings" class="nav-link">我的预约</router-link>
      <router-link to="/admin" class="nav-link">管理后台</router-link>
      <NotificationBell :unread-count="unreadCount" @refresh="refreshUnread" />
      <button class="btn-link" @click="handleLogout">退出</button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import NotificationBell from '../notifications/NotificationBell.vue'
import { useNotification } from '../../composables/useNotification'

const router = useRouter()
const authStore = useAuthStore()
const { unreadCount, refresh: refreshUnread } = useNotification()

function handleLogout() {
  authStore.logout()
  router.push('/login')
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
}
.navbar-brand {
  font-size: 18px;
  font-weight: 600;
  color: white;
  text-decoration: none;
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
