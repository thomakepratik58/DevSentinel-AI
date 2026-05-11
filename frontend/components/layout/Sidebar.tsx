"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  GitBranch,
  AlertTriangle,
  Activity,
  GitPullRequest,
  BarChart3,
  Settings,
  ListChecks,
  ChevronLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";

type NavItem = {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
};

const primaryNav: NavItem[] = [
  { href: "/app", label: "Overview", icon: LayoutDashboard },
  { href: "/app/repositories", label: "Repositories", icon: GitBranch },
  { href: "/app/incidents", label: "Incidents", icon: AlertTriangle },
  { href: "/app/runs", label: "Analysis Runs", icon: Activity },
  { href: "/app/patches", label: "Patches", icon: GitPullRequest },
  { href: "/app/observability", label: "Observability", icon: BarChart3 },
];

const secondaryNav: NavItem[] = [
  { href: "/app/settings", label: "Settings", icon: Settings },
  { href: "/app/audit", label: "Audit Logs", icon: ListChecks },
];

function NavLink({ item, pathname }: { item: NavItem; pathname: string }) {
  const isActive =
    item.href === "/app"
      ? pathname === "/app"
      : pathname.startsWith(item.href);
  const Icon = item.icon;

  return (
    <Link
      href={item.href}
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
          isActive ? "text-accent" : "text-text-muted group-hover:text-text-secondary"
        )}
        aria-hidden="true"
      />
      {item.label}
    </Link>
  );
}

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-[248px] flex-col border-r border-border-subtle bg-surface">
      {/* Product mark + workspace */}
      <div className="flex h-14 items-center gap-2 border-b border-border-subtle px-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent text-xs font-bold text-white">
          D
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-semibold text-text-primary leading-tight">
            DevSentinel
          </span>
          <span className="text-[11px] text-text-muted leading-tight">
            Acme Engineering
          </span>
        </div>
      </div>

      {/* Primary navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4" aria-label="Main navigation">
        {primaryNav.map((item) => (
          <NavLink key={item.href} item={item} pathname={pathname} />
        ))}
      </nav>

      {/* Secondary navigation */}
      <nav
        className="space-y-1 border-t border-border-subtle px-3 py-3"
        aria-label="Secondary navigation"
      >
        {secondaryNav.map((item) => (
          <NavLink key={item.href} item={item} pathname={pathname} />
        ))}
      </nav>

      {/* Usage footer */}
      <div className="border-t border-border-subtle px-4 py-3">
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-[11px] text-text-muted">
            <span>AI usage this month</span>
            <span className="font-medium tabular-nums">68%</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-raised">
            <div
              className="h-full rounded-full bg-accent transition-all"
              style={{ width: "68%" }}
            />
          </div>
        </div>
      </div>
    </aside>
  );
}
