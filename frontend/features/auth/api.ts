/** Auth API functions — typed wrappers around the /auth endpoints. */

import { apiClient } from "@/lib/api-client"
import { setAccessToken, clearAccessToken } from "@/lib/auth"
import type {
  AuthUser,
  LoginPayload,
  RegisterPayload,
  RefreshResponse,
  TokenResponse,
} from "./types"

export async function registerUser(payload: RegisterPayload): Promise<TokenResponse> {
  const data = await apiClient.post<TokenResponse>("/api/v1/auth/register", payload, {
    skipAuth: true,
  })
  setAccessToken(data.access_token)
  return data
}

export async function loginUser(payload: LoginPayload): Promise<TokenResponse> {
  const data = await apiClient.post<TokenResponse>("/api/v1/auth/login", payload, {
    skipAuth: true,
  })
  setAccessToken(data.access_token)
  return data
}

export async function logoutUser(): Promise<void> {
  try {
    await apiClient.post<{ message: string }>("/api/v1/auth/logout")
  } finally {
    // Always clear in-memory token even if the network request fails
    clearAccessToken()
  }
}

export async function getCurrentUser(): Promise<AuthUser> {
  return apiClient.get<AuthUser>("/api/v1/auth/me")
}

export async function refreshToken(): Promise<RefreshResponse> {
  return apiClient.post<RefreshResponse>("/api/v1/auth/refresh", undefined, {
    skipAuth: true,
  })
}
