"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useActiveWorkspace } from "@/features/workspaces/hooks/useWorkspaces"
import { createRepository } from "@/features/repositories/api"
import { ApiError } from "@/lib/api-client"
import { ArrowLeft, GitBranch } from "lucide-react"
import Link from "next/link"

// ── Validation schema ─────────────────────────────────────────────────────────

const createRepoSchema = z.object({
  name: z
    .string()
    .min(1, "Repository name is required.")
    .max(200, "Name is too long."),
  full_name: z
    .string()
    .min(1, "Full name is required (e.g. 'org/repo').")
    .max(300)
    .regex(
      /^[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+$/,
      "Use the format 'owner/repository' (e.g. 'facebook/react')."
    ),
  clone_url: z
    .string()
    .min(1, "Clone URL is required.")
    .url("Enter a valid URL.")
    .refine(
      (v) => v.startsWith("https://"),
      "Clone URL must start with 'https://'."
    ),
  default_branch: z.string().min(1).max(100).default("main"),
  description: z.string().max(500).optional(),
})

type CreateRepoValues = z.infer<typeof createRepoSchema>

// ── Auto-fill helper ──────────────────────────────────────────────────────────

function deriveFromFullName(fullName: string) {
  const parts = fullName.split("/")
  if (parts.length !== 2) return {}
  const name = parts[1]
  const cloneUrl = `https://github.com/${fullName}.git`
  return { name, cloneUrl }
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function ConnectRepositoryPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { activeWorkspace } = useActiveWorkspace()
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<CreateRepoValues>({
    resolver: zodResolver(createRepoSchema),
    defaultValues: {
      default_branch: "main",
    },
  })

  const mutation = useMutation({
    mutationFn: (values: CreateRepoValues) =>
      createRepository(activeWorkspace!.id, values),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["repositories", activeWorkspace?.id],
      })
      router.push("/app/repositories")
    },
    onError: (err) => {
      if (err instanceof ApiError) {
        setServerError(err.message)
      } else {
        setServerError("Failed to connect repository. Please try again.")
      }
    },
  })

  const onSubmit = (values: CreateRepoValues) => {
    setServerError(null)
    mutation.mutate(values)
  }

  // Auto-fill name and clone_url when full_name changes
  const handleFullNameBlur = () => {
    const fullName = watch("full_name")
    if (fullName) {
      const derived = deriveFromFullName(fullName)
      if (derived.name && !watch("name")) {
        setValue("name", derived.name)
      }
      if (derived.cloneUrl && !watch("clone_url")) {
        setValue("clone_url", derived.cloneUrl)
      }
    }
  }

  return (
    <>
      <div className="connect-page">
        {/* Back link */}
        <Link href="/app/repositories" className="back-link">
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Back to repositories
        </Link>

        {/* Header */}
        <div className="connect-header">
          <div className="connect-header__icon">
            <GitBranch className="h-6 w-6" aria-hidden="true" />
          </div>
          <div>
            <h1 className="page-title">Connect repository</h1>
            <p className="page-subtitle">
              Register a GitHub repository for AI-powered code analysis.
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

          <form onSubmit={handleSubmit(onSubmit)} noValidate className="connect-form">
            {/* Full name */}
            <div className="form-field">
              <label htmlFor="repo-full-name" className="form-field__label">
                Repository <span className="required">*</span>
              </label>
              <input
                id="repo-full-name"
                type="text"
                autoFocus
                autoComplete="off"
                disabled={isSubmitting}
                aria-invalid={!!errors.full_name}
                aria-describedby={errors.full_name ? "repo-full-name-error" : "repo-full-name-hint"}
                className={`form-field__input ${errors.full_name ? "form-field__input--error" : ""}`}
                placeholder="facebook/react"
                {...register("full_name", { onBlur: handleFullNameBlur })}
              />
              <p id="repo-full-name-hint" className="form-field__hint">
                Enter as owner/repository (e.g. &quot;facebook/react&quot;).
              </p>
              {errors.full_name && (
                <p id="repo-full-name-error" className="form-field__error" role="alert">
                  {errors.full_name.message}
                </p>
              )}
            </div>

            {/* Name */}
            <div className="form-field">
              <label htmlFor="repo-name" className="form-field__label">
                Display name <span className="required">*</span>
              </label>
              <input
                id="repo-name"
                type="text"
                autoComplete="off"
                disabled={isSubmitting}
                aria-invalid={!!errors.name}
                className={`form-field__input ${errors.name ? "form-field__input--error" : ""}`}
                placeholder="react"
                {...register("name")}
              />
              {errors.name && (
                <p className="form-field__error" role="alert">
                  {errors.name.message}
                </p>
              )}
            </div>

            {/* Clone URL */}
            <div className="form-field">
              <label htmlFor="repo-clone-url" className="form-field__label">
                Clone URL <span className="required">*</span>
              </label>
              <input
                id="repo-clone-url"
                type="url"
                autoComplete="off"
                disabled={isSubmitting}
                aria-invalid={!!errors.clone_url}
                className={`form-field__input form-field__input--mono ${errors.clone_url ? "form-field__input--error" : ""}`}
                placeholder="https://github.com/facebook/react.git"
                {...register("clone_url")}
              />
              {errors.clone_url && (
                <p className="form-field__error" role="alert">
                  {errors.clone_url.message}
                </p>
              )}
            </div>

            {/* Default branch */}
            <div className="form-field">
              <label htmlFor="repo-branch" className="form-field__label">
                Default branch
              </label>
              <input
                id="repo-branch"
                type="text"
                autoComplete="off"
                disabled={isSubmitting}
                className="form-field__input"
                placeholder="main"
                {...register("default_branch")}
              />
            </div>

            {/* Description */}
            <div className="form-field">
              <label htmlFor="repo-description" className="form-field__label">
                Description
              </label>
              <textarea
                id="repo-description"
                rows={3}
                disabled={isSubmitting}
                className="form-field__input form-field__textarea"
                placeholder="Optional description of this repository…"
                {...register("description")}
              />
            </div>

            {/* Actions */}
            <div className="form-actions">
              <Link href="/app/repositories" className="btn btn--ghost">
                Cancel
              </Link>
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn btn--primary"
                aria-busy={isSubmitting}
              >
                {isSubmitting && <span className="btn-spinner" aria-hidden="true" />}
                {isSubmitting ? "Connecting…" : "Connect repository"}
              </button>
            </div>
          </form>
        </div>
      </div>

      <style>{`
        .connect-page { max-width: 640px; }

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

        .connect-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 28px;
        }
        .connect-header__icon {
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: hsl(var(--accent-muted));
          border-radius: var(--radius-lg);
          color: hsl(var(--accent));
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

        .connect-form {
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
        .form-field__input--error:focus {
          box-shadow: 0 0 0 3px hsl(var(--danger) / 0.18);
        }
        .form-field__input:disabled { opacity: 0.6; cursor: not-allowed; }
        .form-field__textarea { resize: vertical; min-height: 80px; }
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
