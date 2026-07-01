export type ToolStatus = "Connected" | "Disconnected";

export interface Tool {
  id: string;
  name: string;
  description: string;
  status: ToolStatus;
}
