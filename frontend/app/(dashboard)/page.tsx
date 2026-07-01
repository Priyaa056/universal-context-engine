"use client";

import { useEffect, useMemo, useState } from "react";
import { Activity, BookOpen, CheckCircle2, Loader2, Wrench } from "lucide-react";

import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { PageHeader } from "@/components/ui/page-header";
import { StatCard } from "@/components/ui/stat-card";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { dashboardStats } from "@/lib/constants";
import { fetchDocuments } from "@/lib/api";
import { buildUploadActivities } from "@/lib/document-utils";
import type { DocumentSummary } from "@/types/document";

export default function DashboardPage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [isLoadingActivities, setIsLoadingActivities] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchDocuments()
      .then((response) => {
        if (mounted) {
          setDocuments(response.documents);
        }
      })
      .finally(() => {
        if (mounted) {
          setIsLoadingActivities(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  const recentActivities = useMemo(
    () => buildUploadActivities(documents),
    [documents]
  );

  return (
    <DashboardLayout
      title="Dashboard"
      description="Overview of your Universal Context Engine workspace."
    >
      <PageHeader
        title="Welcome back"
        description="Monitor your knowledge bases, connected tools, and system activity."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatCard
          title="Knowledge Bases"
          value={dashboardStats.knowledgeBases}
          icon={BookOpen}
          description="Active knowledge collections"
        />
        <StatCard
          title="Connected Tools"
          value={dashboardStats.connectedTools}
          icon={Wrench}
          description="MCP-ready integrations"
        />
        <StatCard
          title="System Status"
          value={dashboardStats.systemStatus}
          icon={CheckCircle2}
          description="All services operational"
        />
      </div>

      <Card className="mt-6 shadow-sm">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-base">Recent Activity</CardTitle>
          </div>
          <CardDescription>
            Latest updates across your workspace.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingActivities ? (
            <div className="flex items-center gap-2 py-4 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading recent activity...
            </div>
          ) : recentActivities.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No recent activity yet. Upload a document to see updates here.
            </p>
          ) : (
            <div className="space-y-4">
              {recentActivities.map((activity) => (
                <div
                  key={activity.id}
                  className="flex flex-col gap-1 border-b border-border pb-4 last:border-0 last:pb-0 sm:flex-row sm:items-start sm:justify-between"
                >
                  <div>
                    <p className="text-sm font-medium">{activity.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {activity.description}
                    </p>
                  </div>
                  <p className="shrink-0 text-xs text-muted-foreground">
                    {activity.timestamp}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}
