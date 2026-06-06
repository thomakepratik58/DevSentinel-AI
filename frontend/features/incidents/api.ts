/** Incident API functions — typed wrappers around the incident endpoints. */

import { apiClient } from "@/lib/api-client"
import type {
  Incident,
  IncidentListResponse,
  CreateIncidentPayload,
  UpdateIncidentPayload,
} from "./types"

export async function listIncidents(
  workspaceId: string
): Promise<IncidentListResponse> {
  return apiClient.get<IncidentListResponse>(
    `/api/v1/workspaces/${workspaceId}/incidents`
  )
}

export async function getIncident(
  workspaceId: string,
  incidentId: string
): Promise<Incident> {
  return apiClient.get<Incident>(
    `/api/v1/workspaces/${workspaceId}/incidents/${incidentId}`
  )
}

export async function createIncident(
  workspaceId: string,
  payload: CreateIncidentPayload
): Promise<Incident> {
  return apiClient.post<Incident>(
    `/api/v1/workspaces/${workspaceId}/incidents`,
    payload
  )
}

export async function updateIncident(
  workspaceId: string,
  incidentId: string,
  payload: UpdateIncidentPayload
): Promise<Incident> {
  return apiClient.patch<Incident>(
    `/api/v1/workspaces/${workspaceId}/incidents/${incidentId}`,
    payload
  )
}
