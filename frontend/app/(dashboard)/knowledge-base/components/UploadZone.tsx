"use client";

import { useRef } from "react";
import { motion } from "framer-motion";
import {
  Upload,
  Sparkles,
  Loader2,
  FileText,
  CheckCircle2,
} from "lucide-react";

import { Button } from "@/components/ui/button";

interface UploadZoneProps {
  selectedFile: File | null;
  loading: boolean;
  dragActive: boolean;

  setDragActive: (value: boolean) => void;
  onFileSelect: (file: File | null) => void;
  onUpload: () => void;
}

const ACCEPTED_TYPES = ".pdf,.txt";

export default function UploadZone({
  selectedFile,
  loading,
  dragActive,
  setDragActive,
  onFileSelect,
  onUpload,
}: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <>
      <input
        ref={inputRef}
        hidden
        type="file"
        accept={ACCEPTED_TYPES}
        onChange={(e) => onFileSelect(e.target.files?.[0] ?? null)}
      />

      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ scale: 1.01 }}
        transition={{ duration: .25 }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragActive(false);

          if (e.dataTransfer.files.length > 0) {
            onFileSelect(e.dataTransfer.files[0]);
          }
        }}
        className={`relative overflow-hidden rounded-[32px] border-2 border-dashed transition-all duration-300

        ${
          dragActive
            ? "border-violet-500 bg-violet-50"
            : "border-slate-200 bg-white"
        }

        `}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-violet-50 via-white to-sky-50 opacity-80" />

        <div className="relative flex flex-col items-center px-10 py-16">

          <motion.div
            animate={{
              y: [0, -8, 0],
            }}
            transition={{
              repeat: Infinity,
              duration: 2,
            }}
            className="mb-8"
          >
            <div className="flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-sky-500 shadow-2xl">

              <Upload className="h-10 w-10 text-white"/>

            </div>
          </motion.div>

          <h2 className="text-3xl font-bold text-slate-900">

            Drop your files here

          </h2>

          <p className="mt-4 max-w-xl text-center leading-7 text-slate-500">

            Alex automatically extracts text, creates chunks,
            generates embeddings and indexes your knowledge.

          </p>

          {selectedFile ? (

            <motion.div
              initial={{opacity:0}}
              animate={{opacity:1}}
              className="mt-10 flex items-center gap-4 rounded-2xl border bg-white px-5 py-4 shadow-sm"
            >

              <FileText className="h-8 w-8 text-violet-600"/>

              <div>

                <p className="font-semibold">

                  {selectedFile.name}

                </p>

                <p className="text-sm text-slate-500">

                  {(selectedFile.size/1024).toFixed(1)} KB

                </p>

              </div>

              <CheckCircle2 className="ml-4 h-6 w-6 text-emerald-500"/>

            </motion.div>

          ) : (

            <Button
              className="mt-10 rounded-full px-8"
              onClick={() => inputRef.current?.click()}
            >

              Browse Files

            </Button>

          )}

          {selectedFile && (

            <Button
              className="mt-8 rounded-full px-8"
              disabled={loading}
              onClick={onUpload}
            >

              {loading ? (

                <>

                  <Loader2 className="mr-2 h-4 w-4 animate-spin"/>

                  Uploading...

                </>

              ) : (

                <>

                  <Sparkles className="mr-2 h-4 w-4"/>

                  Upload Knowledge

                </>

              )}

            </Button>

          )}

          <div className="mt-10 flex gap-3">

            <span className="rounded-full border bg-white px-3 py-1 text-xs">

              PDF

            </span>

            <span className="rounded-full border bg-white px-3 py-1 text-xs">

              TXT

            </span>

            <span className="rounded-full border bg-white px-3 py-1 text-xs">

              AI Indexed

            </span>

          </div>

        </div>
      </motion.div>
    </>
  );
}