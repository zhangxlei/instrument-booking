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
  gap: 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.instrument-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.card-left {
  flex-shrink: 0;
}
.card-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
}
.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-image.placeholder {
  background: #f1f5f9;
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
  margin-bottom: 4px;
}
.card-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}
.status-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}
.status-badge.available { background: #dcfce7; color: #166534; }
.status-badge.maintenance { background: #fef9c3; color: #854d0e; }
.status-badge.retired { background: #f1f5f9; color: #64748b; }
.card-location, .card-price {
  font-size: 13px;
  color: #64748b;
  margin: 2px 0;
}
.card-price {
  color: #059669;
  font-weight: 500;
}
.card-desc {
  font-size: 13px;
  color: #94a3b8;
  margin: 4px 0 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
