import type { ActivityItem } from "@/types/activity";
import type { Tool } from "@/types/tool";

export const dashboardStats = {
  knowledgeBases: 1,
  connectedTools: 2,
  systemStatus: "Healthy",
} as const;

export const recentActivities: ActivityItem[] = [
  {
    id: "1",
    title: "Knowledge base initialized",
    description: "Default knowledge base created for project context.",
    timestamp: "2 hours ago",
  },
  {
    id: "2",
    title: "Email tool connected",
    description: "Email Tool is ready to send project summaries and reports.",
    timestamp: "5 hours ago",
  },
  {
    id: "3",
    title: "Task tool connected",
    description: "Task Tool is ready to create and manage tasks.",
    timestamp: "1 day ago",
  },
  {
    id: "4",
    title: "System health check passed",
    description: "All services are running and responding normally.",
    timestamp: "1 day ago",
  },
];

export const tools: Tool[] = [
  {
    id: "email-tool",
    name: "Email Tool",
    description: "Send project summaries and reports.",
    status: "Connected",
  },
  {
    id: "task-tool",
    name: "Task Tool",
    description: "Create and manage tasks.",
    status: "Connected",
  },
];
