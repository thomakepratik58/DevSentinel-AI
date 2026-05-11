import Link from "next/link";
import {
  GitBranch,
  Bug,
  Search,
  Brain,
  FileCode2,
  FlaskConical,
  ShieldCheck,
  ArrowRight,
  Activity,
  Lock,
  Zap,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* ── Navigation ────────────────────────────────────── */}
      <nav className="border-b border-border-subtle">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
          <span className="text-base font-semibold tracking-tight">
            DevSentinel AI
          </span>
          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="text-sm text-text-secondary hover:text-text-primary transition-colors"
            >
              Sign in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            >
              Get started
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ──────────────────────────────────────────── */}
      <section className="mx-auto max-w-6xl px-6 pb-20 pt-24 text-center">
        <div className="mx-auto max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-border-subtle bg-surface px-3 py-1 text-xs font-medium text-text-secondary">
            <Activity className="h-3 w-3 text-status-success" aria-hidden="true" />
            AI-powered incident analysis
          </div>
          <h1 className="text-5xl font-semibold leading-tight tracking-tight sm:text-6xl">
            Trace production failures to{" "}
            <span className="text-accent">evidence-backed</span> root causes
          </h1>
          <p className="mx-auto max-w-xl text-lg leading-relaxed text-text-muted">
            Connect a repository, attach logs and stack traces, and let
            DevSentinel retrieve relevant code, explain the root cause with
            citations, generate a candidate patch, and validate it in a sandbox.
          </p>
          <div className="flex items-center justify-center gap-4 pt-2">
            <Link
              href="/register"
              className="inline-flex items-center gap-2 rounded-lg bg-accent px-6 py-3 text-sm font-medium text-white shadow-sm hover:bg-accent/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            >
              Analyze an incident
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
            <Link
              href="/app"
              className="inline-flex items-center gap-2 rounded-lg border border-border-subtle bg-surface px-6 py-3 text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-surface-raised transition-colors"
            >
              View demo workflow
            </Link>
          </div>
        </div>
      </section>

      {/* ── Product Preview ───────────────────────────────── */}
      <section className="mx-auto max-w-6xl px-6 pb-24">
        <div className="overflow-hidden rounded-2xl border border-border-subtle bg-surface-raised shadow-[var(--shadow-panel)]">
          <div className="flex h-10 items-center gap-2 border-b border-border-subtle px-4">
            <div className="h-3 w-3 rounded-full bg-status-danger/60" />
            <div className="h-3 w-3 rounded-full bg-status-warning/60" />
            <div className="h-3 w-3 rounded-full bg-status-success/60" />
            <span className="ml-3 text-xs text-text-muted font-mono">
              devsentinel — incident analysis
            </span>
          </div>
          <div className="grid grid-cols-12 divide-x divide-border-subtle">
            {/* Left: Incident list preview */}
            <div className="col-span-3 p-4 space-y-3">
              <p className="text-[11px] font-medium uppercase tracking-widest text-text-muted">
                Open Incidents
              </p>
              {[
                { title: "API 500 after token expiry", severity: "high" },
                { title: "Upload endpoint timeout", severity: "medium" },
                { title: "Missing rate-limit header", severity: "low" },
              ].map((item) => (
                <div
                  key={item.title}
                  className="rounded-lg border border-border-subtle bg-surface p-3 space-y-1"
                >
                  <p className="text-sm font-medium text-text-primary leading-tight">
                    {item.title}
                  </p>
                  <span
                    className={`inline-block rounded-md px-2 py-0.5 text-[11px] font-medium ${
                      item.severity === "high"
                        ? "bg-status-danger/15 text-status-danger"
                        : item.severity === "medium"
                          ? "bg-status-warning/15 text-status-warning"
                          : "bg-status-success/15 text-status-success"
                    }`}
                  >
                    {item.severity}
                  </span>
                </div>
              ))}
            </div>
            {/* Center: Analysis timeline preview */}
            <div className="col-span-6 p-5 space-y-4">
              <p className="text-[11px] font-medium uppercase tracking-widest text-text-muted">
                AI Analysis Timeline
              </p>
              {[
                { step: "Reading incident context", status: "done" },
                { step: "Retrieving related files", status: "done" },
                { step: "Analyzing stack trace", status: "done" },
                { step: "Generating root-cause hypotheses", status: "active" },
                { step: "Building candidate patch", status: "pending" },
                { step: "Running validation", status: "pending" },
              ].map((s) => (
                <div key={s.step} className="flex items-center gap-3">
                  <div
                    className={`h-2.5 w-2.5 rounded-full shrink-0 ${
                      s.status === "done"
                        ? "bg-status-success"
                        : s.status === "active"
                          ? "bg-accent animate-pulse"
                          : "bg-border-strong"
                    }`}
                  />
                  <span
                    className={`text-sm ${
                      s.status === "pending"
                        ? "text-text-disabled"
                        : "text-text-primary"
                    }`}
                  >
                    {s.step}
                  </span>
                </div>
              ))}
            </div>
            {/* Right: Evidence & risk preview */}
            <div className="col-span-3 p-4 space-y-4">
              <div className="space-y-1">
                <p className="text-[11px] font-medium uppercase tracking-widest text-text-muted">
                  Confidence
                </p>
                <p className="text-2xl font-semibold text-status-success">
                  78%{" "}
                  <span className="text-sm font-normal text-text-muted">
                    High
                  </span>
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-[11px] font-medium uppercase tracking-widest text-text-muted">
                  Risk Level
                </p>
                <span className="inline-flex items-center gap-1.5 rounded-md bg-status-warning/15 px-2 py-0.5 text-[11px] font-medium text-status-warning">
                  <ShieldCheck className="h-3 w-3" aria-hidden="true" />
                  Medium risk
                </span>
              </div>
              <div className="space-y-1">
                <p className="text-[11px] font-medium uppercase tracking-widest text-text-muted">
                  Evidence
                </p>
                <p className="text-sm text-text-secondary">
                  3 files cited · 1 test · 2 log entries
                </p>
              </div>
              <div className="space-y-1.5 pt-2">
                <p className="text-[11px] font-medium uppercase tracking-widest text-text-muted">
                  Cited File
                </p>
                <div className="rounded-lg bg-surface-code border border-border-subtle p-2">
                  <code className="font-mono text-xs text-text-secondary">
                    auth/session.py:84–103
                  </code>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── How It Works ──────────────────────────────────── */}
      <section className="border-t border-border-subtle bg-surface py-24">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-3xl font-semibold tracking-tight">
            How DevSentinel works
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-text-muted">
            A deterministic AI pipeline with human review at every step.
          </p>
          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: GitBranch,
                title: "Connect repository",
                desc: "Import a public GitHub repository or upload a ZIP. DevSentinel indexes source files, docs, tests, and symbols.",
              },
              {
                icon: Bug,
                title: "Submit incident",
                desc: "Paste a stack trace, error logs, and describe the expected vs. actual behavior with severity and environment.",
              },
              {
                icon: Search,
                title: "Evidence retrieval",
                desc: "Hybrid vector + keyword search retrieves the most relevant code chunks, documentation, and test files.",
              },
              {
                icon: Brain,
                title: "Root-cause analysis",
                desc: "The AI explains the likely root cause with file citations, confidence scores, and risk assessment.",
              },
              {
                icon: FileCode2,
                title: "Patch generation",
                desc: "A candidate unified diff is generated only for files supported by evidence. Every change includes rationale.",
              },
              {
                icon: FlaskConical,
                title: "Sandbox validation",
                desc: "The patch is applied in an isolated sandbox and existing tests are run. Results are shown before any human action.",
              },
            ].map(({ icon: Icon, title, desc }) => (
              <div
                key={title}
                className="rounded-xl border border-border-subtle bg-surface-raised p-6 space-y-3"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent-muted">
                  <Icon className="h-5 w-5 text-accent" aria-hidden="true" />
                </div>
                <h3 className="text-base font-semibold">{title}</h3>
                <p className="text-sm leading-relaxed text-text-muted">
                  {desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Trust & Security ──────────────────────────────── */}
      <section className="border-t border-border-subtle py-24">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-3xl font-semibold tracking-tight">
            Built for engineering trust
          </h2>
          <p className="mx-auto mt-3 max-w-lg text-center text-text-muted">
            Every AI recommendation is inspectable, bounded, and reversible.
          </p>
          <div className="mt-14 grid grid-cols-1 gap-6 sm:grid-cols-3">
            {[
              {
                icon: Lock,
                title: "Evidence-grounded",
                desc: "Every claim cites source files, line numbers, logs, or test output. No hallucinated explanations.",
              },
              {
                icon: ShieldCheck,
                title: "Human in control",
                desc: "AI suggests patches — you approve them. Safety gates block irreversible actions until explicit confirmation.",
              },
              {
                icon: Zap,
                title: "Auditable pipeline",
                desc: "Full trace of every AI step, model version, retrieval strategy, and token usage. Inspect everything.",
              },
            ].map(({ icon: Icon, title, desc }) => (
              <div
                key={title}
                className="rounded-xl border border-border-subtle bg-surface p-6 text-center space-y-3"
              >
                <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-lg border border-border-subtle bg-surface-raised">
                  <Icon
                    className="h-5 w-5 text-text-secondary"
                    aria-hidden="true"
                  />
                </div>
                <h3 className="text-base font-semibold">{title}</h3>
                <p className="text-sm leading-relaxed text-text-muted">
                  {desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Final CTA ─────────────────────────────────────── */}
      <section className="border-t border-border-subtle bg-surface py-24 text-center">
        <div className="mx-auto max-w-xl space-y-6 px-6">
          <h2 className="text-3xl font-semibold tracking-tight">
            Start investigating incidents
          </h2>
          <p className="text-text-muted">
            Connect your first repository and run an AI-powered analysis in
            under two minutes.
          </p>
          <Link
            href="/register"
            className="inline-flex items-center gap-2 rounded-lg bg-accent px-6 py-3 text-sm font-medium text-white hover:bg-accent/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          >
            Analyze an incident
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────── */}
      <footer className="border-t border-border-subtle py-8">
        <div className="mx-auto max-w-6xl px-6 flex items-center justify-between text-xs text-text-muted">
          <span>© 2026 DevSentinel AI</span>
          <div className="flex items-center gap-4">
            <Link href="/app" className="hover:text-text-primary transition-colors">
              Dashboard
            </Link>
            <Link href="#" className="hover:text-text-primary transition-colors">
              Documentation
            </Link>
            <Link href="#" className="hover:text-text-primary transition-colors">
              GitHub
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
