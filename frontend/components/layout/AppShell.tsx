"use client"

import { Sidebar } from "./Sidebar"
import { TopBar } from "./TopBar"
import type { AuthUser } from "@/features/auth/types"

interface AppShellProps {
  user: AuthUser
  children: React.ReactNode
}

/**
 * App shell wrapper for all authenticated dashboard pages.
 * Provides the fixed sidebar navigation and sticky top bar.
 *
 * Layout (design.md §5.1):
 * ┌────────────────────────────────────────────────────────────┐
 * │ Sidebar (fixed) │ Top Bar (sticky) + Main Content          │
 * └────────────────────────────────────────────────────────────┘
 */
export function AppShell({ user, children }: AppShellProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar user={user} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar user={user} />
        <main
          id="main-content"
          className="flex-1 overflow-y-auto"
          aria-label="Main content"
        >
          <div className="mx-auto w-full max-w-[1400px] p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
