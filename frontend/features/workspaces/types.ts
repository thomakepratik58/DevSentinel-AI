/** Domain types for workspaces. */

export interface Workspace {
  id: string
  name: string
  slug: string
  description: string | null
  owner_id: string
  created_at: string
  updated_at: string
}

export interface WorkspaceListResponse {
  workspaces: Workspace[]
  count: number
}

export interface CreateWorkspacePayload {
  name: string
  description?: string | null
}
