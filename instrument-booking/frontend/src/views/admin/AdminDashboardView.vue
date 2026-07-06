<template>
  <div class="dashboard">
    <h2>仪表盘</h2>
    <LoadingSpinner v-if="loading" text="加载中..." />
    <StatsCards v-else :stats="stats" @navigate="goTo" />
    <DashboardCharts />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardStats } from '../../api/admin'
import DashboardCharts from '../../components/admin/DashboardCharts.vue'
import LoadingSpinner from '../../components/common/LoadingSpinner.vue'
import StatsCards from '../../components/admin/StatsCards.vue'

const router = useRouter()
const stats = ref({ total_instruments: 0, total_users: 0, today_bookings: 0, pending_approvals: 0 })
const loading = ref(true)

function goTo(path: string) {
  router.push(path)
}

onMounted(async () => {
  try { stats.value = await getDashboardStats() } catch {}
  finally { loading.value = false }
})
</script>

<style scoped>
h2 { font-size: 22px; color: #1e293b; margin: 0 0 20px; }
</style>
