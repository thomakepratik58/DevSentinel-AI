import type { Metadata } from "next"

export const metadata: Metadata = {
  title: {
    default: "Sign in",
    template: "%s · DevSentinel AI",
  },
}

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="auth-layout">
      <div className="auth-layout__brand">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
          <rect width="28" height="28" rx="7" fill="hsl(252 83% 66%)" />
          <path
            d="M8 14.5L12.5 19L20 10"
            stroke="white"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <span className="auth-layout__brand-name">DevSentinel AI</span>
      </div>

      <main className="auth-layout__main">
        <div className="auth-layout__card">
          {children}
        </div>
      </main>

      <footer className="auth-layout__footer">
        <p>© 2026 DevSentinel AI. All rights reserved.</p>
      </footer>

      <style>{`
        .auth-layout {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          background: hsl(var(--background));
          position: relative;
          overflow: hidden;
        }

        /* Subtle background gradient mesh */
        .auth-layout::before {
          content: '';
          position: absolute;
          inset: 0;
          background:
            radial-gradient(ellipse 80% 60% at 50% -20%, hsl(252 83% 66% / 0.12) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 80%, hsl(217 91% 65% / 0.07) 0%, transparent 50%);
          pointer-events: none;
        }

        .auth-layout__brand {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 24px 32px;
          position: relative;
          z-index: 1;
        }

        .auth-layout__brand-name {
          font-size: 15px;
          font-weight: 600;
          color: hsl(var(--text-primary));
          letter-spacing: -0.01em;
        }

        .auth-layout__main {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px 16px;
          position: relative;
          z-index: 1;
        }

        .auth-layout__card {
          width: 100%;
          max-width: 400px;
          background: hsl(var(--surface-raised));
          border: 1px solid hsl(var(--border-subtle));
          border-radius: var(--radius-xl);
          padding: 36px 32px;
          box-shadow: var(--shadow-overlay);
        }

        .auth-layout__footer {
          padding: 20px 32px;
          text-align: center;
          position: relative;
          z-index: 1;
        }

        .auth-layout__footer p {
          font-size: 12px;
          color: hsl(var(--text-muted));
        }
      `}</style>
    </div>
  )
}
