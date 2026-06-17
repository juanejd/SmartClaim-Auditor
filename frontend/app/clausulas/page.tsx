"use client";

import { useState, useEffect } from "react";
import { getClauses } from "@/lib/api";
import type { ClausesDoc } from "@/lib/types";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";

export default function ClausulasPage() {
  const [corpus, setCorpus] = useState<ClausesDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getClauses()
      .then(setCorpus)
      .catch(() => setError("No se pudieron cargar las cláusulas."))
      .finally(() => setLoading(false));
  }, []);

  const totalClauses = corpus.reduce(
    (sum, doc) =>
      sum + doc.sections.reduce((s, sec) => s + sec.clauses.length, 0),
    0,
  );

  return (
    <div className="flex-1 overflow-y-auto bg-background">
      <div className="max-w-5xl mx-auto px-6 py-8 flex flex-col gap-8">
        {/* Page header */}
        <div className="flex flex-col gap-1.5">
          <h1 className="font-display text-2xl text-foreground">
            Corpus de cláusulas contractuales
          </h1>
          <p className="text-sm text-muted-foreground">
            Base de referencia estructurada utilizada por el auditor de IA para
            la citación y el análisis de cobertura.
          </p>
          {!loading && !error && (
            <div className="flex items-center gap-3 mt-1">
              <Badge variant="secondary" className="font-mono text-xs">
                {corpus.length} documentos
              </Badge>
              <Badge variant="secondary" className="font-mono text-xs">
                {totalClauses} cláusulas
              </Badge>
            </div>
          )}
        </div>

        {/* Loading state */}
        {loading && (
          <div className="flex flex-col gap-6">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-48 w-full rounded-lg" />
            ))}
          </div>
        )}

        {/* Error state */}
        {error && (
          <Card className="border-border bg-card">
            <CardContent className="py-10 text-center">
              <p className="text-sm text-destructive">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Corpus */}
        {!loading &&
          !error &&
          corpus.map((doc) => (
            <div key={doc.id} className="flex flex-col gap-4">
              {/* Document heading */}
              <div className="flex items-center gap-3 flex-wrap">
                <h2 className="font-display text-lg text-foreground">
                  {doc.document}
                </h2>
                {doc.code && (
                  <Badge
                    variant="secondary"
                    className="font-mono text-xs text-primary border-primary/20 bg-primary/5"
                  >
                    {doc.code}
                  </Badge>
                )}
              </div>

              {/* Sections */}
              <div className="flex flex-col gap-4">
                {doc.sections.map((section, sIdx) => (
                  <Card key={section.id} className="border-border bg-card">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium text-foreground">
                        {section.title}
                      </CardTitle>
                      <CardDescription className="font-mono text-xs text-muted-foreground">
                        {section.clauses.length}{" "}
                        {section.clauses.length === 1
                          ? "cláusula"
                          : "cláusulas"}
                      </CardDescription>
                    </CardHeader>
                    <Separator />
                    <CardContent className="p-0">
                      <div className="divide-y divide-border">
                        {section.clauses.map((clause, cIdx) => (
                          <div
                            key={clause.id}
                            className="px-4 py-3 flex flex-col gap-1.5"
                          >
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-mono text-xs text-primary bg-primary/10 px-1.5 py-0.5 rounded">
                                {clause.ref}
                              </span>
                              <span className="text-sm font-medium text-foreground">
                                {clause.title}
                              </span>
                            </div>
                            <p className="text-sm text-muted-foreground leading-relaxed">
                              {clause.text}
                            </p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Divider between documents */}
              {doc !== corpus[corpus.length - 1] && (
                <Separator className="mt-2" />
              )}
            </div>
          ))}
      </div>
    </div>
  );
}
