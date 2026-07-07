"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BrainCircuit, Sparkles } from "lucide-react";

import { cn } from "@/lib/utils";
import { navItems } from "@/types/navigation";

interface SidebarProps {
  onNavigate?: () => void;
  className?: string;
}

export function Sidebar({ onNavigate, className }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "flex h-full w-full flex-col rounded-[28px] border border-slate-200/80 bg-white/85 p-3 shadow-[0_30px_90px_-45px_rgba(15,23,42,0.45)] backdrop-blur-xl",
        className
      )}
    >
      <div className="flex items-center gap-3 rounded-[22px] border border-violet-100 bg-gradient-to-br from-violet-600 to-fuchsia-500 p-3 text-white">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/20">
          <BrainCircuit className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm font-semibold leading-none">Universal Context</p>
          <p className="mt-1 text-xs text-violet-100">Engine • Alex</p>
        </div>
      </div>

      <nav className="mt-4 flex-1 space-y-1.5">
        {navItems.map((item) => {
          const isActive =
            item.href === "/workspace"
              ? pathname === "/workspace"
              : pathname.startsWith(item.href);
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-medium transition-all",
                isActive
                  ? "bg-violet-600 text-white shadow-[0_16px_35px_-20px_rgba(124,58,237,0.7)]"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {item.title}
            </Link>
          );
        })}
      </nav>

      <div className="rounded-[22px] border border-slate-200 bg-slate-50/80 p-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
          <Sparkles className="h-4 w-4 text-violet-600" />
          Premium workspace
        </div>
        <p className="mt-1 text-xs text-slate-500">
          Your knowledge, actions, and connected tools are always in sync.
        </p>
      </div>
    </aside>
  );
}
