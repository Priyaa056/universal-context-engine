import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { ToolStatus } from "@/types/tool";

interface ToolCardProps {
  name: string;
  description: string;
  status: ToolStatus;
  className?: string;
}

function getStatusClasses(status: ToolStatus): string {
  return status === "Connected"
    ? "bg-emerald-500/10 text-emerald-700"
    : "bg-amber-500/10 text-amber-700";
}

export function ToolCard({
  name,
  description,
  status,
  className,
}: ToolCardProps) {
  return (
    <Card className={cn("transition-all hover:-translate-y-1", className)}>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div>
            <CardTitle className="text-base text-slate-950">{name}</CardTitle>
            <CardDescription className="mt-1">{description}</CardDescription>
          </div>
          <Badge className={cn("rounded-full border-0 px-3 py-1 text-xs", getStatusClasses(status))}>
            {status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-slate-500">
          Tool integration is ready to support rich actions and AI-assisted workflows.
        </p>
      </CardContent>
    </Card>
  );
}
