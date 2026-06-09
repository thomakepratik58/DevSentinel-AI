/** Repository API functions — typed wrappers around the repository endpoints. */

import { apiClient } from "@/lib/api-client"
import type {
  Repository,
  RepositoryListResponse,
  CreateRepositoryPayload,
} from "./types"

export async function listRepositories(
  workspaceId: string
): Promise<RepositoryListResponse> {
  return apiClient.get<RepositoryListResponse>(
    `/api/v1/workspaces/${workspaceId}/repositories`
  )
}

export async function getRepository(
  workspaceId: string,
  repositoryId: string
): Promise<Repository> {
  return apiClient.get<Repository>(
    `/api/v1/workspaces/${workspaceId}/repositories/${repositoryId}`
  )
}

export async function createRepository(
  workspaceId: string,
  payload: CreateRepositoryPayload
): Promise<Repository> {
  return apiClient.post<Repository>(
    `/api/v1/workspaces/${workspaceId}/repositories`,
    payload
  )
}

export async function deleteRepository(
  workspaceId: string,
  repositoryId: string
): Promise<void> {
  await apiClient.delete(`/api/v1/workspaces/${workspaceId}/repositories/${repositoryId}`)
}
