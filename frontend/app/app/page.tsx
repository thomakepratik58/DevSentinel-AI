import {
  AlertTriangle,
  Activity,
  CheckCircle,
  GitBranch,
  Clock,
  GitPullRequest,
  Plus,
} from "lucide-react";

export default function DashboardOverview() {
  return (
    <div className="space-y-6">
      {/* ── Page header ──────────────────────────────────── */}
      <div>
        <h1 className="text-[28px] font-semibold leading-9 tracking-[-0.02em] text-text-primary">
          Overview
        </h1>
        <p className="mt-1 text-sm text-text-muted">
          Active investigations, codebase health, and recent AI operations.
        </p>
      </div>

      {/* ── Metric cards row (design.md §16.3 / §17.4) ──── */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <MetricCard
          label="Open incidents"
          value="0"
          icon={AlertTriangle}
          iconColor="text-status-warning"
        />
        <MetricCard
          label="Active analyses"
          value="0"
          icon={Activity}
          iconColor="text-status-info"
        />
        <MetricCard
          label="Patch validation rate"
          value="—"
          icon={CheckCircle}
          iconColor="text-status-success"
        />
        <MetricCard
          label="Repositories indexed"
          value="0"
          icon={GitBranch}
          iconColor="text-accent"
        />
        <MetricCard
          label="Avg. analysis latency"
          value="—"
          icon={Clock}
          iconColor="text-text-muted"
        />
      </div>

      {/* ── Two-column main grid ─────────────────────────── */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Recent incidents (empty state) */}
        <div className="lg:col-span-2 rounded-xl border border-border-subtle bg-surface">
          <div className="flex items-center justify-between border-b border-border-subtle px-5 py-3">
            <h2 className="text-sm font-semibold text-text-primary">
              Recent incidents
            </h2>
            <button
              className="inline-flex items-center gap-1.5 rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white hover:bg-accent/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            >
              <Plus className="h-3 w-3" aria-hidden="true" />
              New incident
            </button>
          </div>
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-border-subtle bg-surface-raised">
              <AlertTriangle className="h-5 w-5 text-text-muted" aria-hidden="true" />
            </div>
            <h3 className="mt-4 text-sm font-semibold text-text-primary">
              No incidents reported yet
            </h3>
            <p className="mt-1 max-w-xs text-sm text-text-muted">
              Create an incident from a stack trace, bug report, or failing test
              to start an AI-guided investigation.
            </p>
            <button className="mt-5 inline-flex items-center gap-1.5 rounded-lg border border-border-subtle bg-surface-raised px-4 py-2 text-sm font-medium text-text-primary hover:bg-surface transition-colors">
              <Plus className="h-3.5 w-3.5" aria-hidden="true" />
              Create incident
            </button>
          </div>
        </div>

        {/* Activity rail (right column) */}
        <div className="space-y-4">
          {/* Repository health */}
          <div className="rounded-xl border border-border-subtle bg-surface">
            <div className="border-b border-border-subtle px-5 py-3">
              <h2 className="text-sm font-semibold text-text-primary">
                Repository health
              </h2>
            </div>
            <div className="flex flex-col items-center justify-center py-10 text-center px-5">
              <GitBranch
                className="h-5 w-5 text-text-muted"
                aria-hidden="true"
              />
              <p className="mt-3 text-sm text-text-muted">
                No repositories connected.
              </p>
              <button className="mt-4 inline-flex items-center gap-1.5 rounded-lg border border-border-subtle bg-surface-raised px-3 py-1.5 text-xs font-medium text-text-primary hover:bg-surface transition-colors">
                Connect repository
              </button>
            </div>
          </div>

          {/* Patch review queue */}
          <div className="rounded-xl border border-border-subtle bg-surface">
            <div className="border-b border-border-subtle px-5 py-3">
              <h2 className="text-sm font-semibold text-text-primary">
                Patch review queue
              </h2>
            </div>
            <div className="flex flex-col items-center justify-center py-10 text-center px-5">
              <GitPullRequest
                className="h-5 w-5 text-text-muted"
                aria-hidden="true"
              />
              <p className="mt-3 text-sm text-text-muted">
                No patches awaiting review.
              </p>
            </div>
          </div>

          {/* System health */}
          <div className="rounded-xl border border-border-subtle bg-surface">
            <div className="border-b border-border-subtle px-5 py-3">
              <h2 className="text-sm font-semibold text-text-primary">
                System health
              </h2>
            </div>
            <div className="divide-y divide-border-subtle">
              <HealthRow label="API" status="healthy" />
              <HealthRow label="Database" status="connected" />
              <HealthRow label="Redis" status="connected" />
              <HealthRow label="AI provider" status="not configured" variant="warning" />
              <HealthRow label="Worker queue" status="idle" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Sub-components ────────────────────────────────────────── */

function MetricCard({
  label,
  value,
  icon: Icon,
  iconColor,
}: {
  label: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
  iconColor: string;
}) {
  return (
    <div className="rounded-xl border border-border-subtle bg-surface p-4 space-y-2">
      <div className="flex items-center gap-2">
        <Icon className={`h-4 w-4 ${iconColor}`} aria-hidden="true" />
        <span className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-muted">
          {label}
        </span>
      </div>
      <p className="text-2xl font-semibold tabular-nums text-text-primary">
        {value}
      </p>
    </div>
  );
}

function HealthRow({
  label,
  status,
  variant = "success",
}: {
  label: string;
  status: string;
  variant?: "success" | "warning" | "danger";
}) {
  const dotColor =
    variant === "warning"
      ? "bg-status-warning"
      : variant === "danger"
        ? "bg-status-danger"
        : "bg-status-success";

  return (
    <div className="flex items-center justify-between px-5 py-2.5">
      <span className="text-sm text-text-secondary">{label}</span>
      <div className="flex items-center gap-2">
        <div className={`h-2 w-2 rounded-full ${dotColor}`} />
        <span className="text-xs text-text-muted">{status}</span>
      </div>
    </div>
  );
}
