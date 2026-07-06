<template>
  <div class="app-layout">
    <AppNavbar />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppNavbar from './AppNavbar.vue'
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #f1f5f9;
}
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
</style>
