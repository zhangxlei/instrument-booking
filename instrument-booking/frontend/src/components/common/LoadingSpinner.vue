<template>
  <div class="loading-container">
    <div class="spinner"></div>
    <p v-if="text" class="loading-text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{ text?: string }>()
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-2xl) 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: var(--space-md);
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
}
</style>
