<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { getMe } from './api/auth'

const authStore = useAuthStore()

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
})
</script>
