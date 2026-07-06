<template>
  <div class="empty-state">
    <p class="empty-icon">{{ icon }}</p>
    <p class="empty-title">{{ title }}</p>
    <p v-if="description" class="empty-desc">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon?: string
  title: string
  description?: string
}>()
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}
.empty-title {
  font-size: 16px;
  font-weight: 500;
  color: #64748b;
}
.empty-desc {
  font-size: 14px;
  margin-top: 8px;
}
</style>
