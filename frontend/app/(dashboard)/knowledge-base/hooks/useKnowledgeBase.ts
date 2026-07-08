"use client";

import { useMemo, useState } from "react";
import type { DocumentSummary } from "@/types/document";

export function useKnowledgeBase(initialDocuments: DocumentSummary[]) {

  const [documents, setDocuments] = useState(initialDocuments);

  const [search, setSearch] = useState("");

  const filteredDocuments = useMemo(() => {

    if (!search.trim()) return documents;

    return documents.filter((doc) =>
      doc.filename.toLowerCase().includes(search.toLowerCase())
    );

  }, [documents, search]);

  const stats = useMemo(() => {

    const chunks = documents.reduce(
      (sum, d) => sum + d.chunks_created,
      0
    );

    const storage = documents.reduce(
      (sum, d) => sum + d.file_size,
      0
    );

    return {
      documents: documents.length,
      chunks,
      storage,
    };

  }, [documents]);

  return {
    documents,
    setDocuments,

    filteredDocuments,

    search,
    setSearch,

    stats,
  };
}