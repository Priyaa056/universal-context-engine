"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Bot, BrainCircuit, DatabaseZap, ShieldCheck, Sparkles, Workflow } from "lucide-react";

const featureCards = [
  {
    title: "Knowledge Hub",
    description: "Retrieve knowledge from your documents.",
    icon: BrainCircuit,
  },
  {
    title: "Alex AI",
    description: "Chat naturally with your AI assistant.",
    icon: Bot,
  },
  {
    title: "Connected Apps",
    description: "Use AI across all connected tools.",
    icon: Workflow,
  },
  {
    title: "Document Intelligence",
    description: "Upload documents and gain insights.",
    icon: DatabaseZap,
  },
];

const floatingParticles = Array.from({ length: 18 }, (_, index) => ({
  id: index,
  left: `${(index * 7) % 100}%`,
  top: `${(index * 13) % 100}%`,
  size: `${10 + (index % 4) * 4}px`,
  delay: `${index * 0.18}s`,
}));

export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(124,58,237,0.18),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(59,130,246,0.14),_transparent_32%),linear-gradient(135deg,_#f8fafc_0%,_#fdfdff_100%)] text-slate-900">
      <div className="absolute inset-0 overflow-hidden">
        {floatingParticles.map((particle) => (
          <motion.span
            key={particle.id}
            className="absolute rounded-full bg-white/70 blur-[1px]"
            style={{ left: particle.left, top: particle.top, width: particle.size, height: particle.size }}
            animate={{ y: [0, -14, 0], opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 5 + (particle.id % 4), repeat: Number.POSITIVE_INFINITY, delay: Number(particle.delay), ease: "easeInOut" }}
          />
        ))}
      </div>

      <section className="relative mx-auto flex min-h-screen max-w-7xl flex-col items-center justify-center px-6 py-16 sm:px-10 lg:px-16">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="glass-card relative w-full max-w-6xl overflow-hidden px-6 py-10 shadow-[0_45px_120px_-45px_rgba(15,23,42,0.4)] sm:px-10 lg:px-14 lg:py-14"
        >
          <div className="absolute inset-0 bg-[linear-gradient(120deg,rgba(255,255,255,0.65),rgba(255,255,255,0.15),rgba(255,255,255,0.65))]" />
          <div className="relative flex flex-col items-center text-center">
            <motion.div
              animate={{ y: [0, -9, 0], rotate: [0, 2, -2, 0] }}
              transition={{ duration: 5.5, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
              className="pulse-glow relative mb-7 flex h-28 w-28 items-center justify-center rounded-full border border-violet-200/80 bg-gradient-to-br from-violet-600 via-fuchsia-500 to-sky-500 text-white shadow-[0_30px_80px_-25px_rgba(124,58,237,0.7)]"
            >
              <Sparkles className="h-12 w-12" />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.16, duration: 0.6 }}
              className="max-w-3xl"
            >
              <p className="text-sm font-semibold uppercase tracking-[0.35em] text-violet-700">Hello!</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl lg:text-6xl">
                I’m Alex.
              </h1>
              <p className="mt-4 text-lg text-slate-600 sm:text-xl">
                Your AI Assistant for the Universal Context Engine.
              </p>
              <p className="mx-auto mt-5 max-w-2xl text-base leading-8 text-slate-600 sm:text-lg">
                I help you understand your documents, retrieve knowledge, execute actions, and work across all your connected applications.
              </p>
            </motion.div>

            <div className="mt-10 grid w-full gap-4 md:grid-cols-2 xl:grid-cols-4">
              {featureCards.map((card, index) => {
                const Icon = card.icon;
                return (
                  <motion.div
                    key={card.title}
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.14 + index * 0.08, duration: 0.45 }}
                    whileHover={{ y: -6, scale: 1.02 }}
                    className="rounded-[24px] border border-slate-200/80 bg-white/80 p-5 text-left shadow-[0_24px_70px_-35px_rgba(15,23,42,0.35)] backdrop-blur"
                  >
                    <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 to-sky-500 text-white">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h2 className="mt-4 text-lg font-semibold text-slate-950">{card.title}</h2>
                    <p className="mt-2 text-sm leading-6 text-slate-600">{card.description}</p>
                  </motion.div>
                );
              })}
            </div>

            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.55 }}
              className="mt-10 flex flex-col items-center gap-4"
            >
              <Link href="/workspace">
                <motion.button
                  whileHover={{ y: -3, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="group inline-flex items-center gap-3 rounded-full bg-gradient-to-r from-violet-600 via-fuchsia-500 to-sky-500 px-7 py-4 text-base font-semibold text-white shadow-[0_22px_70px_-25px_rgba(124,58,237,0.7)]"
                >
                  Let’s Get Started
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </motion.button>
              </Link>
              <p className="flex items-center gap-2 text-sm text-slate-500">
                <ShieldCheck className="h-4 w-4 text-emerald-600" />
                Your data remains private and secure.
              </p>
            </motion.div>
          </div>
        </motion.div>
      </section>
    </main>
  );
}
