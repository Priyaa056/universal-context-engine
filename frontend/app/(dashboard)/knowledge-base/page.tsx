"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import {
  AlertCircle,
  CheckCircle2,
  Clock3,
  FileText,
  Loader2,
  Sparkles,
  Upload,
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
import { fetchDocuments, uploadDocument } from "@/lib/api";
import type { DocumentSummary } from "@/types/document";

const ACCEPTED_TYPES = ".pdf,.txt";
const ACCEPTED_EXTENSIONS = [".pdf", ".txt"];

function isAcceptedFile(file: File): boolean {
  const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
  return ACCEPTED_EXTENSIONS.includes(extension);
}

export default function KnowledgeBasePage() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);

  const loadDocuments = useCallback(async () => {
    try {
      const response = await fetchDocuments();
      setDocuments(response.documents);
    } catch {
      setErrorMessage("Failed to load documents. Is the backend running?");
    } finally {
      setIsFetching(false);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const resetMessages = () => setErrorMessage(null);

  const handleFileSelection = (file: File | null) => {
    resetMessages();

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

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelection(event.target.files?.[0] ?? null);
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    resetMessages();

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

  return (
    <DashboardLayout
      title="Knowledge Hub"
      description="Upload and manage documents for richer context and retrieval."
    >
      <PageHeader
        title="Knowledge Hub"
        description="Bring your documents into the platform and turn them into a premium knowledge layer for Alex."
      />

      {errorMessage && (
        <div className="mb-5 flex items-center gap-2 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
        <Card className="overflow-hidden">
          <CardHeader className="border-b border-slate-100 bg-gradient-to-r from-violet-50 via-white to-sky-50">
            <CardTitle className="text-lg text-slate-950">Upload Documents</CardTitle>
            <CardDescription>
              Drag and drop files, or browse your workspace. Supported formats are PDF and TXT.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-5">
            <input
              ref={fileInputRef}
              type="file"
              accept={ACCEPTED_TYPES}
              className="hidden"
              aria-hidden
              onChange={handleFileChange}
            />

            <motion.div
              whileHover={{ y: -3, scale: 1.01 }}
              onDragOver={(event) => {
                event.preventDefault();
                setIsDragActive(true);
              }}
              onDragLeave={() => setIsDragActive(false)}
              onDrop={(event) => {
                event.preventDefault();
                setIsDragActive(false);
                handleFileSelection(event.dataTransfer.files?.[0] ?? null);
              }}
              onClick={handleUploadClick}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  handleUploadClick();
                }
              }}
              role="button"
              tabIndex={0}
              aria-label="Upload documents"
              className={`flex min-h-[260px] flex-col items-center justify-center rounded-[28px] border border-dashed px-6 py-10 text-center transition-all ${isDragActive ? "border-violet-400 bg-violet-50/70" : "border-slate-200 bg-slate-50/80"}`}
            >
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-to-br from-violet-600 to-sky-500 text-white shadow-[0_20px_45px_-20px_rgba(124,58,237,0.7)]">
                <Upload className="h-7 w-7" />
              </div>
              <p className="text-lg font-semibold text-slate-950">Drop files here or browse</p>
              <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                {selectedFile
                  ? `Selected: ${selectedFile.name}`
                  : "PDF or TXT files only. Once uploaded, Alex will prepare them for retrieval."}
              </p>
              <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
                <Button
                  onClick={(event) => {
                    event.stopPropagation();
                    if (selectedFile) {
                      handleUpload();
                    } else {
                      handleUploadClick();
                    }
                  }}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      {selectedFile ? "Upload File" : "Browse Files"}
                    </>
                  )}
                </Button>
                <div className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-500">
                  {selectedFile ? "Ready for upload" : "No file selected"}
                </div>
              </div>
            </motion.div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-slate-950">Recent Uploads</CardTitle>
            <CardDescription>Latest documents available for context retrieval.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {isFetching ? (
              <div className="flex items-center gap-2 py-2 text-sm text-slate-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading documents...
              </div>
            ) : documents.length === 0 ? (
              <div className="rounded-[20px] border border-dashed border-slate-200 bg-slate-50/80 p-5 text-center text-sm text-slate-500">
                No documents uploaded yet.
              </div>
            ) : (
              documents.slice(0, 4).map((document) => (
                <div key={document.id || document.filename} className="rounded-[20px] border border-slate-100 bg-slate-50/80 p-3">
                  <div className="flex items-start gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white text-violet-700 shadow-sm">
                      <FileText className="h-4 w-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold text-slate-900">{document.filename}</p>
                      <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                        <span className="inline-flex items-center gap-1 rounded-full bg-white px-2 py-1">
                          <Clock3 className="h-3 w-3" />
                          {document.uploaded_at}
                        </span>
                        <span>{document.chunks_created} chunks</span>
                      </div>
                    </div>
                    <div className="mt-1">
                      {document.status === "Processed" ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                      ) : (
                        <Loader2 className="h-4 w-4 animate-spin text-amber-600" />
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-lg text-slate-950">Uploaded Documents</CardTitle>
          <CardDescription>Documents stored in the knowledge base with chunk counts.</CardDescription>
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
              <p className="text-sm font-medium text-slate-900">No documents uploaded yet.</p>
              <p className="mt-1 max-w-sm text-sm text-slate-500">
                Upload a PDF or TXT file to add it to your knowledge base.
              </p>
            </div>
          ) : (
            <ul className="grid gap-4 md:grid-cols-2">
              {documents.map((document) => (
                <li key={document.id || document.filename} className="rounded-[24px] border border-slate-100 bg-slate-50/80 p-4">
                  <div className="flex h-full flex-col justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-white text-violet-700 shadow-sm">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold text-slate-900">{document.filename}</p>
                        <p className="mt-1 text-xs text-slate-500">Uploaded: {document.uploaded_at}</p>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <Badge variant="secondary" className="uppercase">
                        {document.file_type}
                      </Badge>
                      <Badge variant="outline">{document.file_size_readable}</Badge>
                      <Badge variant="outline">
                        {document.chunks_created} {document.chunks_created === 1 ? "Chunk" : "Chunks"}
                      </Badge>
                      <Badge className={document.status === "Processed" ? "bg-emerald-500/10 text-emerald-700" : "bg-amber-500/10 text-amber-700"}>
                        {document.status}
                      </Badge>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}
