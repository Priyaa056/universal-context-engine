import type { DocumentSummary } from "@/types/document";

import type { ActivityItem } from "@/types/activity";
import { getRelativeTimeLabel } from "@/lib/date-utils";

export function buildUploadActivities(documents: DocumentSummary[]): ActivityItem[] {
  return [...documents]
    .sort((a, b) => new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime())
    .slice(0, 6)
    .map((document) => ({
      id: document.id,
      title: `Uploaded ${document.filename}`,
      description: `${document.chunks_created} ${document.chunks_created === 1 ? "chunk" : "chunks"} created`,
      timestamp: getRelativeTimeLabel(document.uploaded_at),
    }));
}
