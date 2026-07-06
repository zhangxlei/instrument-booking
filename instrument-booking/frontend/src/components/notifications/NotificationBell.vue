<template>
  <div class="notification-wrapper" @click.stop="toggleDropdown">
    <span class="bell-icon">&#128276;</span>
    <span v-if="unreadCount > 0" class="badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
    <NotificationList v-if="showDropdown" @close="showDropdown = false" @refresh="$emit('refresh')" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import NotificationList from './NotificationList.vue'

defineProps<{ unreadCount: number }>()
defineEmits<{ refresh: [] }>()

const showDropdown = ref(false)

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}
</script>

<style scoped>
.notification-wrapper {
  position: relative;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.bell-icon { font-size: 20px; }
.badge {
  position: absolute;
  top: -4px;
  right: -8px;
  background: #dc2626;
  color: white;
  font-size: 11px;
  padding: 1px 5px;
  border-radius: 8px;
  font-weight: 600;
  min-width: 16px;
  text-align: center;
}
</style>
