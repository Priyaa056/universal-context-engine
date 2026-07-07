interface PageHeaderProps {
  title: string;
  description?: string;
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="mb-8 flex flex-col gap-2">
      <div className="inline-flex w-fit items-center gap-2 rounded-full border border-violet-200 bg-violet-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.3em] text-violet-700">
        Alex workspace
      </div>
      <h2 className="text-3xl font-semibold tracking-tight text-slate-950">{title}</h2>
      {description ? (
        <p className="max-w-2xl text-sm text-slate-600">{description}</p>
      ) : null}
    </div>
  );
}
