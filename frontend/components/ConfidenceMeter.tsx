interface ConfidenceMeterProps {
  confidence: number | null;
}

export function ConfidenceMeter({ confidence }: ConfidenceMeterProps) {
  if (confidence === null) return null;

  const pct = Math.round(confidence * 100);
  const color =
    pct >= 80
      ? "bg-verdict-approved"
      : pct >= 60
        ? "bg-verdict-inspect"
        : "bg-verdict-rejected";

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-1.5 bg-border rounded-full overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all", color)}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="font-mono text-xs text-muted-foreground tabular-nums w-9 text-right">
        {pct}%
      </span>
    </div>
  );
}

function cn(...args: (string | undefined | false | null)[]): string {
  return args.filter(Boolean).join(" ");
}
