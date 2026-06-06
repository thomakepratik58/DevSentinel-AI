/** Workspace API functions — typed wrappers around /workspaces endpoints. */

import { apiClient } from "@/lib/api-client"
import type {
  Workspace,
  WorkspaceListResponse,
  CreateWorkspacePayload,
} from "./types"

export async function listWorkspaces(): Promise<WorkspaceListResponse> {
  return apiClient.get<WorkspaceListResponse>("/api/v1/workspaces")
}

export async function getWorkspace(workspaceId: string): Promise<Workspace> {
  return apiClient.get<Workspace>(`/api/v1/workspaces/${workspaceId}`)
}

export async function createWorkspace(
  payload: CreateWorkspacePayload
): Promise<Workspace> {
  return apiClient.post<Workspace>("/api/v1/workspaces", payload)
}
