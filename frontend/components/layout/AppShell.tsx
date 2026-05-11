import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

/**
 * App shell wrapper for all authenticated dashboard pages.
 * Provides the sidebar navigation and top bar.
 *
 * Layout (design.md §5.1):
 * ┌───────────────────────────────────────────────────────────┐
 * │ Top Bar                                                     │
 * ├──────────────┬──────────────────────────────────────────────┤
 * │ Sidebar      │ Main Content (scrollable)                     │
 * └──────────────┴──────────────────────────────────────────────┘
 */
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-[1440px] p-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
