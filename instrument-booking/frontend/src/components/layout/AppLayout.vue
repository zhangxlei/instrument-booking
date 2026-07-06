<template>
  <div class="app-layout">
    <AppNavbar />
    <main class="main-content">
      <router-view />
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import AppNavbar from './AppNavbar.vue'
import AppFooter from './AppFooter.vue'
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #f1f5f9;
  display: flex;
  flex-direction: column;
}
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  width: 100%;
}
</style>
