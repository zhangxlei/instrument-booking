<template>
  <div class="instrument-card" @click="$router.push(`/instruments/${instrument.id}`)">
    <div class="card-left">
      <div v-if="instrument.image_url" class="card-image">
        <img :src="instrument.image_url" :alt="instrument.name" />
      </div>
      <div v-else class="card-image placeholder">
        <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="#94a3b8" stroke-width="1.5">
          <path d="M2 12L9 19L16 12L23 19" />
          <circle cx="9" cy="7" r="2" />
          <rect x="3" y="3" width="18" height="18" rx="2" />
        </svg>
      </div>
    </div>
    <div class="card-body">
      <div class="card-header">
        <h3 class="card-name">{{ instrument.name }}</h3>
        <span class="status-badge" :class="instrument.status">{{ statusText }}</span>
      </div>
      <p v-if="instrument.location" class="card-location">{{ instrument.location }}</p>
      <p v-if="instrument.price_per_hour" class="card-price">¥{{ instrument.price_per_hour }}/小时</p>
      <p v-if="instrument.description" class="card-desc">{{ instrument.description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { InstrumentRead } from '../../api/instruments'

const props = defineProps<{
  instrument: InstrumentRead
}>()

const statusText = computed(() => {
  const map: Record<string, string> = {
    available: '可用',
    maintenance: '维护中',
    retired: '已报废',
  }
  return map[props.instrument.status] || props.instrument.status
})
</script>

<style scoped>
.instrument-card {
  display: flex;
  gap: var(--space-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.instrument-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary-light);
}

.card-left {
  flex-shrink: 0;
}

.card-image {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-normal);
}

.instrument-card:hover .card-image img {
  transform: scale(1.05);
}

.card-image.placeholder {
  background: var(--color-primary-50);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xs);
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  transition: color var(--transition-fast);
}

.instrument-card:hover .card-name {
  color: var(--color-primary);
}

.status-badge {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-weight: 500;
}

.status-badge.available { 
  background: var(--color-success-bg); 
  color: #047857; 
}

.status-badge.maintenance { 
  background: var(--color-warning-bg); 
  color: #B45309; 
}

.status-badge.retired { 
  background: var(--color-bg); 
  color: var(--color-text-secondary); 
}

.card-location, .card-price {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 2px 0;
}

.card-price {
  color: var(--color-success);
  font-weight: 600;
}

.card-desc {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: var(--space-xs) 0 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
