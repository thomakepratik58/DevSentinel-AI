"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import Link from "next/link"
import { loginUser } from "@/features/auth/api"
import { ApiError } from "@/lib/api-client"
import { useQueryClient } from "@tanstack/react-query"
import { CURRENT_USER_QUERY_KEY } from "@/features/auth/hooks/useCurrentUser"

// ── Validation schema ─────────────────────────────────────────────────────────

const loginSchema = z.object({
  email: z
    .string()
    .min(1, "Email address is required.")
    .email("Enter a valid email address."),
  password: z
    .string()
    .min(1, "Password is required."),
})

type LoginFormValues = z.infer<typeof loginSchema>

// ── Page ──────────────────────────────────────────────────────────────────────

export default function LoginPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (values: LoginFormValues) => {
    setServerError(null)
    try {
      const result = await loginUser(values)
      // Pre-populate the user query cache to avoid an extra network hit
      queryClient.setQueryData(CURRENT_USER_QUERY_KEY, result.user)
      router.push("/app/dashboard")
    } catch (err) {
      if (err instanceof ApiError) {
        setServerError(err.message)
      } else {
        setServerError("Unable to sign in. Check your connection and try again.")
      }
    }
  }

  return (
    <>
      <div className="auth-card__header">
        <h1 className="auth-card__title">Sign in</h1>
        <p className="auth-card__subtitle">
          Sign in to your DevSentinel AI account.
        </p>
      </div>

      {serverError && (
        <div className="auth-error" role="alert" aria-live="assertive">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <circle cx="8" cy="8" r="7" stroke="hsl(var(--danger))" strokeWidth="1.5" />
            <path d="M8 5v3.5M8 11v.5" stroke="hsl(var(--danger))" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          {serverError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="auth-form">
        {/* Email */}
        <div className="auth-field">
          <label htmlFor="login-email" className="auth-field__label">
            Email address
          </label>
          <input
            id="login-email"
            type="email"
            autoComplete="email"
            autoFocus
            disabled={isSubmitting}
            aria-invalid={!!errors.email}
            aria-describedby={errors.email ? "login-email-error" : undefined}
            className={`auth-field__input ${errors.email ? "auth-field__input--error" : ""}`}
            placeholder="you@company.com"
            {...register("email")}
          />
          {errors.email && (
            <p id="login-email-error" className="auth-field__error" role="alert">
              {errors.email.message}
            </p>
          )}
        </div>

        {/* Password */}
        <div className="auth-field">
          <div className="auth-field__row">
            <label htmlFor="login-password" className="auth-field__label">
              Password
            </label>
          </div>
          <input
            id="login-password"
            type="password"
            autoComplete="current-password"
            disabled={isSubmitting}
            aria-invalid={!!errors.password}
            aria-describedby={errors.password ? "login-password-error" : undefined}
            className={`auth-field__input ${errors.password ? "auth-field__input--error" : ""}`}
            placeholder="••••••••"
            {...register("password")}
          />
          {errors.password && (
            <p id="login-password-error" className="auth-field__error" role="alert">
              {errors.password.message}
            </p>
          )}
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="auth-submit"
          aria-busy={isSubmitting}
        >
          {isSubmitting ? (
            <span className="auth-submit__spinner" aria-hidden="true" />
          ) : null}
          {isSubmitting ? "Signing in…" : "Sign in"}
        </button>
      </form>

      <p className="auth-card__footer-text">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="auth-link">
          Create account
        </Link>
      </p>

      <style>{`
        .auth-card__header { margin-bottom: 24px; }
        .auth-card__title {
          font-size: 22px;
          font-weight: 700;
          letter-spacing: -0.02em;
          color: hsl(var(--text-primary));
          margin: 0 0 6px;
        }
        .auth-card__subtitle {
          font-size: 14px;
          color: hsl(var(--text-muted));
          margin: 0;
        }

        .auth-error {
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
        .auth-error svg { margin-top: 1px; flex-shrink: 0; }

        .auth-form { display: flex; flex-direction: column; gap: 16px; }

        .auth-field { display: flex; flex-direction: column; gap: 6px; }
        .auth-field__row {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .auth-field__label {
          font-size: 13px;
          font-weight: 500;
          color: hsl(var(--text-secondary));
        }
        .auth-field__input {
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
        .auth-field__input::placeholder { color: hsl(var(--text-disabled)); }
        .auth-field__input:focus {
          border-color: hsl(var(--accent));
          box-shadow: 0 0 0 3px hsl(var(--accent) / 0.18);
        }
        .auth-field__input--error { border-color: hsl(var(--danger)); }
        .auth-field__input--error:focus {
          box-shadow: 0 0 0 3px hsl(var(--danger) / 0.18);
        }
        .auth-field__input:disabled { opacity: 0.6; cursor: not-allowed; }
        .auth-field__error {
          font-size: 12px;
          color: hsl(var(--danger));
          margin: 0;
        }

        .auth-submit {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 10px;
          margin-top: 4px;
          font-size: 14px;
          font-weight: 600;
          font-family: var(--font-sans);
          background: hsl(var(--accent));
          color: #fff;
          border: none;
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: opacity 150ms ease, transform 150ms ease;
        }
        .auth-submit:hover:not(:disabled) { opacity: 0.92; }
        .auth-submit:active:not(:disabled) { transform: scale(0.99); }
        .auth-submit:disabled { opacity: 0.6; cursor: not-allowed; }

        .auth-submit__spinner {
          width: 15px;
          height: 15px;
          border: 2px solid rgba(255,255,255,0.35);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin 0.65s linear infinite;
          flex-shrink: 0;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .auth-card__footer-text {
          margin-top: 20px;
          text-align: center;
          font-size: 13px;
          color: hsl(var(--text-muted));
        }
        .auth-link {
          color: hsl(var(--accent));
          text-decoration: none;
          font-weight: 500;
        }
        .auth-link:hover { text-decoration: underline; }
      `}</style>
    </>
  )
}
