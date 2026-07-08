"use client";
import { motion } from "framer-motion";
import { ArrowUpRight, CheckCircle2, Mail, PlugZap, Sparkles, Workflow } from "lucide-react";

import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const integrations = [
  {
    name: "Email",
    description: "Send polished summaries, follow-ups, and reports from Alex.",
    status: "Connected",
    icon: Mail,
    accent: "from-violet-500 to-fuchsia-500",
  },
  {
    name: "Task Manager",
    description: "Create and track structured actions from your workspace context.",
    status: "Connected",
    icon: Workflow,
    accent: "from-sky-500 to-cyan-500",
  },
  {
    name: "GitHub",
    description: "Connect repo-aware workflow actions and pull request insights.",
    status: "Coming Soon",
    icon: Sparkles,
    accent: "from-emerald-500 to-lime-500",
  },
  {
    name: "Slack",
    description: "Surface updates and enable collaboration across your team.",
    status: "Coming Soon",
    icon: PlugZap,
    accent: "from-amber-500 to-orange-500",
  },
];

export default function ToolsPage() {
  return (
    <DashboardLayout title="Connected Apps" description="A beautiful integration marketplace for your AI operating system.">
      <PageHeader
        title="Connected Apps"
        description="Connect your tools, keep everything in sync, and let Alex orchestrate actions across the platform."
      />

      <div className="grid gap-5 md:grid-cols-2">
        {integrations.map((integration, index) => {
          const Icon = integration.icon;
          return (
            <motion.div key={integration.name} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.06 }} whileHover={{ y: -4, scale: 1.01 }}>
              <Card className="h-full overflow-hidden">
                <CardHeader className="border-b border-slate-100">
                  <div className="flex items-start justify-between gap-4">
                    <div className={`flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br ${integration.accent} text-white`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <Badge className={integration.status === "Connected" ? "bg-emerald-500/10 text-emerald-700" : "bg-amber-500/10 text-amber-700"}>
                      {integration.status}
                    </Badge>
                  </div>
                  <CardTitle className="mt-4 text-lg text-slate-950">{integration.name}</CardTitle>
                  <CardDescription>{integration.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex items-center justify-between p-5">
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                    {integration.status === "Connected" ? "Ready to use" : "Planned for launch"}
                  </div>
                  <button className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700">
                    Open
                    <ArrowUpRight className="h-4 w-4" />
                  </button>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </DashboardLayout>
  );
}
