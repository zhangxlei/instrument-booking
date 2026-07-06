<template>
  <div class="dashboard-charts">
    <div class="charts-row">
      <div class="chart-card small">
        <h3>仪器使用占比</h3>
        <div class="chart-wrap">
          <canvas ref="usageCanvas"></canvas>
        </div>
        <p v-if="noUsageData" class="no-data">暂无数据</p>
      </div>
      <div class="chart-card small">
        <h3>人员预约占比</h3>
        <div class="chart-wrap">
          <canvas ref="userCanvas"></canvas>
        </div>
        <p v-if="noUserData" class="no-data">暂无数据</p>
      </div>
    </div>

    <div class="chart-card wide">
      <h3>近30天预约趋势</h3>
      <canvas ref="trendCanvas"></canvas>
      <p v-if="noTrendData" class="no-data">暂无数据</p>
    </div>

    <div class="chart-card wide">
      <h3>时段热度分布</h3>
      <p class="hint">显示各时段被预约的次数，柱子越高表示该时段越热门</p>
      <canvas ref="hourCanvas"></canvas>
      <p v-if="noHourData" class="no-data">暂无数据</p>
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
const trendCanvas = ref<HTMLCanvasElement | null>(null)
const hourCanvas = ref<HTMLCanvasElement | null>(null)
const noUsageData = ref(true)
const noUserData = ref(true)
const noTrendData = ref(true)
const noHourData = ref(true)

const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16']

function makeChart(canvas: HTMLCanvasElement, type: string, labels: string[], data: number[], bgColors: string[], extraOptions?: any) {
  return new Chart(canvas, {
    type,
    data: {
      labels,
      datasets: [{ data, backgroundColor: bgColors, borderWidth: 0 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'right',
          labels: { boxWidth: 12, padding: 8, font: { size: 11 } },
        },
      },
      ...extraOptions,
    },
  })
}

onMounted(async () => {
  try {
    const res = await client.get('/admin/dashboard/charts')
    const data = res.data
    await nextTick()

    if (data.instrument_usage?.length && usageCanvas.value) {
      noUsageData.value = false
      makeChart(usageCanvas.value, 'doughnut',
        data.instrument_usage.map((i: any) => i.name),
        data.instrument_usage.map((i: any) => i.count),
        colors.slice(0, data.instrument_usage.length),
      )
    }

    if (data.user_distribution?.length && userCanvas.value) {
      noUserData.value = false
      makeChart(userCanvas.value, 'doughnut',
        data.user_distribution.map((u: any) => u.name),
        data.user_distribution.map((u: any) => u.count),
        colors.slice(0, data.user_distribution.length),
      )
    }

    if (data.daily_trend?.length && trendCanvas.value) {
      noTrendData.value = false
      const labels = data.daily_trend.map((d: any) => d.date.slice(5))
      const values = data.daily_trend.map((d: any) => d.count)
      new Chart(trendCanvas.value, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: '预约数',
            data: values,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.08)',
            fill: true,
            tension: 0.3,
            pointRadius: 2,
            pointHoverRadius: 5,
          }],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: { ticks: { font: { size: 10 }, maxTicksLimit: 15 } },
            y: { beginAtZero: true, ticks: { stepSize: 1, font: { size: 10 } } },
          },
        },
      })
    }

    if (data.hourly_distribution?.labels?.length && hourCanvas.value) {
      noHourData.value = false
      const hLabels = data.hourly_distribution.labels
      const hData = data.hourly_distribution.data
      const barColors = hData.map((v: number) =>
        v > 0 ? `rgba(59, 130, 246, ${0.3 + (v / Math.max(...hData)) * 0.7})` : '#f1f5f9'
      )
      new Chart(hourCanvas.value, {
        type: 'bar',
        data: {
          labels: hLabels,
          datasets: [{
            label: '预约次数',
            data: hData,
            backgroundColor: barColors,
            borderRadius: 3,
          }],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { font: { size: 9 } } },
            y: { beginAtZero: true, ticks: { stepSize: 1, font: { size: 10 } } },
          },
        },
      })
    }
  } catch {}
})
</script>

<style scoped>
.dashboard-charts {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.chart-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
}
.chart-card h3 {
  font-size: 14px;
  color: #475569;
  margin: 0 0 12px;
  font-weight: 600;
}
.chart-wrap {
  max-width: 320px;
  margin: 0 auto;
}
.hint {
  font-size: 12px;
  color: #94a3b8;
  margin: -8px 0 12px;
}
.no-data {
  text-align: center;
  color: #94a3b8;
  padding: 60px 0;
  font-size: 14px;
}
</style>
