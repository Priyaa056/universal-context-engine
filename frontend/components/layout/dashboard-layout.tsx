import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";

interface DashboardLayoutProps {
  children: React.ReactNode;
  title: string;
  description?: string;
}

export function DashboardLayout({
  children,
  title,
  description,
}: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(124,58,237,0.12),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(59,130,246,0.12),_transparent_28%),linear-gradient(135deg,_#f8fafc_0%,_#fdfdff_100%)]">
      <div className="mx-auto flex min-h-screen max-w-7xl gap-4 px-3 py-3 md:px-4 md:py-4">
        <div className="hidden md:flex md:w-72">
          <Sidebar />
        </div>

        <div className="flex min-h-screen flex-1 flex-col rounded-[32px] border border-slate-200/70 bg-white/70 p-2 shadow-[0_30px_90px_-45px_rgba(15,23,42,0.45)] backdrop-blur-xl md:rounded-[36px] md:p-3">
          <Navbar title={title} description={description} />
          <main className="flex-1 rounded-[24px] bg-slate-50/85 px-4 py-5 md:px-6 md:py-8">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
