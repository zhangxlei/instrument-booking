<template>
  <div class="admin-layout">
    <AppNavbar />
    <div class="admin-body">
      <AppSidebar />
      <main class="admin-content">
        <router-view />
      </main>
    </div>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import AppNavbar from './AppNavbar.vue'
import AppFooter from './AppFooter.vue'
import AppSidebar from './AppSidebar.vue'
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f1f5f9;
  display: flex;
  flex-direction: column;
}
.admin-body {
  display: flex;
  flex: 1;
}
.admin-content {
  flex: 1;
  padding: 24px;
}
</style>
