import client from './client'

export interface InstrumentRead {
  id: string
  name: string
  description: string | null
  location: string | null
  image_url: string | null
  status: string
  requires_approval: boolean
  price_per_hour: number | null
  manager_name: string | null
  manager_phone: string | null
  probe_type: string | null
}

export interface InstrumentCreate {
  name: string
  description?: string
  location?: string
  image_url?: string
  requires_approval?: boolean
  price_per_hour?: number
  manager_name?: string
  manager_phone?: string
  probe_type?: string
}

export interface AttachmentInfo {
  id: string
  original_filename: string
  file_size: number
  file_type: string | null
  created_at: string
}

export async function getInstruments(params?: {
  status?: string
  search?: string
  page?: number
  per_page?: number
}): Promise<InstrumentRead[]> {
  const res = await client.get('/instruments', { params })
  return res.data
}

export async function getInstrument(id: string): Promise<InstrumentRead> {
  const res = await client.get(`/instruments/${id}`)
  return res.data
}

export async function createInstrument(data: InstrumentCreate): Promise<InstrumentRead> {
  const res = await client.post('/instruments', data)
  return res.data
}

export async function updateInstrument(id: string, data: Partial<InstrumentCreate>): Promise<InstrumentRead> {
  const res = await client.put(`/instruments/${id}`, data)
  return res.data
}

export async function deleteInstrument(id: string): Promise<void> {
  await client.delete(`/instruments/${id}`)
}

export async function getAttachments(instrumentId: string): Promise<AttachmentInfo[]> {
  const res = await client.get(`/instruments/${instrumentId}/attachments`)
  return res.data
}

export async function deleteAttachment(instrumentId: string, attachmentId: string): Promise<void> {
  await client.delete(`/instruments/${instrumentId}/attachments/${attachmentId}`)
}

export async function uploadAttachment(instrumentId: string, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await client.post(`/instruments/${instrumentId}/attachments`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export interface AvailabilitySlot {
  date: string
  slots: { start: string; end: string; available: boolean; booked_by: { username: string; full_name: string } | null }[]
}

export async function getAvailability(instrumentId: string, days = 7): Promise<AvailabilitySlot[]> {
  const res = await client.get(`/instruments/${instrumentId}/availability`, { params: { days, _t: Date.now() } })
  return res.data
}

export function getAttachmentUrl(instrumentId: string, attachmentId: string): string {
  return `/api/v1/instruments/${instrumentId}/attachments/${attachmentId}`
}

export async function uploadImage(instrumentId: string, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await client.post(`/instruments/${instrumentId}/image`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function deleteImage(instrumentId: string) {
  const res = await client.delete(`/instruments/${instrumentId}/image`)
  return res.data
}
