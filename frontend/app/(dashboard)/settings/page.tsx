"use client";

import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { PageHeader } from "@/components/ui/page-header";

export default function KnowledgeBasePage() {
  return (
    <DashboardLayout
      title="Knowledge Hub"
      description="Premium Knowledge Management"
    >
      <PageHeader
        title="Knowledge Hub"
        description="Manage all your AI knowledge."
      />
    </DashboardLayout>
  );
}