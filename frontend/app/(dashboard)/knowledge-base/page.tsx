"use client";

import { DragEvent, useCallback, useEffect, useRef, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Download,
  Eye,
  FileText,
  Loader2,
  Pencil,
  Search,
  Sparkles,
  Trash2,
  Upload,
  X,
} from "lucide-react";
import { toast } from "sonner";

import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import UploadZone from "./components/UploadZone";
import { fetchDocuments, uploadDocument } from "@/lib/api";
import type { DocumentSummary } from "@/types/document";

const API_BASE = "http://127.0.0.1:8000";
const ACCEPTED_TYPES = ".pdf,.txt";
const ACCEPTED_EXTENSIONS = [".pdf", ".txt"];

type DocumentDetails = {
  document: DocumentSummary;
  chunks: unknown[];
  preview: string;
};

function isAcceptedFile(file: File): boolean {
  const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
  return ACCEPTED_EXTENSIONS.includes(extension);
}

export default function KnowledgeBasePage() {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [isDragActive, setIsDragActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [selectedDocument, setSelectedDocument] = useState<DocumentDetails | null>(null);
  const [renameDocument, setRenameDocument] = useState<DocumentSummary | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [deleteDocumentItem, setDeleteDocumentItem] = useState<DocumentSummary | null>(null);

  const loadDocuments = useCallback(async () => {
    setIsFetching(true);

    try {
      const url = searchQuery.trim()
        ? `${API_BASE}/api/documents/search?q=${encodeURIComponent(searchQuery)}`
        : null;

      if (url) {
        const response = await fetch(url);
        const data = await response.json();
        setDocuments(data.documents ?? []);
      } else {
        const response = await fetchDocuments();
        setDocuments(response.documents);
      }
    } catch {
      setErrorMessage("Failed to load documents. Is the backend running?");
    } finally {
      setIsFetching(false);
    }
  }, [searchQuery]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleFileSelection = (file: File | null) => {
    setErrorMessage(null);

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (!isAcceptedFile(file)) {
      setSelectedFile(null);
      setErrorMessage("Unsupported file type. Only PDF and TXT files are allowed.");
      toast.error("Unsupported file type. Please upload PDF or TXT.");
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    setErrorMessage(null);

    if (!selectedFile) {
      setErrorMessage("Please select a file before uploading.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await uploadDocument(selectedFile);
      toast.success(`${response.document.filename} processed successfully.`);
      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await loadDocuments();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Upload failed. Please try again.";
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleView = async (document: DocumentSummary) => {
    try {
      const response = await fetch(`${API_BASE}/api/documents/${document.id}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail?.message ?? "Failed to load document.");
      }

      setSelectedDocument(data);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to view document.");
    }
  };

  const handleDownload = (document: DocumentSummary) => {
    window.open(`${API_BASE}/api/documents/${document.id}/download`, "_blank");
  };

  const handleRename = async () => {
    if (!renameDocument || !renameValue.trim()) return;

    try {
      const response = await fetch(`${API_BASE}/api/documents/${renameDocument.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          filename: renameValue.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail?.message ?? "Rename failed.");
      }

      toast.success("Document renamed successfully.");
      setRenameDocument(null);
      setRenameValue("");
      await loadDocuments();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Rename failed.");
    }
  };

  const handleDelete = async () => {
    if (!deleteDocumentItem) return;

    try {
      const response = await fetch(`${API_BASE}/api/documents/${deleteDocumentItem.id}`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail?.message ?? "Delete failed.");
      }

      toast.success("Document deleted successfully.");
      setDeleteDocumentItem(null);
      await loadDocuments();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Delete failed.");
    }
  };

  return (
    <DashboardLayout
      title="Knowledge Hub"
      description="Upload and manage documents for richer context and retrieval."
    >
      <PageHeader
        title="Knowledge Hub"
        description="Upload, search, view, rename, download, and delete documents used by Alex."
      />

      {errorMessage && (
        <div className="mb-5 flex items-center gap-2 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
        <UploadZone
          selectedFile={selectedFile}
          loading={isLoading}
          dragActive={isDragActive}
          setDragActive={setIsDragActive}
          onFileSelect={handleFileSelection}
          onUpload={handleUpload}
        />
         
        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-slate-950">Knowledge Stats</CardTitle>
            <CardDescription>Live document intelligence summary.</CardDescription>
          </CardHeader>

          <CardContent className="grid gap-3">
            <div className="rounded-2xl border bg-slate-50 p-4">
              <p className="text-xs text-slate-500">Documents</p>
              <p className="text-2xl font-bold text-slate-950">{documents.length}</p>
            </div>

            <div className="rounded-2xl border bg-slate-50 p-4">
              <p className="text-xs text-slate-500">Total Chunks</p>
              <p className="text-2xl font-bold text-slate-950">
                {documents.reduce((total, doc) => total + doc.chunks_created, 0)}
              </p>
            </div>

            <div className="rounded-2xl border bg-slate-50 p-4">
              <p className="text-xs text-slate-500">Status</p>
              <p className="text-sm font-semibold text-emerald-600">Ready for retrieval</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle className="text-lg text-slate-950">Uploaded Documents</CardTitle>
              <CardDescription>
                Manage documents stored in the knowledge layer.
              </CardDescription>
            </div>

            <div className="relative w-full md:w-80">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search documents..."
                className="pl-9"
              />
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {isFetching ? (
            <div className="flex items-center justify-center gap-2 py-12 text-sm text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading documents...
            </div>
          ) : documents.length === 0 ? (
            <div className="flex flex-col items-center justify-center px-6 py-12 text-center">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-500">
                <FileText className="h-5 w-5" />
              </div>
              <p className="text-sm font-medium text-slate-900">No documents found.</p>
              <p className="mt-1 max-w-sm text-sm text-slate-500">
                Upload or search for another document.
              </p>
            </div>
          ) : (
            <ul className="grid gap-4 md:grid-cols-2">
              {documents.map((document) => (
                <li
                  key={document.id || document.filename}
                  className="rounded-[24px] border border-slate-100 bg-slate-50/80 p-4"
                >
                  <div className="flex h-full flex-col justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-white text-violet-700 shadow-sm">
                        <FileText className="h-5 w-5" />
                      </div>

                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold text-slate-900">
                          {document.filename}
                        </p>
                        <p className="mt-1 text-xs text-slate-500">
                          Uploaded: {document.uploaded_at}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <Badge variant="secondary" className="uppercase">
                        {document.file_type}
                      </Badge>
                      <Badge variant="outline">{document.file_size_readable}</Badge>
                      <Badge variant="outline">
                        {document.chunks_created}{" "}
                        {document.chunks_created === 1 ? "Chunk" : "Chunks"}
                      </Badge>
                      <Badge className="bg-emerald-500/10 text-emerald-700">
                        {document.status}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
                      <Button variant="outline" size="sm" onClick={() => handleView(document)}>
                        <Eye className="h-4 w-4" />
                        View
                      </Button>

                      <Button variant="outline" size="sm" onClick={() => handleDownload(document)}>
                        <Download className="h-4 w-4" />
                        Download
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setRenameDocument(document);
                          setRenameValue(document.filename);
                        }}
                      >
                        <Pencil className="h-4 w-4" />
                        Rename
                      </Button>

                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => setDeleteDocumentItem(document)}
                      >
                        <Trash2 className="h-4 w-4" />
                        Delete
                      </Button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      {selectedDocument && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="max-h-[85vh] w-full max-w-3xl overflow-auto rounded-3xl bg-white p-6 shadow-2xl">
            <div className="mb-4 flex items-start justify-between">
              <div>
                <h2 className="text-lg font-bold text-slate-950">
                  {selectedDocument.document.filename}
                </h2>
                <p className="text-sm text-slate-500">
                  {selectedDocument.document.file_size_readable} •{" "}
                  {selectedDocument.document.chunks_created} chunks
                </p>
              </div>

              <Button variant="ghost" size="sm" onClick={() => setSelectedDocument(null)}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="mb-4 flex flex-wrap gap-2">
              <Badge>{selectedDocument.document.file_type}</Badge>
              <Badge variant="outline">{selectedDocument.document.status}</Badge>
              <Badge variant="outline">{selectedDocument.chunks.length} chunks loaded</Badge>
            </div>

            <div className="rounded-2xl border bg-slate-50 p-4">
              <p className="mb-2 text-sm font-semibold text-slate-900">Preview</p>
              <pre className="whitespace-pre-wrap text-sm leading-6 text-slate-600">
                {selectedDocument.preview || "No preview available."}
              </pre>
            </div>
          </div>
        </div>
      )}

      {renameDocument && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-3xl bg-white p-6 shadow-2xl">
            <h2 className="text-lg font-bold text-slate-950">Rename Document</h2>
            <p className="mt-1 text-sm text-slate-500">
              Enter a new filename. Extension will be preserved.
            </p>

            <Input
              value={renameValue}
              onChange={(event) => setRenameValue(event.target.value)}
              className="mt-4"
            />

            <div className="mt-5 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setRenameDocument(null)}>
                Cancel
              </Button>
              <Button onClick={handleRename}>Rename</Button>
            </div>
          </div>
        </div>
      )}

      {deleteDocumentItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-3xl bg-white p-6 shadow-2xl">
            <h2 className="text-lg font-bold text-slate-950">Delete Document?</h2>
            <p className="mt-2 text-sm text-slate-500">
              This will permanently delete{" "}
              <span className="font-semibold text-slate-900">
                {deleteDocumentItem.filename}
              </span>{" "}
              from uploads, metadata, chunks, and vectors.
            </p>

            <div className="mt-5 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setDeleteDocumentItem(null)}>
                Cancel
              </Button>
              <Button variant="destructive" onClick={handleDelete}>
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}