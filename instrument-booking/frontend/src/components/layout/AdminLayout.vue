<template>
  <div class="admin-layout">
    <AppNavbar />
    <div class="admin-body">
      <AppSidebar />
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppNavbar from './AppNavbar.vue'
import AppSidebar from './AppSidebar.vue'
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f1f5f9;
}
.admin-body {
  display: flex;
}
.admin-content {
  flex: 1;
  padding: 24px;
  min-height: calc(100vh - 56px);
}
</style>
