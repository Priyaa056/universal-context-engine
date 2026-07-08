"use client";

import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export default function SearchBar({
  value,
  onChange,
}: Props) {
  return (
    <div className="relative w-full max-w-md">
      <Search className="absolute left-4 top-3.5 h-4 w-4 text-slate-400" />

      <Input
        placeholder="Search documents..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-11 rounded-2xl border-slate-200 pl-11 pr-12 shadow-sm"
      />

      {value && (
        <Button
          size="icon"
          variant="ghost"
          className="absolute right-1 top-1 h-9 w-9 rounded-xl"
          onClick={() => onChange("")}
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}