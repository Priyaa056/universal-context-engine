"use client";

import {
  FileText,
  Brain,
  Database,
  CheckCircle2,
} from "lucide-react";

interface StatsCardsProps {
  documentCount: number;
  chunkCount: number;
  storageSize: number;
}

export default function StatsCards({
  documentCount,
  chunkCount,
  storageSize,
}: StatsCardsProps) {
  const stats = [
    {
      title: "Documents",
      value: documentCount,
      icon: FileText,
      color: "from-violet-500 to-fuchsia-500",
    },
    {
      title: "Chunks",
      value: chunkCount,
      icon: Brain,
      color: "from-sky-500 to-cyan-500",
    },
    {
      title: "Storage",
      value: `${(storageSize / 1024).toFixed(1)} KB`,
      icon: Database,
      color: "from-emerald-500 to-lime-500",
    },
    {
      title: "Indexed",
      value: "100%",
      icon: CheckCircle2,
      color: "from-amber-500 to-orange-500",
    },
  ];

  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => {
        const Icon = stat.icon;

        return (
          <div
            key={stat.title}
            className="rounded-3xl border bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
          >
            <div
              className={`flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${stat.color} text-white`}
            >
              <Icon className="h-6 w-6" />
            </div>

            <p className="mt-5 text-sm text-slate-500">
              {stat.title}
            </p>

            <h2 className="mt-1 text-3xl font-bold text-slate-900">
              {stat.value}
            </h2>
          </div>
        );
      })}
    </div>
  );
}