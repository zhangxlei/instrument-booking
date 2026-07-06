import { ref, onMounted, onUnmounted } from 'vue'
import { getUnreadCount } from '../api/notifications'

export function useNotification() {
  const unreadCount = ref(0)
  let timer: ReturnType<typeof setInterval> | null = null

  async function refresh() {
    try {
      unreadCount.value = await getUnreadCount()
    } catch {}
  }

  function startPolling(interval = 30000) {
    refresh()
    timer = setInterval(refresh, interval)
  }

  function stopPolling() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  onMounted(startPolling)
  onUnmounted(stopPolling)

  return { unreadCount, refresh }
}
