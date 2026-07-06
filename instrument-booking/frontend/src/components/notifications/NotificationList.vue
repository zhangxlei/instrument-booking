<template>
  <div class="dropdown" @click.stop>
    <div class="dropdown-header">
      <span>通知</span>
      <button class="btn-mark-all" @click="handleMarkAll">全部已读</button>
    </div>
    <div class="dropdown-body">
      <div v-if="notifications.length === 0" class="empty">暂无通知</div>
      <div
        v-for="n in notifications" :key="n.id"
        class="notif-item"
        :class="{ unread: !n.is_read }"
        @click="handleClick(n)"
      >
        <p class="notif-title">{{ n.title }}</p>
        <p class="notif-msg">{{ n.message }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getNotifications, markRead, markAllRead, type NotificationRead } from '../../api/notifications'

const emit = defineEmits<{ close: []; refresh: [] }>()
const notifications = ref<NotificationRead[]>([])

async function load() {
  try {
    notifications.value = await getNotifications()
  } catch {}
}

async function handleClick(n: NotificationRead) {
  if (!n.is_read) {
    await markRead(n.id)
    emit('refresh')
    await load()
  }
}

async function handleMarkAll() {
  await markAllRead()
  emit('refresh')
  await load()
}

onMounted(load)
</script>

<style scoped>
.dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 320px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  max-height: 400px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid #e2e8f0;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}
.btn-mark-all {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 12px;
}
.dropdown-body {
  overflow-y: auto;
  flex: 1;
}
.notif-item {
  padding: 10px 14px;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
}
.notif-item:hover { background: #f8fafc; }
.notif-item.unread { background: #eff6ff; }
.notif-title {
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
  margin: 0 0 2px;
}
.notif-msg {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}
.empty {
  padding: 24px;
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}
</style>
