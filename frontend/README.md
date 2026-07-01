# Universal Context Engine — Frontend

Next.js dashboard for the Universal Context Engine with MCP Action Layer.

## Overview

Phase 1 provides a professional SaaS-style dashboard with navigation, reusable components, and placeholder pages for Knowledge Base, Tools, and Chat. No backend integration or AI features are included in this phase.

## Tech Stack

- Next.js 15 (App Router)
- TypeScript
- TailwindCSS
- shadcn/ui
- Lucide Icons

## Folder Structure

```
frontend/
├── app/
│   ├── (dashboard)/
│   │   ├── page.tsx              # Dashboard
│   │   ├── knowledge-base/
│   │   ├── tools/
│   │   └── chat/
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── layout/                   # Sidebar, Navbar, DashboardLayout
│   └── ui/                       # shadcn/ui + custom components
├── lib/
│   └── constants.ts
├── types/
└── package.json
```

## Installation

```bash
npm install
```

## Run

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Pages

| Route             | Description                          |
|-------------------|--------------------------------------|
| `/`               | Dashboard with stats and activity    |
| `/knowledge-base` | Document upload and management UI    |
| `/tools`          | Connected tool cards                 |
| `/chat`           | AI chat interface (UI only)          |

## Reusable Components

- `Sidebar` — Responsive navigation with mobile sheet menu
- `Navbar` — Page header with mobile menu trigger
- `StatCard` — Dashboard metric cards
- `PageHeader` — Section titles and descriptions
- `ToolCard` — Tool status cards with badges

## Future Development

- Backend API integration
- RAG and ChromaDB document processing
- MCP tool connections
- Agent logic and decision engine
- Real-time chat with LLM providers
