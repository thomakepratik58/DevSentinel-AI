/**
 * Typed API client for DevSentinel backend.
 *
 * Handles:
 *   - Base URL + JSON content-type
 *   - Authorization: Bearer <token> header from in-memory store
 *   - Automatic silent refresh on 401 → retry once
 *   - Typed AppError normalization for all failure paths
 *   - Request IDs propagated from response headers
 */

import { getAccessToken, refreshAccessToken, setAccessToken } from "./auth"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

// ── Error types ───────────────────────────────────────────────────────────────

export interface AppError {
  code: string
  message: string
  requestId?: string
  retryable: boolean
  status: number
  details?: Record<string, unknown>
}

export class ApiError extends Error {
  readonly code: string
  readonly requestId: string | undefined
  readonly retryable: boolean
  readonly status: number
  readonly details: Record<string, unknown> | undefined

  constructor(appError: AppError) {
    super(appError.message)
    this.name = "ApiError"
    this.code = appError.code
    this.requestId = appError.requestId
    this.retryable = appError.retryable
    this.status = appError.status
    this.details = appError.details
  }
}

// ── Core fetch wrapper ────────────────────────────────────────────────────────

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown
  skipAuth?: boolean
}

async function request<T>(
  path: string,
  options: RequestOptions = {},
  isRetry = false
): Promise<T> {
  const { body, skipAuth = false, ...rest } = options

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((rest.headers as Record<string, string>) ?? {}),
  }

  if (!skipAuth) {
    const token = getAccessToken()
    if (token) {
      headers["Authorization"] = `Bearer ${token}`
    }
  }

  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...rest,
      credentials: "include", // always send cookies for refresh endpoint
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch (networkError) {
    throw new ApiError({
      code: "network_error",
      message: "Unable to reach the server. Check your connection and try again.",
      retryable: true,
      status: 0,
    })
  }

  // ── Silent token refresh on 401 ───────────────────────────────
  if (response.status === 401 && !isRetry && !skipAuth) {
    const newToken = await refreshAccessToken()
    if (newToken) {
      setAccessToken(newToken)
      return request<T>(path, options, true)
    }
    // Refresh failed — let the error propagate so the auth hook can redirect
  }

  // ── Parse JSON body ───────────────────────────────────────────
  let json: unknown
  try {
    json = await response.json()
  } catch {
    if (!response.ok) {
      throw new ApiError({
        code: "parse_error",
        message: "The server returned an unexpected response.",
        retryable: false,
        status: response.status,
      })
    }
    return undefined as unknown as T
  }

  if (!response.ok) {
    const envelope = json as { error?: Partial<AppError> }
    const err = envelope.error ?? {}
    throw new ApiError({
      code: err.code ?? "unknown_error",
      message: err.message ?? "An unexpected error occurred.",
      requestId: err.requestId,
      retryable: err.retryable ?? response.status >= 500,
      status: response.status,
      details: err.details,
    })
  }

  return json as T
}

// ── Typed HTTP methods ────────────────────────────────────────────────────────

export const apiClient = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "GET" }),

  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "POST", body }),

  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "PUT", body }),

  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "PATCH", body }),

  delete: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "DELETE" }),
}
