"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useActiveWorkspace } from "@/features/workspaces/hooks/useWorkspaces"
import { listRepositories, deleteRepository } from "@/features/repositories/api"
import type { Repository, RepositoryListResponse } from "@/features/repositories/types"
import {
  GitBranch,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Trash2,
  ExternalLink,
} from "lucide-react"
import Link from "next/link"

// ── Status badge ──────────────────────────────────────────────────────────────

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: typeof CheckCircle2 }> = {
  pending: { label: "Pending", color: "var(--warning)", icon: Clock },
  indexing: { label: "Indexing", color: "var(--info)", icon: Loader2 },
  ready: { label: "Ready", color: "var(--success)", icon: CheckCircle2 },
  error: { label: "Error", color: "var(--danger)", icon: AlertCircle },
  archived: { label: "Archived", color: "var(--text-muted)", icon: Clock },
}

function StatusBadge({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.pending
  const Icon = config.icon
  return (
    <span className="status-badge" style={{ "--badge-color": `hsl(${config.color})` } as React.CSSProperties}>
      <Icon className="status-badge__icon" aria-hidden="true" />
      {config.label}
    </span>
  )
}

// ── Repository card ───────────────────────────────────────────────────────────

function RepoCard({
  repo,
  workspaceId,
  onDelete,
}: {
  repo: Repository
  workspaceId: string
  onDelete: (id: string) => void
}) {
  return (
    <div className="repo-card">
      <div className="repo-card__header">
        <div className="repo-card__icon-wrap">
          <GitBranch className="repo-card__icon" aria-hidden="true" />
        </div>
        <div className="repo-card__info">
          <span className="repo-card__name">{repo.name}</span>
          <span className="repo-card__full-name">{repo.full_name}</span>
        </div>
        <StatusBadge status={repo.status} />
      </div>

      {repo.description && (
        <p className="repo-card__description">{repo.description}</p>
      )}

      <div className="repo-card__meta">
        <span className="repo-card__branch">
          <GitBranch className="h-3 w-3" aria-hidden="true" />
          {repo.default_branch}
        </span>
        <span className="repo-card__date">
          <Clock className="h-3 w-3" aria-hidden="true" />
          Connected {new Date(repo.created_at).toLocaleDateString()}
        </span>
      </div>

      <div className="repo-card__actions">
        <a
          href={repo.clone_url.replace(".git", "")}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn--ghost btn--sm"
        >
          <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
          View on GitHub
        </a>
        <button
          onClick={() => onDelete(repo.id)}
          className="btn btn--danger-ghost btn--sm"
          aria-label={`Delete ${repo.name}`}
        >
          <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
          Remove
        </button>
      </div>
    </div>
  )
}

// ── Empty state ───────────────────────────────────────────────────────────────

function EmptyRepositories() {
  return (
    <div className="empty-state" role="status">
      <div className="empty-state__icon">
        <GitBranch className="h-6 w-6" aria-hidden="true" />
      </div>
      <h3 className="empty-state__title">No repositories connected</h3>
      <p className="empty-state__description">
        Connect a GitHub repository to start indexing code for AI-powered
        incident analysis and root cause detection.
      </p>
      <Link href="/app/repositories/new" className="btn btn--primary">
        <Plus className="h-4 w-4" aria-hidden="true" />
        Connect repository
      </Link>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function RepositoriesPage() {
  const { activeWorkspace, isLoading: wsLoading } = useActiveWorkspace()
  const queryClient = useQueryClient()

  const {
    data,
    isLoading: repoLoading,
    error,
  } = useQuery<RepositoryListResponse, Error>({
    queryKey: ["repositories", activeWorkspace?.id],
    queryFn: () => listRepositories(activeWorkspace!.id),
    enabled: !!activeWorkspace,
  })

  const deleteMutation = useMutation({
    mutationFn: (repoId: string) =>
      deleteRepository(activeWorkspace!.id, repoId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["repositories", activeWorkspace?.id],
      })
    },
  })

  const isLoading = wsLoading || repoLoading
  const repos = data?.repositories ?? []

  return (
    <>
      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Repositories</h1>
          <p className="page-subtitle">
            Manage connected source-code repositories for AI analysis.
          </p>
        </div>
        {repos.length > 0 && (
          <Link href="/app/repositories/new" className="btn btn--primary">
            <Plus className="h-4 w-4" aria-hidden="true" />
            Connect repository
          </Link>
        )}
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="loading-grid">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton-card">
              <div className="skeleton" style={{ height: 20, width: "60%" }} />
              <div className="skeleton" style={{ height: 14, width: "40%", marginTop: 8 }} />
              <div className="skeleton" style={{ height: 14, width: "80%", marginTop: 16 }} />
            </div>
          ))}
        </div>
      ) : repos.length === 0 ? (
        <div className="empty-container">
          <EmptyRepositories />
        </div>
      ) : (
        <div className="repo-grid">
          {repos.map((repo) => (
            <RepoCard
              key={repo.id}
              repo={repo}
              workspaceId={activeWorkspace!.id}
              onDelete={(id) => deleteMutation.mutate(id)}
            />
          ))}
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

        /* ── Repo grid ───────────────────────────────────────────── */
        .repo-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
          gap: 16px;
        }
        @media (max-width: 500px) {
          .repo-grid { grid-template-columns: 1fr; }
        }

        /* ── Repo card ───────────────────────────────────────────── */
        .repo-card {
          background: hsl(var(--surface-raised));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-lg);
          padding: 20px;
          transition: border-color 150ms ease, box-shadow 200ms ease;
        }
        .repo-card:hover {
          border-color: hsl(var(--border-strong));
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }

        .repo-card__header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .repo-card__icon-wrap {
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
        .repo-card__icon { width: 18px; height: 18px; }

        .repo-card__info {
          flex: 1;
          min-width: 0;
        }
        .repo-card__name {
          display: block;
          font-size: 15px;
          font-weight: 600;
          color: hsl(var(--text-primary));
          line-height: 1.3;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .repo-card__full-name {
          display: block;
          font-size: 12px;
          color: hsl(var(--text-muted));
          font-family: var(--font-mono);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .repo-card__description {
          font-size: 13px;
          color: hsl(var(--text-secondary));
          line-height: 1.5;
          margin: 0 0 12px;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .repo-card__meta {
          display: flex;
          align-items: center;
          gap: 16px;
          font-size: 12px;
          color: hsl(var(--text-muted));
          margin-bottom: 16px;
        }
        .repo-card__branch,
        .repo-card__date {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .repo-card__actions {
          display: flex;
          gap: 8px;
          padding-top: 12px;
          border-top: 1px solid hsl(var(--border-subtle));
        }

        /* ── Status badge ────────────────────────────────────────── */
        .status-badge {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 3px 10px;
          font-size: 11px;
          font-weight: 600;
          border-radius: 999px;
          color: var(--badge-color);
          background: color-mix(in srgb, var(--badge-color) 12%, transparent);
          border: 1px solid color-mix(in srgb, var(--badge-color) 25%, transparent);
          white-space: nowrap;
          flex-shrink: 0;
        }
        .status-badge__icon { width: 12px; height: 12px; }

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
        .btn--sm { padding: 5px 10px; font-size: 12px; }
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
        .btn--danger-ghost {
          background: transparent;
          border-color: hsl(var(--border-subtle));
          color: hsl(var(--text-muted));
        }
        .btn--danger-ghost:hover {
          color: hsl(var(--danger));
          border-color: hsl(var(--danger) / 0.3);
          background: hsl(var(--danger) / 0.08);
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
          background: hsl(var(--accent-muted));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-xl);
          color: hsl(var(--accent));
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

        /* ── Loading skeletons ───────────────────────────────────── */
        .loading-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
          gap: 16px;
        }
        .skeleton-card {
          background: hsl(var(--surface-raised));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-lg);
          padding: 20px;
        }
      `}</style>
    </>
  )
}
