/**
 * Legacy app layout — this route is superseded by the (dashboard) group.
 * Redirects to the primary dashboard automatically.
 */

import { redirect } from "next/navigation"

export default function LegacyAppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  redirect("/app/dashboard")
}
