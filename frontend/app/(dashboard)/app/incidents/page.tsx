"use client"

import { useQuery } from "@tanstack/react-query"
import { useActiveWorkspace } from "@/features/workspaces/hooks/useWorkspaces"
import { listIncidents } from "@/features/incidents/api"
import type { Incident, IncidentListResponse, IncidentSeverity, IncidentStatus } from "@/features/incidents/types"
import {
  AlertTriangle,
  Plus,
  Clock,
  Search,
  ArrowRight,
} from "lucide-react"
import Link from "next/link"

// ── Severity config ───────────────────────────────────────────────────────────

const SEVERITY_CONFIG: Record<IncidentSeverity, { label: string; color: string }> = {
  critical: { label: "Critical", color: "var(--danger)" },
  high: { label: "High", color: "var(--danger)" },
  medium: { label: "Medium", color: "var(--warning)" },
  low: { label: "Low", color: "var(--info)" },
  info: { label: "Info", color: "var(--text-muted)" },
}

const STATUS_CONFIG: Record<IncidentStatus, { label: string; color: string }> = {
  open: { label: "Open", color: "var(--danger)" },
  investigating: { label: "Investigating", color: "var(--warning)" },
  resolved: { label: "Resolved", color: "var(--success)" },
  closed: { label: "Closed", color: "var(--text-muted)" },
}

function SeverityBadge({ severity }: { severity: IncidentSeverity }) {
  const config = SEVERITY_CONFIG[severity] ?? SEVERITY_CONFIG.medium
  return (
    <span
      className="badge"
      style={{ "--badge-color": `hsl(${config.color})` } as React.CSSProperties}
    >
      {config.label}
    </span>
  )
}

function StatusBadge({ status }: { status: IncidentStatus }) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.open
  return (
    <span
      className="badge badge--outline"
      style={{ "--badge-color": `hsl(${config.color})` } as React.CSSProperties}
    >
      <span className="badge__dot" />
      {config.label}
    </span>
  )
}

// ── Incident row ──────────────────────────────────────────────────────────────

function IncidentRow({ incident }: { incident: Incident }) {
  return (
    <Link
      href={`/app/incidents/${incident.id}`}
      className="incident-row"
    >
      <div className="incident-row__main">
        <div className="incident-row__badges">
          <SeverityBadge severity={incident.severity} />
          <StatusBadge status={incident.status} />
        </div>
        <span className="incident-row__title">{incident.title}</span>
        {incident.description && (
          <span className="incident-row__desc">
            {incident.description.slice(0, 120)}
            {incident.description.length > 120 ? "…" : ""}
          </span>
        )}
      </div>
      <div className="incident-row__meta">
        <span className="incident-row__date">
          <Clock className="h-3 w-3" aria-hidden="true" />
          {new Date(incident.created_at).toLocaleDateString()}
        </span>
        <ArrowRight className="incident-row__arrow h-4 w-4" aria-hidden="true" />
      </div>
    </Link>
  )
}

// ── Empty state ───────────────────────────────────────────────────────────────

function EmptyIncidents() {
  return (
    <div className="empty-state" role="status">
      <div className="empty-state__icon">
        <AlertTriangle className="h-6 w-6" aria-hidden="true" />
      </div>
      <h3 className="empty-state__title">No incidents reported yet</h3>
      <p className="empty-state__description">
        Create your first incident from a stack trace, bug report, or failing test
        to begin AI-powered root cause analysis.
      </p>
      <Link href="/app/incidents/new" className="btn btn--primary">
        <Plus className="h-4 w-4" aria-hidden="true" />
        Create incident
      </Link>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function IncidentsPage() {
  const { activeWorkspace, isLoading: wsLoading } = useActiveWorkspace()

  const {
    data,
    isLoading: incidentsLoading,
  } = useQuery<IncidentListResponse, Error>({
    queryKey: ["incidents", activeWorkspace?.id],
    queryFn: () => listIncidents(activeWorkspace!.id),
    enabled: !!activeWorkspace,
  })

  const isLoading = wsLoading || incidentsLoading
  const incidents = data?.incidents ?? []

  return (
    <>
      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Incidents</h1>
          <p className="page-subtitle">
            Track and analyze production incidents with AI.
          </p>
        </div>
        <div className="page-header__actions">
          {incidents.length > 0 && (
            <Link href="/app/incidents/new" className="btn btn--primary">
              <Plus className="h-4 w-4" aria-hidden="true" />
              Create incident
            </Link>
          )}
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="incidents-panel">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton-row">
              <div className="skeleton" style={{ height: 22, width: "15%" }} />
              <div className="skeleton" style={{ height: 16, width: "55%", marginTop: 8 }} />
              <div className="skeleton" style={{ height: 14, width: "25%", marginTop: 8 }} />
            </div>
          ))}
        </div>
      ) : incidents.length === 0 ? (
        <div className="empty-container">
          <EmptyIncidents />
        </div>
      ) : (
        <div className="incidents-panel">
          <div className="incidents-header">
            <span className="incidents-count">{data?.count ?? 0} incident{incidents.length !== 1 ? "s" : ""}</span>
          </div>
          <div className="incident-list">
            {incidents.map((incident) => (
              <IncidentRow key={incident.id} incident={incident} />
            ))}
          </div>
        </div>
      )}

      <style>{`
        /* ── Page header ─────────────────────────────────────────── */
        .page-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          margin-bottom: 28px;
          gap: 16px;
          flex-wrap: wrap;
        }
        .page-header__actions { display: flex; gap: 8px; }
        .page-title {
          font-size: 22px;
          font-weight: 700;
          letter-spacing: -0.02em;
          color: hsl(var(--text-primary));
          margin: 0 0 4px;
        }
        .page-subtitle {
          font-size: 14px;
          color: hsl(var(--text-muted));
          margin: 0;
        }

        /* ── Badges ──────────────────────────────────────────────── */
        .badge {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 2px 9px;
          font-size: 11px;
          font-weight: 600;
          border-radius: 999px;
          color: var(--badge-color);
          background: color-mix(in srgb, var(--badge-color) 12%, transparent);
          white-space: nowrap;
          flex-shrink: 0;
        }
        .badge--outline {
          background: transparent;
          border: 1px solid color-mix(in srgb, var(--badge-color) 35%, transparent);
        }
        .badge__dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--badge-color);
        }

        /* ── Incidents panel ─────────────────────────────────────── */
        .incidents-panel {
          background: hsl(var(--surface-raised));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-lg);
          overflow: hidden;
        }
        .incidents-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 14px 20px;
          border-bottom: 1px solid hsl(var(--border-subtle));
        }
        .incidents-count {
          font-size: 13px;
          font-weight: 500;
          color: hsl(var(--text-muted));
        }

        /* ── Incident row ────────────────────────────────────────── */
        .incident-list {
          display: flex;
          flex-direction: column;
        }
        .incident-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
          padding: 16px 20px;
          text-decoration: none;
          border-bottom: 1px solid hsl(var(--border-subtle));
          transition: background 120ms ease;
        }
        .incident-row:last-child { border-bottom: none; }
        .incident-row:hover { background: hsl(var(--surface)); }

        .incident-row__main { flex: 1; min-width: 0; }
        .incident-row__badges {
          display: flex;
          gap: 6px;
          margin-bottom: 6px;
        }
        .incident-row__title {
          display: block;
          font-size: 14px;
          font-weight: 600;
          color: hsl(var(--text-primary));
          line-height: 1.4;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .incident-row__desc {
          display: block;
          font-size: 12px;
          color: hsl(var(--text-muted));
          line-height: 1.5;
          margin-top: 2px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .incident-row__meta {
          display: flex;
          align-items: center;
          gap: 12px;
          flex-shrink: 0;
        }
        .incident-row__date {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: hsl(var(--text-muted));
          white-space: nowrap;
        }
        .incident-row__arrow {
          color: hsl(var(--text-disabled));
          transition: transform 120ms ease;
        }
        .incident-row:hover .incident-row__arrow {
          transform: translateX(2px);
          color: hsl(var(--text-secondary));
        }

        /* ── Empty state ─────────────────────────────────────────── */
        .empty-container {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 400px;
          background: hsl(var(--surface-raised));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-lg);
        }
        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          padding: 40px 24px;
          max-width: 360px;
        }
        .empty-state__icon {
          width: 56px;
          height: 56px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: hsl(var(--warning) / 0.12);
          border: 1px solid hsl(var(--warning) / 0.2);
          border-radius: var(--radius-xl);
          color: hsl(var(--warning));
          margin-bottom: 20px;
        }
        .empty-state__title {
          font-size: 16px;
          font-weight: 600;
          color: hsl(var(--text-primary));
          margin: 0 0 8px;
        }
        .empty-state__description {
          font-size: 13px;
          color: hsl(var(--text-muted));
          line-height: 1.6;
          margin: 0 0 24px;
        }

        /* ── Buttons ─────────────────────────────────────────────── */
        .btn {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 7px 14px;
          font-size: 13px;
          font-weight: 500;
          font-family: var(--font-sans);
          border-radius: var(--radius-md);
          text-decoration: none;
          cursor: pointer;
          border: 1px solid transparent;
          transition: opacity 150ms ease, background 150ms ease;
        }
        .btn--primary {
          background: hsl(var(--accent));
          color: #fff;
        }
        .btn--primary:hover { opacity: 0.88; }

        /* ── Loading skeletons ───────────────────────────────────── */
        .skeleton-row {
          padding: 16px 20px;
          border-bottom: 1px solid hsl(var(--border-subtle));
        }
        .skeleton-row:last-child { border-bottom: none; }
      `}</style>
    </>
  )
}
