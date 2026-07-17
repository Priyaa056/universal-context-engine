import type {
  DocumentsListResponse,
  UploadSuccessResponse,
} from "@/types/document";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function uploadDocument(
  file: File
): Promise<UploadSuccessResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/documents/upload`,{
    method: "POST",
    body: formData,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      typeof data?.message === "string"
        ? data.message
        : typeof data?.detail === "string"
          ? data.detail
          : typeof data?.detail?.message === "string"
            ? data.detail.message
            : "Failed to upload document. Please try again.";
    const details =
      typeof data?.details === "string"
        ? data.details
        : typeof data?.detail?.details === "string"
          ? data.detail.details
          : null;
    throw new Error(details ? `${message} (${details})` : message);
  }

  return data as UploadSuccessResponse;
}

export async function fetchDocuments(): Promise<DocumentsListResponse> {
  const response = await fetch(`${API_BASE_URL}/api/documents`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to load documents.");
  }

  return response.json() as Promise<DocumentsListResponse>;
}
