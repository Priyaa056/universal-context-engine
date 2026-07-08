"use client";

import { Button } from "@/components/ui/button";

interface DeleteDialogProps {
  open: boolean;
  filename: string;
  onCancel: () => void;
  onDelete: () => void;
}

export default function DeleteDialog({
  open,
  filename,
  onCancel,
  onDelete,
}: DeleteDialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">

      <div className="w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl">

        <h2 className="text-2xl font-bold">
          Delete Document
        </h2>

        <p className="mt-4 text-slate-600">
          Are you sure you want to permanently delete
        </p>

        <p className="mt-2 font-semibold text-violet-700">
          {filename}
        </p>

        <div className="mt-8 flex justify-end gap-3">

          <Button
            variant="outline"
            onClick={onCancel}
          >
            Cancel
          </Button>

          <Button
            variant="destructive"
            onClick={onDelete}
          >
            Delete
          </Button>

        </div>

      </div>

    </div>
  );
}