export interface DocumentSummary {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  file_size_readable: string;
  chunks_created: number;
  uploaded_at: string;
  status: "Uploading" | "Processing" | "Processed" | "Failed";
}

export interface UploadSuccessResponse {
  status: string;
  message: string;
  document: DocumentSummary;
}

export interface DocumentsListResponse {
  documents: DocumentSummary[];
}
