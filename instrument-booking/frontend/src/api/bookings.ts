import client from './client'

export interface BookingRead {
  id: string
  user_id: string
  instrument_id: string
  start_time: string
  end_time: string
  status: string
  purpose: string | null
  notes: string | null
  rejection_reason: string | null
  created_at: string
  user_username?: string | null
  user_full_name?: string | null
  instrument_name?: string | null
}

export interface BookingCreate {
  instrument_id: string
  start_time: string
  end_time: string
  purpose?: string
  notes?: string
}

export async function getBookings(status?: string): Promise<BookingRead[]> {
  const params = status ? { status } : {}
  const res = await client.get('/bookings', { params })
  return res.data
}

export async function getBooking(id: string): Promise<BookingRead> {
  const res = await client.get(`/bookings/${id}`)
  return res.data
}

export async function createBooking(data: BookingCreate): Promise<BookingRead> {
  const res = await client.post('/bookings', data)
  return res.data
}

export async function cancelBooking(id: string): Promise<void> {
  await client.delete(`/bookings/${id}`)
}

export async function updateBooking(id: string, data: { start_time: string; end_time: string }): Promise<BookingRead> {
  const res = await client.put(`/bookings/${id}`, data)
  return res.data
}
