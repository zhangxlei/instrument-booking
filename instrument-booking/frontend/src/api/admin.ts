import client from './client'
import type { BookingRead } from './bookings'

export async function getAdminBookings(params?: {
  status?: string
  instrument_id?: string
  page?: number
  per_page?: number
}): Promise<BookingRead[]> {
  const res = await client.get('/admin/bookings', { params })
  return res.data
}

export async function approveBooking(id: string): Promise<BookingRead> {
  const res = await client.put(`/admin/bookings/${id}/approve`)
  return res.data
}

export async function rejectBooking(id: string, reason: string): Promise<BookingRead> {
  const res = await client.put(`/admin/bookings/${id}/reject`, { reason })
  return res.data
}

export async function getDashboardStats(): Promise<{
  total_instruments: number
  total_users: number
  today_bookings: number
  pending_approvals: number
}> {
  const res = await client.get('/admin/dashboard/stats')
  return res.data
}

export async function adminRescheduleBooking(id: string, data: { start_time: string; end_time: string }) {
  const res = await client.put(`/admin/bookings/${id}/reschedule`, data)
  return res.data
}

export async function adminCancelBooking(id: string) {
  const res = await client.delete(`/admin/bookings/${id}`)
  return res.data
}

export async function adminCreateBooking(data: {
  user_id: string
  instrument_id: string
  start_time: string
  end_time: string
  purpose?: string
}) {
  const res = await client.post('/admin/bookings', data)
  return res.data
}

export interface UserAdmin {
  id: string
  username: string
  full_name: string
  role: string
  is_active: boolean
}

export async function getUsers(): Promise<UserAdmin[]> {
  const res = await client.get('/admin/users')
  return res.data
}

export async function createUser(data: { username: string; full_name: string; password: string; role?: string }) {
  const res = await client.post('/admin/users', data)
  return res.data
}

export async function changeUserRole(userId: string, role: string) {
  const res = await client.put(`/admin/users/${userId}/role`, { role })
  return res.data
}

export async function toggleUserActive(userId: string) {
  const res = await client.put(`/admin/users/${userId}/toggle-active`)
  return res.data
}

export async function deleteUser(userId: string) {
  const res = await client.delete(`/admin/users/${userId}`)
  return res.data
}
