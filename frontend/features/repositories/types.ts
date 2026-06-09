/** Domain types for repositories. */

export interface Repository {
  id: string
  workspace_id: string
  name: string
  full_name: string
  clone_url: string
  default_branch: string
  description: string | null
  status: RepositoryStatus
  last_indexed_at: string | null
  created_at: string
  updated_at: string
}

export type RepositoryStatus = "pending" | "indexing" | "ready" | "error" | "archived"

export interface RepositoryListResponse {
  repositories: Repository[]
  count: number
}

export interface CreateRepositoryPayload {
  name: string
  full_name: string
  clone_url: string
  default_branch?: string
  description?: string | null
}
