"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AlertCircle, FileText, Loader2, Upload } from "lucide-react";
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

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    resetMessages();
    const file = event.target.files?.[0] ?? null;

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (!isAcceptedFile(file)) {
      setSelectedFile(null);
      setErrorMessage("Unsupported file type. Only PDF and TXT files are allowed.");
      toast.error("Unsupported file type. Please upload PDF or TXT.");
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
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
      title="Knowledge Base"
      description="Upload and manage documents for context building."
    >
      <PageHeader
        title="Document Management"
        description="Upload PDF or TXT documents. Text is extracted and split into chunks for future retrieval."
      />

      {errorMessage && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">Upload Documents</CardTitle>
          <CardDescription>
            Supported formats: PDF and TXT. Documents are processed into text
            chunks on the backend.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <input
            ref={fileInputRef}
            type="file"
            accept={ACCEPTED_TYPES}
            className="hidden"
            aria-hidden
            onChange={handleFileChange}
          />

          <div
            className="flex min-h-[220px] flex-col items-center justify-center rounded-lg border border-dashed border-border bg-muted/30 px-6 py-10 text-center"
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
          >
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-muted">
              <Upload className="h-5 w-5 text-muted-foreground" />
            </div>
            <p className="text-sm font-medium">
              Click to browse and upload
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              {selectedFile
                ? `Selected: ${selectedFile.name}`
                : "PDF or TXT files only"}
            </p>
            <Button
              className="mt-4"
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
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  {selectedFile ? "Upload File" : "Browse Files"}
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="mt-6 shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">Uploaded Documents</CardTitle>
          <CardDescription>
            Documents stored in the knowledge base with chunk counts.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isFetching ? (
            <div className="flex items-center justify-center gap-2 py-12 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading documents...
            </div>
          ) : documents.length === 0 ? (
            <div className="flex flex-col items-center justify-center px-6 py-12 text-center">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-muted">
                <FileText className="h-5 w-5 text-muted-foreground" />
              </div>
              <p className="text-sm font-medium">No documents uploaded yet.</p>
              <p className="mt-1 max-w-sm text-sm text-muted-foreground">
                Upload a PDF or TXT file to add it to your knowledge base.
              </p>
            </div>
          ) : (
            <ul className="grid gap-4 md:grid-cols-2">
              {documents.map((document) => (
                <li
                  key={document.id || document.filename}
                  className="rounded-lg border border-border bg-card p-4 shadow-sm"
                >
                  <div className="flex h-full flex-col justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold">
                          {document.filename}
                        </p>
                        <p className="mt-1 text-xs text-muted-foreground">
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
                      <Badge
                        variant={document.status === "Processed" ? "default" : "destructive"}
                      >
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
