import {
  BookOpen,
  LayoutDashboard,
  MessageSquare,
  Wrench,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
}

export const navItems: NavItem[] = [
  {
    title: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    title: "Knowledge Base",
    href: "/knowledge-base",
    icon: BookOpen,
  },
  {
    title: "Tools",
    href: "/tools",
    icon: Wrench,
  },
  {
    title: "Chat",
    href: "/chat",
    icon: MessageSquare,
  },
];
