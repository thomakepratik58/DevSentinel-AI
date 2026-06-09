/** Domain types for the authentication feature. */

export interface AuthUser {
  id: string
  email: string
  display_name: string
  avatar_url: string | null
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: AuthUser
}

export interface RefreshResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  display_name: string
  password: string
}
