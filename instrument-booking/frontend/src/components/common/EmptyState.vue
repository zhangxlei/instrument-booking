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
  padding: var(--space-2xl) var(--space-lg);
  color: var(--color-text-muted);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--space-md);
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.empty-desc {
  font-size: 14px;
  margin-top: var(--space-sm);
  color: var(--color-text-muted);
}
</style>
