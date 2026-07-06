<template>
  <div class="dashboard-charts">
    <div class="chart-card">
      <h3>仪器使用率</h3>
      <canvas ref="usageCanvas"></canvas>
      <p v-if="noUsageData" class="no-data">暂无数据</p>
    </div>
    <div class="chart-card">
      <h3>人员预约分布</h3>
      <canvas ref="userCanvas"></canvas>
      <p v-if="noUserData" class="no-data">暂无数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import client from '../../api/client'

Chart.register(...registerables)

const usageCanvas = ref<HTMLCanvasElement | null>(null)
const userCanvas = ref<HTMLCanvasElement | null>(null)
const noUsageData = ref(true)
const noUserData = ref(true)

onMounted(async () => {
  try {
    const res = await client.get('/admin/dashboard/charts')
    const data = res.data

    await nextTick()

    if (data.instrument_usage?.length && usageCanvas.value) {
      noUsageData.value = false
      new Chart(usageCanvas.value, {
        type: 'pie',
        data: {
          labels: data.instrument_usage.map((i: any) => i.name),
          datasets: [{
            data: data.instrument_usage.map((i: any) => i.count),
            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'],
          }],
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
      })
    }

    if (data.user_distribution?.length && userCanvas.value) {
      noUserData.value = false
      new Chart(userCanvas.value, {
        type: 'pie',
        data: {
          labels: data.user_distribution.map((u: any) => u.name),
          datasets: [{
            data: data.user_distribution.map((u: any) => u.count),
            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'],
          }],
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
      })
    }
  } catch {}
})
</script>

<style scoped>
.dashboard-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}
.chart-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
}
.chart-card h3 {
  font-size: 15px;
  color: #475569;
  margin: 0 0 16px;
}
.no-data {
  text-align: center;
  color: #94a3b8;
  padding: 40px 0;
}
</style>
