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
    <div className="flex min-h-screen bg-background">
      <div className="hidden md:fixed md:inset-y-0 md:flex md:w-64">
        <Sidebar />
      </div>

      <div className="flex min-h-screen flex-1 flex-col md:pl-64">
        <Navbar title={title} description={description} />
        <main className="flex-1 p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
