"use client";

import { FormEvent, useState } from "react";
import { Bot, Send, User } from "lucide-react";

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

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedInput = input.trim();
    if (!trimmedInput) {
      return;
    }

    setMessages((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmedInput,
      },
    ]);
    setInput("");
  };

  return (
    <DashboardLayout
      title="Chat"
      description="Converse with the Universal Context Engine."
    >
      <PageHeader
        title="AI Chat"
        description="Modern chat interface ready for future agent and MCP integration."
      />

      <Card className="flex min-h-[calc(100vh-12rem)] flex-col shadow-sm">
        <CardHeader className="border-b border-border">
          <CardTitle className="text-base">Conversation</CardTitle>
          <CardDescription>
            Messages are stored locally for Phase 1 UI preview only.
          </CardDescription>
        </CardHeader>

        <CardContent className="flex flex-1 flex-col p-0">
          <ScrollArea className="flex-1 px-4 py-6">
            {messages.length === 0 ? (
              <div className="flex h-full min-h-[320px] flex-col items-center justify-center text-center">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-muted">
                  <Bot className="h-5 w-5 text-muted-foreground" />
                </div>
                <p className="max-w-md text-sm font-medium">
                  Start a conversation with the Universal Context Engine.
                </p>
                <p className="mt-1 max-w-md text-sm text-muted-foreground">
                  Ask questions, explore context, and prepare for future action
                  execution capabilities.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => {
                  const isUser = message.role === "user";

                  return (
                    <div
                      key={message.id}
                      className={cn(
                        "flex gap-3",
                        isUser ? "justify-end" : "justify-start"
                      )}
                    >
                      {!isUser ? (
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
                          <Bot className="h-4 w-4 text-muted-foreground" />
                        </div>
                      ) : null}

                      <div
                        className={cn(
                          "max-w-[80%] rounded-lg px-4 py-2.5 text-sm",
                          isUser
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted text-foreground"
                        )}
                      >
                        {message.content}
                      </div>

                      {isUser ? (
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                          <User className="h-4 w-4" />
                        </div>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            )}
          </ScrollArea>

          <form
            onSubmit={handleSubmit}
            className="flex items-center gap-2 border-t border-border p-4"
          >
            <Input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Type your message..."
              aria-label="Chat message"
            />
            <Button type="submit" aria-label="Send message">
              <Send className="h-4 w-4" />
              Send
            </Button>
          </form>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}
