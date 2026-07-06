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
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 10px 14px;
  font-size: 14px;
  margin-bottom: 16px;
}
</style>
