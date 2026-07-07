"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BookOpen,
  Bot,
  CheckCircle2,
  DatabaseZap,
  FileText,
  FolderOpen,
  Sparkles,
  Wrench,
} from "lucide-react";

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
import { Button } from "@/components/ui/button";
import { fetchDocuments } from "@/lib/api";
import { buildUploadActivities } from "@/lib/document-utils";
import type { DocumentSummary } from "@/types/document";
import Link from "next/link";

const quickActions = [
  {
    title: "Ask Alex",
    description: "Start a conversation with your AI operating system.",
    href: "/chat",
    icon: Bot,
    accent: "from-violet-500 to-fuchsia-500",
  },
  {
    title: "Upload Documents",
    description: "Bring in new knowledge for retrieval and insight.",
    href: "/knowledge-base",
    icon: FileText,
    accent: "from-sky-500 to-cyan-500",
  },
  {
    title: "Search Knowledge",
    description: "Find context across your active document collections.",
    href: "/knowledge-base",
    icon: FolderOpen,
    accent: "from-emerald-500 to-lime-500",
  },
  {
    title: "Use Connected Apps",
    description: "Route actions through your integrations.",
    href: "/tools",
    icon: Wrench,
    accent: "from-amber-500 to-orange-500",
  },
];

export default function WorkspacePage() {
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
      title="Workspace"
      description="Everything you need, powered by Alex."
    >
      <PageHeader
        title="Workspace"
        description="Monitor knowledge, connected tools, and the health of your AI operating system."
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Knowledge Collections"
          value="3"
          icon={BookOpen}
          description="Active document hubs"
          accentClassName="bg-violet-50 text-violet-700"
          iconClassName="text-violet-700"
        />
        <StatCard
          title="Documents"
          value={documents.length}
          icon={FileText}
          description="Processed files ready for retrieval"
          accentClassName="bg-sky-50 text-sky-700"
          iconClassName="text-sky-700"
        />
        <StatCard
          title="Connected Apps"
          value="2"
          icon={Wrench}
          description="Ready for AI actions"
          accentClassName="bg-emerald-50 text-emerald-700"
          iconClassName="text-emerald-700"
        />
        <StatCard
          title="Total Chunks"
          value="16"
          icon={DatabaseZap}
          description="Indexed knowledge units"
          accentClassName="bg-amber-50 text-amber-700"
          iconClassName="text-amber-700"
        />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.6fr_0.9fr]">
        <Card className="overflow-hidden">
          <CardHeader className="border-b border-slate-100 bg-gradient-to-r from-violet-50 via-white to-sky-50">
            <div className="flex items-center justify-between gap-4">
              <div>
                <CardTitle className="text-lg text-slate-950">Recent Activity</CardTitle>
                <CardDescription>Live updates from the workspace.</CardDescription>
              </div>
              <div className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                Healthy
              </div>
            </div>
          </CardHeader>
          <CardContent className="px-0 py-0">
            {isLoadingActivities ? (
              <div className="flex items-center gap-2 px-6 py-5 text-sm text-slate-500">
                <Activity className="h-4 w-4 animate-pulse" />
                Loading activity feed...
              </div>
            ) : recentActivities.length === 0 ? (
              <p className="px-6 py-6 text-sm text-slate-500">
                No recent activity yet. Upload a document and Alex will start organizing it.
              </p>
            ) : (
              <div className="space-y-0">
                {recentActivities.map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-4 last:border-b-0"
                  >
                    <div>
                      <p className="text-sm font-semibold text-slate-800">{activity.title}</p>
                      <p className="mt-1 text-sm text-slate-500">{activity.description}</p>
                    </div>
                    <p className="text-xs text-slate-400">{activity.timestamp}</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-slate-950">System Status</CardTitle>
            <CardDescription>Healthy integrations and services.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {[
              { label: "API", status: "Healthy" },
              { label: "Vector Database", status: "Healthy" },
              { label: "AI Service", status: "Healthy" },
              { label: "Tool Integrations", status: "Healthy" },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/80 px-3 py-3">
                <span className="text-sm font-medium text-slate-700">{item.label}</span>
                <span className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  {item.status}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {quickActions.map((action) => {
          const Icon = action.icon;

          return (
            <Link key={action.title} href={action.href} className="group">
              <Card className="h-full transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_30px_80px_-40px_rgba(124,58,237,0.55)]">
                <CardContent className="flex h-full flex-col gap-4 p-5">
                  <div className={`flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br ${action.accent} text-white`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-slate-950">{action.title}</h3>
                    <p className="mt-1 text-sm text-slate-500">{action.description}</p>
                  </div>
                  <div className="mt-auto flex items-center justify-between text-sm font-medium text-violet-700">
                    Open
                    <Sparkles className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>
    </DashboardLayout>
  );
}
