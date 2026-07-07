<template>
  <div v-if="message" class="error-alert">
    {{ message }}
  </div>
</template>

<script setup lang="ts">
defineProps<{ message: string | null }>()
</script>

<style scoped>
.error-alert {
  background: var(--color-danger-bg);
  color: var(--color-danger);
  border: 1px solid #FECACA;
  border-radius: var(--radius-md);
  padding: var(--space-sm) var(--space-md);
  font-size: 14px;
  margin-bottom: var(--space-md);
}
</style>
