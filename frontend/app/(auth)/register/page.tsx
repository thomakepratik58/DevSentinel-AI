"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import Link from "next/link"
import { registerUser } from "@/features/auth/api"
import { ApiError } from "@/lib/api-client"
import { useQueryClient } from "@tanstack/react-query"
import { CURRENT_USER_QUERY_KEY } from "@/features/auth/hooks/useCurrentUser"

// ── Validation schema ─────────────────────────────────────────────────────────

const registerSchema = z
  .object({
    display_name: z
      .string()
      .min(2, "Display name must be at least 2 characters.")
      .max(100, "Display name cannot exceed 100 characters.")
      .refine((v) => v.trim().length >= 2, "Display name cannot be blank."),
    email: z
      .string()
      .min(1, "Email address is required.")
      .email("Enter a valid email address."),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters.")
      .max(128, "Password cannot exceed 128 characters.")
      .refine(
        (v) => /[a-zA-Z]/.test(v) && /[0-9]/.test(v),
        "Password must contain at least one letter and one digit."
      ),
    confirm_password: z.string().min(1, "Please confirm your password."),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match.",
    path: ["confirm_password"],
  })

type RegisterFormValues = z.infer<typeof registerSchema>

// ── Password strength indicator ───────────────────────────────────────────────

function passwordStrength(password: string): { score: number; label: string; color: string } {
  if (!password) return { score: 0, label: "", color: "transparent" }
  let score = 0
  if (password.length >= 8) score++
  if (password.length >= 12) score++
  if (/[A-Z]/.test(password)) score++
  if (/[0-9]/.test(password)) score++
  if (/[^a-zA-Z0-9]/.test(password)) score++

  if (score <= 1) return { score: 1, label: "Weak", color: "hsl(var(--danger))" }
  if (score <= 2) return { score: 2, label: "Fair", color: "hsl(var(--warning))" }
  if (score <= 3) return { score: 3, label: "Good", color: "hsl(var(--info))" }
  return { score: 4, label: "Strong", color: "hsl(var(--success))" }
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function RegisterPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [serverError, setServerError] = useState<string | null>(null)
  const [passwordValue, setPasswordValue] = useState("")

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  })

  const strength = passwordStrength(passwordValue)

  const onSubmit = async (values: RegisterFormValues) => {
    setServerError(null)
    try {
      const result = await registerUser({
        email: values.email,
        display_name: values.display_name,
        password: values.password,
      })
      queryClient.setQueryData(CURRENT_USER_QUERY_KEY, result.user)
      router.push("/app/dashboard")
    } catch (err) {
      if (err instanceof ApiError) {
        // Map email-conflict server error to the email field
        if (err.code === "email_already_registered") {
          setError("email", { message: err.message })
        } else {
          setServerError(err.message)
        }
      } else {
        setServerError("Registration failed. Check your connection and try again.")
      }
    }
  }

  return (
    <>
      <div className="auth-card__header">
        <h1 className="auth-card__title">Create account</h1>
        <p className="auth-card__subtitle">
          Start analyzing incidents with AI-powered code intelligence.
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
        {/* Display name */}
        <div className="auth-field">
          <label htmlFor="reg-name" className="auth-field__label">
            Display name
          </label>
          <input
            id="reg-name"
            type="text"
            autoComplete="name"
            autoFocus
            disabled={isSubmitting}
            aria-invalid={!!errors.display_name}
            aria-describedby={errors.display_name ? "reg-name-error" : undefined}
            className={`auth-field__input ${errors.display_name ? "auth-field__input--error" : ""}`}
            placeholder="Alex Johnson"
            {...register("display_name")}
          />
          {errors.display_name && (
            <p id="reg-name-error" className="auth-field__error" role="alert">
              {errors.display_name.message}
            </p>
          )}
        </div>

        {/* Email */}
        <div className="auth-field">
          <label htmlFor="reg-email" className="auth-field__label">
            Email address
          </label>
          <input
            id="reg-email"
            type="email"
            autoComplete="email"
            disabled={isSubmitting}
            aria-invalid={!!errors.email}
            aria-describedby={errors.email ? "reg-email-error" : undefined}
            className={`auth-field__input ${errors.email ? "auth-field__input--error" : ""}`}
            placeholder="you@company.com"
            {...register("email")}
          />
          {errors.email && (
            <p id="reg-email-error" className="auth-field__error" role="alert">
              {errors.email.message}
            </p>
          )}
        </div>

        {/* Password */}
        <div className="auth-field">
          <label htmlFor="reg-password" className="auth-field__label">
            Password
          </label>
          <input
            id="reg-password"
            type="password"
            autoComplete="new-password"
            disabled={isSubmitting}
            aria-invalid={!!errors.password}
            aria-describedby="reg-password-hint reg-password-strength reg-password-error"
            className={`auth-field__input ${errors.password ? "auth-field__input--error" : ""}`}
            placeholder="Min. 8 characters"
            {...register("password", {
              onChange: (e) => setPasswordValue(e.target.value),
            })}
          />
          <p id="reg-password-hint" className="auth-field__hint">
            Must contain at least one letter and one digit.
          </p>
          {passwordValue && (
            <div
              id="reg-password-strength"
              className="strength-meter"
              aria-label={`Password strength: ${strength.label}`}
            >
              <div className="strength-meter__bars">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="strength-meter__bar"
                    style={{
                      background: i <= strength.score ? strength.color : "hsl(var(--border-subtle))",
                    }}
                  />
                ))}
              </div>
              <span className="strength-meter__label" style={{ color: strength.color }}>
                {strength.label}
              </span>
            </div>
          )}
          {errors.password && (
            <p id="reg-password-error" className="auth-field__error" role="alert">
              {errors.password.message}
            </p>
          )}
        </div>

        {/* Confirm password */}
        <div className="auth-field">
          <label htmlFor="reg-confirm" className="auth-field__label">
            Confirm password
          </label>
          <input
            id="reg-confirm"
            type="password"
            autoComplete="new-password"
            disabled={isSubmitting}
            aria-invalid={!!errors.confirm_password}
            aria-describedby={errors.confirm_password ? "reg-confirm-error" : undefined}
            className={`auth-field__input ${errors.confirm_password ? "auth-field__input--error" : ""}`}
            placeholder="Repeat your password"
            {...register("confirm_password")}
          />
          {errors.confirm_password && (
            <p id="reg-confirm-error" className="auth-field__error" role="alert">
              {errors.confirm_password.message}
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
          {isSubmitting && <span className="auth-submit__spinner" aria-hidden="true" />}
          {isSubmitting ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="auth-card__footer-text">
        Already have an account?{" "}
        <Link href="/login" className="auth-link">
          Sign in
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

        .auth-form { display: flex; flex-direction: column; gap: 16px; }

        .auth-field { display: flex; flex-direction: column; gap: 6px; }
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
        .auth-field__hint {
          font-size: 12px;
          color: hsl(var(--text-muted));
          margin: 0;
        }

        .strength-meter {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .strength-meter__bars {
          display: flex;
          gap: 4px;
          flex: 1;
        }
        .strength-meter__bar {
          height: 3px;
          flex: 1;
          border-radius: 2px;
          transition: background 200ms ease;
        }
        .strength-meter__label {
          font-size: 11px;
          font-weight: 600;
          min-width: 40px;
          text-align: right;
          transition: color 200ms ease;
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
