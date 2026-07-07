<template>
  <nav class="navbar">
    <router-link to="/" class="navbar-brand">上海光电科技创新中心硅光实验室仪表预约系统</router-link>
    <div class="navbar-menu">
      <router-link to="/bookings" class="nav-link">我的预约</router-link>
      <router-link v-if="authStore.isAdmin()" to="/admin" class="nav-link">管理后台</router-link>
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
  height: 64px;
  padding: 0 var(--space-lg);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: box-shadow var(--transition-normal);
}

.navbar:hover {
  box-shadow: var(--shadow-md);
}

.user-name {
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.navbar-brand {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: var(--space-md);
  transition: color var(--transition-fast);
}

.navbar-brand:hover {
  color: var(--color-primary);
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.nav-link {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-primary);
  background: var(--color-primary-50);
}

.nav-link.router-link-active {
  color: var(--color-primary);
  background: var(--color-primary-100);
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.btn-link:hover {
  color: var(--color-primary);
  background: var(--color-primary-50);
}
</style>
