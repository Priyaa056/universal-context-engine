"use client";

import type { DocumentSummary } from "@/types/document";
import DocumentCard from "./DocumentCard";

interface Props {
  documents: DocumentSummary[];

  onView: (doc: DocumentSummary) => void;
  onDownload: (doc: DocumentSummary) => void;
  onRename: (doc: DocumentSummary) => void;
  onDelete: (doc: DocumentSummary) => void;
}

export default function DocumentGrid({
  documents,
  onView,
  onDownload,
  onRename,
  onDelete,
}: Props) {

  if (!documents.length) {
    return (
      <div className="rounded-3xl border border-dashed p-16 text-center">

        <h2 className="text-xl font-semibold">
          No Documents Found
        </h2>

        <p className="mt-3 text-slate-500">
          Upload your first document to start building your AI knowledge base.
        </p>

      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">

      {documents.map((doc) => (

        <DocumentCard

          key={doc.id}

          document={doc}

          onView={() => onView(doc)}
          onDownload={() => onDownload(doc)}
          onRename={() => onRename(doc)}
          onDelete={() => onDelete(doc)}

        />

      ))}

    </div>
  );
}