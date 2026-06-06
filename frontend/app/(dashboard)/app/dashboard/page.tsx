"use client"

import { useCurrentUser } from "@/features/auth/hooks/useCurrentUser"
import {
  GitBranch,
  AlertTriangle,
  Activity,
  CheckCircle2,
  Plus,
  ArrowRight,
} from "lucide-react"
import type { Metadata } from "next"
import Link from "next/link"

// ── Stat card component ───────────────────────────────────────────────────────

interface StatCardProps {
  label: string
  value: string | number
  icon: React.ElementType
  sublabel?: string
  accent?: boolean
}

function StatCard({ label, value, icon: Icon, sublabel, accent }: StatCardProps) {
  return (
    <div className="stat-card" data-accent={accent}>
      <div className="stat-card__header">
        <span className="stat-card__label">{label}</span>
        <div className="stat-card__icon-wrap">
          <Icon className="stat-card__icon" aria-hidden="true" />
        </div>
      </div>
      <div className="stat-card__value">{value}</div>
      {sublabel && <div className="stat-card__sublabel">{sublabel}</div>}
    </div>
  )
}

// ── Empty state component ─────────────────────────────────────────────────────

function EmptyIncidents() {
  return (
    <div className="empty-state" role="status">
      <div className="empty-state__icon">
        <AlertTriangle className="h-6 w-6" aria-hidden="true" />
      </div>
      <h3 className="empty-state__title">No incidents analyzed yet</h3>
      <p className="empty-state__description">
        Create an incident from a stack trace, bug report, or failing test to
        start an AI-guided root cause investigation.
      </p>
      <div className="empty-state__actions">
        <Link href="/app/incidents/new" className="btn btn--primary">
          <Plus className="h-4 w-4" aria-hidden="true" />
          Create incident
        </Link>
        <Link href="/app/repositories" className="btn btn--ghost">
          Connect repository
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </Link>
      </div>
    </div>
  )
}

// ── Quick actions panel ───────────────────────────────────────────────────────

function QuickActions() {
  const actions = [
    {
      href: "/app/repositories/new",
      label: "Connect repository",
      description: "Index a GitHub repository for AI analysis.",
      icon: GitBranch,
    },
    {
      href: "/app/incidents/new",
      label: "Report incident",
      description: "Attach logs or a stack trace to start analysis.",
      icon: AlertTriangle,
    },
  ]

  return (
    <section aria-labelledby="quick-actions-heading">
      <h2 id="quick-actions-heading" className="section-title">
        Quick actions
      </h2>
      <div className="quick-actions">
        {actions.map((action) => {
          const Icon = action.icon
          return (
            <Link key={action.href} href={action.href} className="quick-action-card">
              <div className="quick-action-card__icon-wrap">
                <Icon className="h-5 w-5" aria-hidden="true" />
              </div>
              <div className="quick-action-card__body">
                <span className="quick-action-card__label">{action.label}</span>
                <span className="quick-action-card__desc">{action.description}</span>
              </div>
              <ArrowRight className="quick-action-card__arrow h-4 w-4" aria-hidden="true" />
            </Link>
          )
        })}
      </div>
    </section>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { data: user } = useCurrentUser()

  const stats = [
    {
      label: "Repositories",
      value: 0,
      icon: GitBranch,
      sublabel: "None connected yet",
    },
    {
      label: "Open Incidents",
      value: 0,
      icon: AlertTriangle,
      sublabel: "No open incidents",
    },
    {
      label: "Analysis Runs",
      value: 0,
      icon: Activity,
      sublabel: "No runs started",
    },
    {
      label: "Resolved",
      value: 0,
      icon: CheckCircle2,
      sublabel: "Nothing resolved yet",
      accent: true,
    },
  ]

  const firstName = user?.display_name.split(" ")[0] ?? "there"

  return (
    <>
      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Welcome back, {firstName}</h1>
          <p className="page-subtitle">
            Here&apos;s an overview of your workspace activity.
          </p>
        </div>
      </div>

      {/* Stats row */}
      <section aria-labelledby="stats-heading" className="stats-section">
        <h2 id="stats-heading" className="sr-only">
          Workspace statistics
        </h2>
        <div className="stats-grid">
          {stats.map((stat) => (
            <StatCard key={stat.label} {...stat} />
          ))}
        </div>
      </section>

      {/* Main content: incidents + quick actions */}
      <div className="dashboard-grid">
        {/* Recent incidents */}
        <section aria-labelledby="incidents-heading" className="incidents-section">
          <div className="section-header">
            <h2 id="incidents-heading" className="section-title">
              Recent incidents
            </h2>
            <Link href="/app/incidents" className="section-link">
              View all
              <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
            </Link>
          </div>
          <div className="incidents-panel">
            <EmptyIncidents />
          </div>
        </section>

        {/* Quick actions */}
        <div className="sidebar-column">
          <QuickActions />
        </div>
      </div>

      <style>{`
        /* ── Page header ─────────────────────────────────────────── */
        .page-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          margin-bottom: 28px;
        }
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

        /* ── Stats ───────────────────────────────────────────────── */
        .stats-section { margin-bottom: 32px; }
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
        }
        @media (max-width: 1024px) {
          .stats-grid { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 600px) {
          .stats-grid { grid-template-columns: 1fr; }
        }

        .stat-card {
          background: hsl(var(--surface-raised));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-lg);
          padding: 20px;
          transition: border-color 150ms ease;
        }
        .stat-card:hover {
          border-color: hsl(var(--border-strong));
        }
        .stat-card__header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
        }
        .stat-card__label {
          font-size: 12px;
          font-weight: 500;
          color: hsl(var(--text-muted));
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .stat-card__icon-wrap {
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: hsl(var(--surface));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-sm);
        }
        .stat-card__icon {
          width: 15px;
          height: 15px;
          color: hsl(var(--text-muted));
        }
        .stat-card[data-accent="true"] .stat-card__icon {
          color: hsl(var(--success));
        }
        .stat-card__value {
          font-size: 30px;
          font-weight: 700;
          letter-spacing: -0.03em;
          color: hsl(var(--text-primary));
          line-height: 1;
          margin-bottom: 6px;
          font-variant-numeric: tabular-nums;
        }
        .stat-card__sublabel {
          font-size: 12px;
          color: hsl(var(--text-muted));
        }

        /* ── Dashboard grid ──────────────────────────────────────── */
        .dashboard-grid {
          display: grid;
          grid-template-columns: 1fr 320px;
          gap: 24px;
          align-items: start;
        }
        @media (max-width: 1024px) {
          .dashboard-grid { grid-template-columns: 1fr; }
          .sidebar-column { order: -1; }
        }

        /* ── Section headers ─────────────────────────────────────── */
        .section-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
        }
        .section-title {
          font-size: 14px;
          font-weight: 600;
          color: hsl(var(--text-primary));
          margin: 0;
        }
        .section-link {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: hsl(var(--accent));
          text-decoration: none;
          transition: opacity 150ms ease;
        }
        .section-link:hover { opacity: 0.8; }

        /* ── Incidents panel ─────────────────────────────────────── */
        .incidents-panel {
          background: hsl(var(--surface-raised));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-lg);
          min-height: 280px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        /* ── Empty state ─────────────────────────────────────────── */
        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          padding: 40px 24px;
          max-width: 320px;
        }
        .empty-state__icon {
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: hsl(var(--surface));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-lg);
          color: hsl(var(--text-muted));
          margin-bottom: 16px;
        }
        .empty-state__title {
          font-size: 15px;
          font-weight: 600;
          color: hsl(var(--text-primary));
          margin: 0 0 8px;
        }
        .empty-state__description {
          font-size: 13px;
          color: hsl(var(--text-muted));
          line-height: 1.6;
          margin: 0 0 20px;
        }
        .empty-state__actions {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          justify-content: center;
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
        .btn--ghost {
          background: transparent;
          border-color: hsl(var(--border-subtle));
          color: hsl(var(--text-secondary));
        }
        .btn--ghost:hover {
          background: hsl(var(--surface-raised));
          color: hsl(var(--text-primary));
        }

        /* ── Quick actions ───────────────────────────────────────── */
        .quick-actions {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-top: 12px;
        }
        .quick-action-card {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 14px 16px;
          background: hsl(var(--surface-raised));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-lg);
          text-decoration: none;
          transition: border-color 150ms ease, background 150ms ease;
        }
        .quick-action-card:hover {
          background: hsl(var(--surface));
          border-color: hsl(var(--border-strong));
        }
        .quick-action-card__icon-wrap {
          width: 36px;
          height: 36px;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          background: hsl(var(--accent-muted));
          border-radius: var(--radius-md);
          color: hsl(var(--accent));
        }
        .quick-action-card__body {
          flex: 1;
          min-width: 0;
        }
        .quick-action-card__label {
          display: block;
          font-size: 13px;
          font-weight: 600;
          color: hsl(var(--text-primary));
          margin-bottom: 2px;
        }
        .quick-action-card__desc {
          display: block;
          font-size: 12px;
          color: hsl(var(--text-muted));
          line-height: 1.4;
        }
        .quick-action-card__arrow {
          flex-shrink: 0;
          color: hsl(var(--text-muted));
          transition: transform 150ms ease;
        }
        .quick-action-card:hover .quick-action-card__arrow {
          transform: translateX(2px);
          color: hsl(var(--text-secondary));
        }

        /* ── Screen reader only ──────────────────────────────────── */
        .sr-only {
          position: absolute;
          width: 1px;
          height: 1px;
          padding: 0;
          margin: -1px;
          overflow: hidden;
          clip: rect(0,0,0,0);
          white-space: nowrap;
          border: 0;
        }
      `}</style>
    </>
  )
}
