"use client";

import { X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Props {
  open: boolean;

  preview: string;

  filename: string;

  chunks: number;

  onClose: () => void;
}

export default function PreviewDrawer({
  open,
  preview,
  filename,
  chunks,
  onClose,
}: Props) {

  if (!open) return null;

  return (

    <div className="fixed inset-0 z-50 bg-black/40">

      <div className="absolute right-0 top-0 h-full w-[600px] overflow-auto bg-white shadow-2xl">

        <div className="flex items-center justify-between border-b p-6">

          <div>

            <h2 className="text-xl font-bold">

              {filename}

            </h2>

            <Badge className="mt-2">

              {chunks} Chunks

            </Badge>

          </div>

          <Button
            size="icon"
            variant="ghost"
            onClick={onClose}
          >

            <X className="h-5 w-5"/>

          </Button>

        </div>

        <div className="p-6">

          <pre className="whitespace-pre-wrap text-sm leading-7">

            {preview}

          </pre>

        </div>

      </div>

    </div>
    
);
}