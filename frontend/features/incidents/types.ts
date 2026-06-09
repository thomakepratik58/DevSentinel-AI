/** Domain types for incidents. */

export interface Incident {
  id: string
  workspace_id: string
  repository_id: string | null
  title: string
  description: string | null
  severity: IncidentSeverity
  status: IncidentStatus
  created_by_id: string
  resolved_at: string | null
  created_at: string
  updated_at: string
}

export type IncidentSeverity = "critical" | "high" | "medium" | "low" | "info"
export type IncidentStatus = "open" | "investigating" | "resolved" | "closed"

export interface IncidentListResponse {
  incidents: Incident[]
  count: number
}

export interface CreateIncidentPayload {
  title: string
  description?: string | null
  severity?: IncidentSeverity
  repository_id?: string | null
}

export interface UpdateIncidentPayload {
  title?: string
  description?: string
  severity?: IncidentSeverity
  status?: IncidentStatus
}
