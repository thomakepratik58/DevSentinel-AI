/**
 * In-memory access token store.
 *
 * Access tokens are kept in module-level memory (never localStorage/cookies)
 * to minimise XSS exposure.  They are lost on page reload, at which point
 * the refresh-token cookie triggers a silent re-issue via /auth/refresh.
 */

let _accessToken: string | null = null

export function setAccessToken(token: string): void {
  _accessToken = token
}

export function getAccessToken(): string | null {
  return _accessToken
}

export function clearAccessToken(): void {
  _accessToken = null
}

/**
 * Attempt a silent token refresh using the HttpOnly refresh-token cookie.
 * Returns the new access token string, or null on failure.
 */
export async function refreshAccessToken(): Promise<string | null> {
  try {
    const res = await fetch("/api/v1/auth/refresh", {
      method: "POST",
      credentials: "include", // sends the HttpOnly cookie
    })
    if (!res.ok) return null
    const data = await res.json()
    const token: string = data.access_token
    setAccessToken(token)
    return token
  } catch {
    return null
  }
}
