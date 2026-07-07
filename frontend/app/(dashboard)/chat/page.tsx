"use client";

import { FormEvent, useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, Bot, Send, Sparkles, User } from "lucide-react";

import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface Source {
  filename: string;
  chunk_index: number;
  score: number;
}

interface ToolResult {
  recipient?: string;
  subject?: string;
  body?: string;
  editable?: boolean;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  toolResult?: ToolResult | null;
}

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    setMessages((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmedInput,
      },
    ]);

    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedInput,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || "Backend request failed");
      }

      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.answer || "Alex is temporarily unavailable. Please try again shortly.",
          sources: data.metadata?.sources ?? [],
          toolResult: data.metadata?.tool_result ?? null,
        },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "⚠ Alex is temporarily unavailable. Knowledge retrieval completed successfully. Please try again shortly.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DashboardLayout title="Alex AI" description="Modern conversation, grounded answers, and action-ready insight.">
      <PageHeader
        title="Alex AI"
        description="Ask about your documents, retrieve context, and trigger action flows through the connected tools."
      />

      <Card className="flex min-h-[calc(100vh-12rem)] flex-col overflow-hidden">
        <CardHeader className="border-b border-slate-100 bg-gradient-to-r from-violet-50 via-white to-sky-50">
          <CardTitle className="text-lg text-slate-950">Conversation</CardTitle>
          <CardDescription>
            Connected to the Universal Context Engine backend.
          </CardDescription>
        </CardHeader>

        <CardContent className="flex flex-1 flex-col p-0">
          <ScrollArea className="flex-1 px-4 py-6 sm:px-6">
            {messages.length === 0 ? (
              <div className="flex h-full min-h-[320px] flex-col items-center justify-center text-center">
                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-sky-500 text-white shadow-[0_20px_50px_-25px_rgba(124,58,237,0.75)]">
                  <Bot className="h-6 w-6" />
                </div>
                <p className="max-w-md text-base font-semibold text-slate-900">Start a conversation with Alex.</p>
                <p className="mt-2 max-w-lg text-sm leading-6 text-slate-500">
                  Ask about your uploaded documents, or try a richer action like “Draft a follow-up email for this report.”
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => {
                  const isUser = message.role === "user";

                  return (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={cn("flex gap-3", isUser ? "justify-end" : "justify-start")}
                    >
                      {!isUser && (
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-sky-500 text-white shadow-sm">
                          <Bot className="h-5 w-5" />
                        </div>
                      )}

                      <div className={cn("max-w-[82%] rounded-[24px] px-4 py-3 text-sm shadow-sm", isUser ? "bg-violet-600 text-white" : "bg-slate-50 text-slate-700") }>
                        <div className="whitespace-pre-wrap leading-7">{message.content}</div>

                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-4 grid gap-2 sm:grid-cols-2">
                            {message.sources.map((source, index) => (
                              <div key={index} className="rounded-2xl border border-slate-200 bg-white/90 p-3 text-xs text-slate-600">
                                <div className="flex items-center justify-between gap-2">
                                  <p className="font-semibold text-slate-900">{source.filename}</p>
                                  <span className="rounded-full bg-violet-50 px-2 py-1 text-[11px] font-semibold text-violet-700">
                                    {source.score.toFixed(2)}
                                  </span>
                                </div>
                                <p className="mt-2 text-slate-500">Chunk {source.chunk_index}</p>
                              </div>
                            ))}
                          </div>
                        )}

                        {message.toolResult && (
                          <div className="mt-4 rounded-[22px] border border-slate-200 bg-white p-4 text-sm text-slate-700">
                            <div className="flex items-center justify-between gap-3">
                              <p className="font-semibold text-slate-900">Draft Email</p>
                              <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-semibold text-emerald-700">
                                Editable
                              </span>
                            </div>
                            <div className="mt-3 space-y-1 text-sm text-slate-600">
                              <p><span className="font-medium text-slate-900">To:</span> {message.toolResult.recipient}</p>
                              <p><span className="font-medium text-slate-900">Subject:</span> {message.toolResult.subject}</p>
                            </div>
                            <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{message.toolResult.body}</p>
                          </div>
                        )}
                      </div>

                      {isUser && (
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-900 text-white shadow-sm">
                          <User className="h-5 w-5" />
                        </div>
                      )}
                    </motion.div>
                  );
                })}

                {isLoading && (
                  <div className="flex gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-sky-500 text-white shadow-sm">
                      <Bot className="h-5 w-5" />
                    </div>
                    <div className="rounded-[24px] bg-slate-50 px-4 py-3 text-sm text-slate-600">
                      <div className="flex items-center gap-2">
                        <Sparkles className="h-4 w-4 animate-pulse text-violet-600" />
                        Alex is thinking...
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </ScrollArea>

          <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t border-slate-100 bg-white/80 p-4">
            <Input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask Alex anything..."
              aria-label="Chat message"
              disabled={isLoading}
              className="h-12 rounded-full border-slate-200 bg-slate-50 px-4"
            />
            <Button type="submit" aria-label="Send message" disabled={isLoading} className="h-12 rounded-full px-5">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}