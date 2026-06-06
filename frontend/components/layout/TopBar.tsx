"use client"

import { usePathname, useRouter } from "next/navigation"
import { Search, Bell, LogOut } from "lucide-react"
import { logoutUser } from "@/features/auth/api"
import { useQueryClient } from "@tanstack/react-query"
import { CURRENT_USER_QUERY_KEY } from "@/features/auth/hooks/useCurrentUser"
import type { AuthUser } from "@/features/auth/types"

/**
 * Derive human-readable breadcrumb segments from the current pathname.
 */
function buildBreadcrumbs(pathname: string): string[] {
  if (pathname === "/app/dashboard" || pathname === "/app") return ["Dashboard"]

  const segments = pathname
    .replace(/^\/app\/?/, "")
    .split("/")
    .filter(Boolean)
    .map((s) =>
      s
        .replace(/-/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase())
    )

  return segments.length > 0 ? segments : ["Dashboard"]
}

interface TopBarProps {
  user: AuthUser
}

export function TopBar({ user }: TopBarProps) {
  const pathname = usePathname()
  const router = useRouter()
  const queryClient = useQueryClient()
  const crumbs = buildBreadcrumbs(pathname)

  const initials = user.display_name
    .split(" ")
    .slice(0, 2)
    .map((n) => n[0]?.toUpperCase() ?? "")
    .join("")

  const handleLogout = async () => {
    try {
      await logoutUser()
    } finally {
      queryClient.removeQueries({ queryKey: CURRENT_USER_QUERY_KEY })
      router.push("/login")
    }
  }

  return (
    <header
      className="sticky top-0 z-20 flex h-14 shrink-0 items-center justify-between border-b border-border-subtle bg-background/95 backdrop-blur-sm px-5"
      style={{ paddingLeft: "calc(240px + 20px)" }}
    >
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1.5 text-sm" aria-label="Breadcrumb">
        <span className="text-text-muted">DevSentinel</span>
        {crumbs.map((crumb, i) => (
          <span key={i} className="flex items-center gap-1.5">
            <span className="text-text-disabled" aria-hidden="true">/</span>
            <span
              className={
                i === crumbs.length - 1
                  ? "font-medium text-text-primary"
                  : "text-text-muted"
              }
              aria-current={i === crumbs.length - 1 ? "page" : undefined}
            >
              {crumb}
            </span>
          </span>
        ))}
      </nav>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {/* Search trigger */}
        <button
          className="flex items-center gap-2 rounded-lg border border-border-subtle bg-surface px-3 py-1.5 text-xs text-text-muted hover:bg-surface-raised transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          aria-label="Search (Ctrl+K)"
          type="button"
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
          type="button"
        >
          <Bell className="h-4 w-4" aria-hidden="true" />
        </button>

        {/* User avatar + logout */}
        <div className="flex items-center gap-2 pl-1 border-l border-border-subtle ml-1">
          <div className="flex flex-col items-end">
            <span className="text-xs font-medium text-text-primary leading-tight hidden sm:block">
              {user.display_name}
            </span>
            <span className="text-[11px] text-text-muted leading-tight hidden sm:block">
              {user.email}
            </span>
          </div>
          <div
            className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 border border-accent/30 text-xs font-semibold text-accent"
            aria-hidden="true"
          >
            {initials}
          </div>
          <button
            onClick={handleLogout}
            className="rounded-md p-1.5 text-text-muted hover:text-status-danger hover:bg-surface-raised transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            aria-label="Sign out"
            title="Sign out"
            type="button"
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>
    </header>
  )
}
