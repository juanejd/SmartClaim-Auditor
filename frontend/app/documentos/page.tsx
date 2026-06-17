"use client";

import { useState, useEffect } from "react";
import { DownloadIcon, FileTextIcon } from "lucide-react";
import { getDocuments, documentUrl } from "@/lib/api";
import type { DocumentMeta } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(0)} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}

export default function DocumentosPage() {
  const [documents, setDocuments] = useState<DocumentMeta[]>([]);
  const [selected, setSelected] = useState<DocumentMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDocuments()
      .then((docs) => {
        setDocuments(docs);
        if (docs.length > 0) setSelected(docs[0]);
      })
      .catch(() => setError("No se pudieron cargar los documentos."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-1 min-h-0 overflow-hidden bg-background">
      {/* Document list sidebar */}
      <aside className="w-72 shrink-0 border-r border-border flex flex-col h-full overflow-y-auto">
        <div className="p-4 border-b border-border">
          <h2 className="font-display text-base text-foreground">
            Manuales y pólizas
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Corpus de referencia del sistema de auditoría.
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
          {loading &&
            Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-14 w-full rounded-lg" />
            ))}

          {error && (
            <p className="text-sm text-destructive px-2 py-4">{error}</p>
          )}

          {!loading &&
            !error &&
            documents.map((doc) => (
              <button
                key={doc.filename}
                onClick={() => setSelected(doc)}
                className={[
                  "w-full text-left flex items-start gap-2.5 px-3 py-2.5 rounded-lg transition-colors",
                  selected?.filename === doc.filename
                    ? "bg-primary/10 text-foreground"
                    : "hover:bg-muted/40 text-muted-foreground hover:text-foreground",
                ].join(" ")}
              >
                <FileTextIcon
                  className={[
                    "size-4 shrink-0 mt-0.5",
                    selected?.filename === doc.filename
                      ? "text-primary"
                      : "text-muted-foreground",
                  ].join(" ")}
                />
                <div className="flex flex-col gap-0.5 min-w-0">
                  <span className="text-sm font-medium truncate">
                    {doc.label}
                  </span>
                  <Badge
                    variant="secondary"
                    className="font-mono text-xs w-fit px-1.5 py-0"
                  >
                    {formatBytes(doc.size_bytes)}
                  </Badge>
                </div>
              </button>
            ))}
        </div>
      </aside>

      {/* PDF viewer pane */}
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        {selected ? (
          <>
            <div className="shrink-0 border-b border-border px-6 py-3 flex items-center justify-between gap-4">
              <div className="flex flex-col gap-0.5 min-w-0">
                <h1 className="font-display text-base text-foreground truncate">
                  {selected.label}
                </h1>
                <p className="font-mono text-xs text-muted-foreground truncate">
                  {selected.filename}
                </p>
              </div>
              <a
                href={documentUrl(selected.filename)}
                download={selected.filename}
                className="shrink-0 flex items-center gap-1.5 font-mono text-xs text-muted-foreground hover:text-primary transition-colors px-3 py-1.5 rounded-md hover:bg-muted/40 border border-border"
              >
                <DownloadIcon className="size-3.5" />
                Descargar PDF
              </a>
            </div>

            <div className="flex-1 min-h-0">
              <iframe
                key={selected.filename}
                src={documentUrl(selected.filename)}
                title={selected.label}
                className="w-full h-full border-0"
                aria-label={`Visor de documento: ${selected.label}`}
              />
            </div>
          </>
        ) : (
          !loading && (
            <Card className="m-6 border-border bg-card">
              <CardContent className="py-16 text-center">
                <p className="text-muted-foreground text-sm">
                  Seleccione un documento para visualizarlo.
                </p>
              </CardContent>
            </Card>
          )
        )}
      </main>
    </div>
  );
}
