"use client"

import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { useCurrentUser } from "@/features/auth/hooks/useCurrentUser"
import { AppShell } from "@/components/layout/AppShell"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { data: user, isLoading, isError } = useCurrentUser()

  useEffect(() => {
    if (!isLoading && isError) {
      router.replace("/login")
    }
  }, [isLoading, isError, router])

  if (isLoading) {
    return (
      <div className="dashboard-loading" aria-label="Loading application…">
        <div className="dashboard-loading__spinner" aria-hidden="true" />
        <p>Loading DevSentinel…</p>
        <style>{`
          .dashboard-loading {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 16px;
            background: hsl(var(--background));
            color: hsl(var(--text-muted));
            font-size: 14px;
          }
          .dashboard-loading__spinner {
            width: 28px;
            height: 28px;
            border: 2px solid hsl(var(--border-subtle));
            border-top-color: hsl(var(--accent));
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
          }
          @keyframes spin { to { transform: rotate(360deg); } }
        `}</style>
      </div>
    )
  }

  if (!user) return null

  return <AppShell user={user}>{children}</AppShell>
}
