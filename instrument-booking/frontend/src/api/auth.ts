import client from './client'
import type { LoginRequest, RegisterRequest, TokenResponse, UserRead } from '../types'

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await client.post('/auth/login', data)
  return res.data
}

export async function register(data: RegisterRequest): Promise<TokenResponse> {
  const res = await client.post('/auth/register', data)
  return res.data
}

export async function getMe(): Promise<UserRead> {
  const res = await client.get('/auth/me')
  return res.data
}

export async function changePassword(oldPassword: string, newPassword: string): Promise<void> {
  await client.put('/auth/me/password', { old_password: oldPassword, new_password: newPassword })
}

export async function changeUsername(newUsername: string): Promise<void> {
  await client.put('/auth/me/username', { new_username: newUsername })
}
