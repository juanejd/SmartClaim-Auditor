import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface VerdictBadgeProps {
  verdict: string | null;
  className?: string;
}

export function VerdictBadge({ verdict, className }: VerdictBadgeProps) {
  if (!verdict) {
    return (
      <Badge
        variant="secondary"
        className={cn("font-mono text-xs tracking-wider", className)}
      >
        SIN CLASIFICAR
      </Badge>
    );
  }

  const config: Record<string, { label: string; className: string }> = {
    APPROVED: {
      label: "APROBADO",
      className:
        "bg-verdict-approved/15 text-verdict-approved border border-verdict-approved/30 font-mono text-xs tracking-wider",
    },
    REJECTED: {
      label: "RECHAZADO",
      className:
        "bg-verdict-rejected/15 text-verdict-rejected border border-verdict-rejected/30 font-mono text-xs tracking-wider",
    },
    INSPECTION_REQUIRED: {
      label: "REQUIERE INSPECCIÓN",
      className:
        "bg-verdict-inspect/15 text-verdict-inspect border border-verdict-inspect/30 font-mono text-xs tracking-wider",
    },
  };

  const entry = config[verdict] ?? {
    label: verdict,
    className:
      "bg-muted text-muted-foreground font-mono text-xs tracking-wider",
  };

  return (
    <Badge className={cn(entry.className, className)}>{entry.label}</Badge>
  );
}
