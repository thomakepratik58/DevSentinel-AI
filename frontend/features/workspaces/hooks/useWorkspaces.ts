/** TanStack Query hook for the authenticated user's workspaces.
 *
 * Auto-selects the first workspace as the "active" workspace.
 * In a future milestone this will support a workspace picker in the sidebar.
 */

"use client"

import { useQuery } from "@tanstack/react-query"
import { listWorkspaces } from "../api"
import type { Workspace, WorkspaceListResponse } from "../types"

export const WORKSPACES_QUERY_KEY = ["workspaces"] as const

export function useWorkspaces() {
  return useQuery<WorkspaceListResponse, Error>({
    queryKey: WORKSPACES_QUERY_KEY,
    queryFn: listWorkspaces,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

/** Returns the first (default) workspace for the current user. */
export function useActiveWorkspace() {
  const { data, ...rest } = useWorkspaces()
  const activeWorkspace: Workspace | undefined = data?.workspaces?.[0]
  return { activeWorkspace, ...rest }
}
