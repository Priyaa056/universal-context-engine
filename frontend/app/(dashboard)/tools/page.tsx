import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { PageHeader } from "@/components/ui/page-header";
import { ToolCard } from "@/components/ui/tool-card";
import { tools } from "@/lib/constants";

export default function ToolsPage() {
  return (
    <DashboardLayout
      title="Tools"
      description="Manage connected tools for action execution."
    >
      <PageHeader
        title="Connected Tools"
        description="View and manage MCP-ready tool integrations for your workspace."
      />

      <div className="grid gap-4 md:grid-cols-2">
        {tools.map((tool) => (
          <ToolCard
            key={tool.id}
            name={tool.name}
            description={tool.description}
            status={tool.status}
          />
        ))}
      </div>
    </DashboardLayout>
  );
}
