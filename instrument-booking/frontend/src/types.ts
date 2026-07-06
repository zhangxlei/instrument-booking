export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
  full_name: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: UserBrief
}

export interface UserBrief {
  id: string
  username: string
  full_name: string
  role: string
}

export interface UserRead {
  id: string
  username: string
  full_name: string
  phone: string | null
  role: string
  is_active: boolean
}
