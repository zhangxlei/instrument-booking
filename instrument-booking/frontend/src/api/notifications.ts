import client from './client'

export interface NotificationRead {
  id: string
  type: string
  title: string
  message: string
  is_read: boolean
  created_at: string
}

export async function getNotifications(): Promise<NotificationRead[]> {
  const res = await client.get('/notifications')
  return res.data
}

export async function getUnreadCount(): Promise<number> {
  const res = await client.get('/notifications/unread-count')
  return res.data.count
}

export async function markRead(id: string): Promise<void> {
  await client.put(`/notifications/${id}/read`)
}

export async function markAllRead(): Promise<void> {
  await client.put('/notifications/read-all')
}
