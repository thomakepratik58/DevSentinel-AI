"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useActiveWorkspace } from "@/features/workspaces/hooks/useWorkspaces"
import { createIncident } from "@/features/incidents/api"
import { listRepositories } from "@/features/repositories/api"
import { ApiError } from "@/lib/api-client"
import type { RepositoryListResponse } from "@/features/repositories/types"
import { ArrowLeft, AlertTriangle } from "lucide-react"
import Link from "next/link"

// ── Validation schema ─────────────────────────────────────────────────────────

const createIncidentSchema = z.object({
  title: z
    .string()
    .min(3, "Title must be at least 3 characters.")
    .max(300, "Title is too long."),
  description: z
    .string()
    .max(10_000)
    .optional(),
  severity: z.enum(["critical", "high", "medium", "low", "info"]).default("medium"),
  repository_id: z.string().optional(),
})

type CreateIncidentValues = z.infer<typeof createIncidentSchema>

// ── Page ──────────────────────────────────────────────────────────────────────

export default function CreateIncidentPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { activeWorkspace } = useActiveWorkspace()
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateIncidentValues>({
    resolver: zodResolver(createIncidentSchema),
    defaultValues: { severity: "medium" },
  })

  // Fetch repos for the dropdown
  const { data: reposData } = useQuery<RepositoryListResponse, Error>({
    queryKey: ["repositories", activeWorkspace?.id],
    queryFn: () => listRepositories(activeWorkspace!.id),
    enabled: !!activeWorkspace,
  })

  const mutation = useMutation({
    mutationFn: (values: CreateIncidentValues) =>
      createIncident(activeWorkspace!.id, {
        title: values.title,
        description: values.description || undefined,
        severity: values.severity,
        repository_id: values.repository_id || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["incidents", activeWorkspace?.id],
      })
      router.push("/app/incidents")
    },
    onError: (err) => {
      if (err instanceof ApiError) {
        setServerError(err.message)
      } else {
        setServerError("Failed to create incident. Please try again.")
      }
    },
  })

  const onSubmit = (values: CreateIncidentValues) => {
    setServerError(null)
    mutation.mutate(values)
  }

  const repos = reposData?.repositories ?? []

  return (
    <>
      <div className="create-page">
        {/* Back link */}
        <Link href="/app/incidents" className="back-link">
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Back to incidents
        </Link>

        {/* Header */}
        <div className="create-header">
          <div className="create-header__icon">
            <AlertTriangle className="h-6 w-6" aria-hidden="true" />
          </div>
          <div>
            <h1 className="page-title">Create incident</h1>
            <p className="page-subtitle">
              Report a production issue for AI-powered root cause analysis.
            </p>
          </div>
        </div>

        {/* Form card */}
        <div className="form-card">
          {serverError && (
            <div className="form-error" role="alert" aria-live="assertive">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                <circle cx="8" cy="8" r="7" stroke="hsl(var(--danger))" strokeWidth="1.5" />
                <path d="M8 5v3.5M8 11v.5" stroke="hsl(var(--danger))" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
              {serverError}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} noValidate className="create-form">
            {/* Title */}
            <div className="form-field">
              <label htmlFor="incident-title" className="form-field__label">
                Title <span className="required">*</span>
              </label>
              <input
                id="incident-title"
                type="text"
                autoFocus
                autoComplete="off"
                disabled={isSubmitting}
                aria-invalid={!!errors.title}
                className={`form-field__input ${errors.title ? "form-field__input--error" : ""}`}
                placeholder="500 errors on /api/v1/checkout after deploy"
                {...register("title")}
              />
              {errors.title && (
                <p className="form-field__error" role="alert">
                  {errors.title.message}
                </p>
              )}
            </div>

            {/* Severity */}
            <div className="form-field">
              <label htmlFor="incident-severity" className="form-field__label">
                Severity
              </label>
              <select
                id="incident-severity"
                disabled={isSubmitting}
                className="form-field__input form-field__select"
                {...register("severity")}
              >
                <option value="critical">🔴 Critical — Service down</option>
                <option value="high">🟠 High — Major feature impacted</option>
                <option value="medium">🟡 Medium — Degraded performance</option>
                <option value="low">🔵 Low — Minor issue</option>
                <option value="info">⚪ Info — Observation</option>
              </select>
            </div>

            {/* Repository link */}
            {repos.length > 0 && (
              <div className="form-field">
                <label htmlFor="incident-repo" className="form-field__label">
                  Linked repository
                </label>
                <select
                  id="incident-repo"
                  disabled={isSubmitting}
                  className="form-field__input form-field__select"
                  {...register("repository_id")}
                >
                  <option value="">None — no repository linked</option>
                  {repos.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.full_name}
                    </option>
                  ))}
                </select>
                <p className="form-field__hint">
                  Link to a repository to enable AI code analysis.
                </p>
              </div>
            )}

            {/* Description */}
            <div className="form-field">
              <label htmlFor="incident-description" className="form-field__label">
                Description
              </label>
              <textarea
                id="incident-description"
                rows={8}
                disabled={isSubmitting}
                className="form-field__input form-field__textarea form-field__input--mono"
                placeholder={"Paste stack traces, error logs, or any context here…\n\nExample:\nTypeError: Cannot read property 'id' of undefined\n  at checkout (/src/routes/checkout.ts:42:15)\n  at processPayment (/src/services/payment.ts:128:8)"}
                {...register("description")}
              />
              <p className="form-field__hint">
                Include stack traces, error logs, and reproduction steps for best AI analysis results.
              </p>
            </div>

            {/* Actions */}
            <div className="form-actions">
              <Link href="/app/incidents" className="btn btn--ghost">
                Cancel
              </Link>
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn btn--primary"
                aria-busy={isSubmitting}
              >
                {isSubmitting && <span className="btn-spinner" aria-hidden="true" />}
                {isSubmitting ? "Creating…" : "Create incident"}
              </button>
            </div>
          </form>
        </div>
      </div>

      <style>{`
        .create-page { max-width: 680px; }

        .back-link {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          color: hsl(var(--text-muted));
          text-decoration: none;
          margin-bottom: 24px;
          transition: color 150ms ease;
        }
        .back-link:hover { color: hsl(var(--text-primary)); }

        .create-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 28px;
        }
        .create-header__icon {
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: hsl(var(--warning) / 0.12);
          border-radius: var(--radius-lg);
          color: hsl(var(--warning));
          flex-shrink: 0;
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

        .form-card {
          background: hsl(var(--surface-raised));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-xl);
          padding: 32px;
        }

        .form-error {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          background: hsl(0 72% 60% / 0.1);
          border: 1px solid hsl(0 72% 60% / 0.3);
          border-radius: var(--radius-md);
          padding: 10px 12px;
          font-size: 13px;
          color: hsl(var(--danger));
          margin-bottom: 20px;
          line-height: 1.5;
        }
        .form-error svg { margin-top: 1px; flex-shrink: 0; }

        .create-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .form-field { display: flex; flex-direction: column; gap: 6px; }
        .form-field__label {
          font-size: 13px;
          font-weight: 500;
          color: hsl(var(--text-secondary));
        }
        .required { color: hsl(var(--danger)); }
        .form-field__input {
          width: 100%;
          padding: 9px 12px;
          font-size: 14px;
          font-family: var(--font-sans);
          background: hsl(var(--surface));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-md);
          color: hsl(var(--text-primary));
          outline: none;
          transition: border-color 150ms ease, box-shadow 150ms ease;
          box-sizing: border-box;
        }
        .form-field__input--mono { font-family: var(--font-mono); font-size: 13px; }
        .form-field__input::placeholder { color: hsl(var(--text-disabled)); }
        .form-field__input:focus {
          border-color: hsl(var(--accent));
          box-shadow: 0 0 0 3px hsl(var(--accent) / 0.18);
        }
        .form-field__input--error { border-color: hsl(var(--danger)); }
        .form-field__input:disabled { opacity: 0.6; cursor: not-allowed; }
        .form-field__textarea { resize: vertical; min-height: 160px; line-height: 1.6; }
        .form-field__select {
          appearance: none;
          background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%236B7280' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
          background-repeat: no-repeat;
          background-position: right 12px center;
          padding-right: 36px;
        }
        .form-field__error {
          font-size: 12px;
          color: hsl(var(--danger));
          margin: 0;
        }
        .form-field__hint {
          font-size: 12px;
          color: hsl(var(--text-muted));
          margin: 0;
        }

        .form-actions {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          padding-top: 8px;
          border-top: 1px solid hsl(var(--border-subtle));
        }

        .btn {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 9px 18px;
          font-size: 14px;
          font-weight: 600;
          font-family: var(--font-sans);
          border-radius: var(--radius-md);
          text-decoration: none;
          cursor: pointer;
          border: 1px solid transparent;
          transition: opacity 150ms ease, background 150ms ease, transform 100ms ease;
        }
        .btn--primary {
          background: hsl(var(--accent));
          color: #fff;
        }
        .btn--primary:hover:not(:disabled) { opacity: 0.92; }
        .btn--primary:active:not(:disabled) { transform: scale(0.99); }
        .btn--primary:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn--ghost {
          background: transparent;
          border-color: hsl(var(--border-subtle));
          color: hsl(var(--text-secondary));
        }
        .btn--ghost:hover { background: hsl(var(--surface)); color: hsl(var(--text-primary)); }

        .btn-spinner {
          width: 15px;
          height: 15px;
          border: 2px solid rgba(255,255,255,0.35);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin 0.65s linear infinite;
          flex-shrink: 0;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </>
  )
}
