"use client";

import {
  Download,
  Eye,
  FileText,
  Pencil,
  Trash2,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

import type { DocumentSummary } from "@/types/document";

interface Props {
  document: DocumentSummary;

  onView: () => void;
  onDownload: () => void;
  onRename: () => void;
  onDelete: () => void;
}

export default function DocumentCard({
  document,
  onView,
  onDownload,
  onRename,
  onDelete,
}: Props) {
  return (
    <div className="group rounded-3xl border bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">

      <div className="flex items-start gap-4">

        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-100">

          <FileText className="h-7 w-7 text-violet-600"/>

        </div>

        <div className="min-w-0 flex-1">

          <h3 className="truncate text-lg font-semibold">

            {document.filename}

          </h3>

          <p className="mt-1 text-sm text-slate-500">

            Uploaded {document.uploaded_at}

          </p>

        </div>

      </div>

      <div className="mt-5 flex flex-wrap gap-2">

        <Badge>{document.file_type.toUpperCase()}</Badge>

        <Badge variant="outline">

          {document.file_size_readable}

        </Badge>

        <Badge variant="outline">

          {document.chunks_created} Chunks

        </Badge>

      </div>

      <div className="mt-6 flex justify-between">

        <Button
          size="icon"
          variant="outline"
          onClick={onView}
        >
          <Eye className="h-4 w-4"/>
        </Button>

        <Button
          size="icon"
          variant="outline"
          onClick={onDownload}
        >
          <Download className="h-4 w-4"/>
        </Button>

        <Button
          size="icon"
          variant="outline"
          onClick={onRename}
        >
          <Pencil className="h-4 w-4"/>
        </Button>

        <Button
          size="icon"
          variant="destructive"
          onClick={onDelete}
        >
          <Trash2 className="h-4 w-4"/>
        </Button>

      </div>

    </div>
  );
}