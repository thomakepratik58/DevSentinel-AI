"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import {
  LayoutDashboard,
  GitBranch,
  AlertTriangle,
  Activity,
  GitPullRequest,
  BarChart3,
  Settings,
  ListChecks,
  LogOut,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { logoutUser } from "@/features/auth/api"
import { useQueryClient } from "@tanstack/react-query"
import { CURRENT_USER_QUERY_KEY } from "@/features/auth/hooks/useCurrentUser"
import type { AuthUser } from "@/features/auth/types"

type NavItem = {
  href: string
  label: string
  icon: React.ElementType
}

const primaryNav: NavItem[] = [
  { href: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/app/repositories", label: "Repositories", icon: GitBranch },
  { href: "/app/incidents", label: "Incidents", icon: AlertTriangle },
  { href: "/app/runs", label: "Analysis Runs", icon: Activity },
  { href: "/app/patches", label: "Patches", icon: GitPullRequest },
  { href: "/app/observability", label: "Observability", icon: BarChart3 },
]

const secondaryNav: NavItem[] = [
  { href: "/app/settings", label: "Settings", icon: Settings },
  { href: "/app/audit", label: "Audit Logs", icon: ListChecks },
]

function NavLink({ item, pathname }: { item: NavItem; pathname: string }) {
  const isActive =
    item.href === "/app/dashboard"
      ? pathname === "/app/dashboard"
      : pathname.startsWith(item.href)
  const Icon = item.icon

  return (
    <Link
      href={item.href}
      aria-current={isActive ? "page" : undefined}
      className={cn(
        "group flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors",
        isActive
          ? "bg-surface-raised text-text-primary font-medium border border-border-subtle"
          : "text-text-secondary hover:text-text-primary hover:bg-surface-raised border border-transparent"
      )}
    >
      <Icon
        className={cn(
          "h-4 w-4 shrink-0",
          isActive
            ? "text-accent"
            : "text-text-muted group-hover:text-text-secondary"
        )}
        aria-hidden="true"
      />
      {item.label}
    </Link>
  )
}

interface SidebarProps {
  user: AuthUser
}

export function Sidebar({ user }: SidebarProps) {
  const pathname = usePathname()
  const router = useRouter()
  const queryClient = useQueryClient()

  const handleLogout = async () => {
    try {
      await logoutUser()
    } finally {
      queryClient.removeQueries({ queryKey: CURRENT_USER_QUERY_KEY })
      router.push("/login")
    }
  }

  // Derive initials for avatar
  const initials = user.display_name
    .split(" ")
    .slice(0, 2)
    .map((n) => n[0]?.toUpperCase() ?? "")
    .join("")

  return (
    <aside
      className="fixed left-0 top-0 flex h-full w-[240px] flex-col border-r border-border-subtle bg-surface z-30"
      aria-label="Main navigation"
    >
      {/* Product mark + workspace */}
      <div className="flex h-14 items-center gap-2.5 border-b border-border-subtle px-4">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-accent text-xs font-bold text-white">
          D
        </div>
        <div className="flex flex-col min-w-0">
          <span className="text-sm font-semibold text-text-primary leading-tight truncate">
            DevSentinel AI
          </span>
          <span className="text-[11px] text-text-muted leading-tight truncate">
            {user.display_name}&apos;s Workspace
          </span>
        </div>
      </div>

      {/* Primary navigation */}
      <nav className="flex-1 space-y-0.5 px-3 py-4" aria-label="Primary navigation">
        {primaryNav.map((item) => (
          <NavLink key={item.href} item={item} pathname={pathname} />
        ))}
      </nav>

      {/* Secondary navigation */}
      <nav
        className="space-y-0.5 border-t border-border-subtle px-3 py-3"
        aria-label="Secondary navigation"
      >
        {secondaryNav.map((item) => (
          <NavLink key={item.href} item={item} pathname={pathname} />
        ))}
      </nav>

      {/* User footer with logout */}
      <div className="border-t border-border-subtle px-3 py-3">
        <div className="flex items-center gap-2.5">
          <div
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/15 border border-accent/30 text-xs font-semibold text-accent"
            aria-hidden="true"
          >
            {initials}
          </div>
          <div className="flex min-w-0 flex-1 flex-col">
            <span className="truncate text-xs font-medium text-text-primary leading-tight">
              {user.display_name}
            </span>
            <span className="truncate text-[11px] text-text-muted leading-tight">
              {user.email}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="rounded-md p-1.5 text-text-muted hover:text-danger hover:bg-surface-raised transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            aria-label="Sign out"
            title="Sign out"
          >
            <LogOut className="h-3.5 w-3.5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </aside>
  )
}
