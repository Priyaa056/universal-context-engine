import {
  BookOpen,
  Bot,
  LayoutGrid,
  PlugZap,
  Settings,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
}

export const navItems: NavItem[] = [
  {
    title: "Workspace",
    href: "/workspace",
    icon: LayoutGrid,
  },
  {
    title: "Knowledge Hub",
    href: "/knowledge-base",
    icon: BookOpen,
  },
  {
    title: "Alex AI",
    href: "/chat",
    icon: Bot,
  },
  {
    title: "Connected Apps",
    href: "/tools",
    icon: PlugZap,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
];
