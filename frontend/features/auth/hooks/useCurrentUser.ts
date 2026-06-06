/** TanStack Query hook for the authenticated user's profile. */

"use client"

import { useQuery } from "@tanstack/react-query"
import { getCurrentUser } from "../api"
import type { AuthUser } from "../types"

export const CURRENT_USER_QUERY_KEY = ["auth", "currentUser"] as const

export function useCurrentUser() {
  return useQuery<AuthUser, Error>({
    queryKey: CURRENT_USER_QUERY_KEY,
    queryFn: getCurrentUser,
    retry: false, // Don't retry 401s — redirect instead
    staleTime: 5 * 60 * 1000,
  })
}
