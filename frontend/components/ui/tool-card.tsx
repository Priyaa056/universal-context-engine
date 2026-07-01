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

function getStatusVariant(status: ToolStatus): "default" | "secondary" {
  return status === "Connected" ? "default" : "secondary";
}

export function ToolCard({
  name,
  description,
  status,
  className,
}: ToolCardProps) {
  return (
    <Card className={cn("shadow-sm", className)}>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div>
            <CardTitle className="text-base">{name}</CardTitle>
            <CardDescription className="mt-1">{description}</CardDescription>
          </div>
          <Badge variant={getStatusVariant(status)}>{status}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          Tool integration ready for future MCP action execution.
        </p>
      </CardContent>
    </Card>
  );
}
