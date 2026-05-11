"use client";

import { usePathname } from "next/navigation";
import { Search, Bell, User } from "lucide-react";

/**
 * Derive human-readable breadcrumb segments from the current pathname.
 */
function buildBreadcrumbs(pathname: string): string[] {
  if (pathname === "/app") return ["Overview"];

  const segments = pathname
    .replace(/^\/app\/?/, "")
    .split("/")
    .filter(Boolean)
    .map((s) =>
      s
        .replace(/-/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase())
    );

  return segments.length > 0 ? segments : ["Overview"];
}

export function TopBar() {
  const pathname = usePathname();
  const crumbs = buildBreadcrumbs(pathname);

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border-subtle bg-background px-5">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1.5 text-sm" aria-label="Breadcrumb">
        <span className="text-text-muted">DevSentinel</span>
        {crumbs.map((crumb, i) => (
          <span key={i} className="flex items-center gap-1.5">
            <span className="text-text-disabled">/</span>
            <span
              className={
                i === crumbs.length - 1
                  ? "font-medium text-text-primary"
                  : "text-text-muted"
              }
            >
              {crumb}
            </span>
          </span>
        ))}
      </nav>

      {/* Actions */}
      <div className="flex items-center gap-3">
        {/* Command search trigger */}
        <button
          className="flex items-center gap-2 rounded-lg border border-border-subtle bg-surface px-3 py-1.5 text-xs text-text-muted hover:bg-surface-raised transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          aria-label="Open search"
        >
          <Search className="h-3.5 w-3.5" aria-hidden="true" />
          <span className="hidden sm:inline">Search…</span>
          <kbd className="ml-1 rounded bg-surface-raised px-1.5 py-0.5 text-[10px] font-mono text-text-disabled border border-border-subtle">
            ⌘K
          </kbd>
        </button>

        {/* Notifications */}
        <button
          className="relative rounded-lg p-2 text-text-muted hover:text-text-primary hover:bg-surface-raised transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4" aria-hidden="true" />
        </button>

        {/* User avatar */}
        <button
          className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 border border-accent/30 text-xs font-medium text-accent hover:bg-accent/25 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          aria-label="User menu"
        >
          AD
        </button>
      </div>
    </header>
  );
}
