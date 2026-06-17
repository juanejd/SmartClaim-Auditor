"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getClauses } from "@/lib/api";
import type { ClausesDoc } from "@/lib/types";

interface ClaimFormProps {
  onSubmit: (data: {
    complaint_text: string;
    contract_clauses: string;
  }) => void;
  isSubmitting?: boolean;
}

export function ClaimForm({ onSubmit, isSubmitting }: ClaimFormProps) {
  const [complaintText, setComplaintText] = useState("");
  const [contractClauses, setContractClauses] = useState("");
  const [clauseDocs, setClauseDocs] = useState<ClausesDoc[]>([]);

  useEffect(() => {
    getClauses()
      .then(setClauseDocs)
      .catch(() => {});
  }, []);

  const clauseById = clauseDocs.reduce<
    Record<string, { doc: string; ref: string; title: string; text: string }>
  >((acc, doc) => {
    for (const section of doc.sections) {
      for (const clause of section.clauses) {
        acc[clause.id] = {
          doc: doc.document,
          ref: clause.ref,
          title: clause.title,
          text: clause.text,
        };
      }
    }
    return acc;
  }, {});

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!complaintText.trim()) return;
    onSubmit({
      complaint_text: complaintText,
      contract_clauses: contractClauses,
    });
  }

  function handleClauseSelect(clauseId: string | null) {
    if (!clauseId) return;
    const entry = clauseById[clauseId];
    if (entry) setContractClauses(entry.text);
  }

  return (
    <Card className="border-border bg-card">
      <CardHeader className="pb-4">
        <CardTitle className="font-display text-xl text-foreground">
          Enviar reclamo para auditoría
        </CardTitle>
        <CardDescription className="text-muted-foreground text-sm">
          Proporcione la descripción del reclamo. Las cláusulas contractuales
          son opcionales — el sistema ORION recuperará evidencia de respaldo
          automáticamente.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          {/* Complaint text — required */}
          <div className="flex flex-col gap-2">
            <label
              htmlFor="complaint-text"
              className="text-sm font-medium text-foreground"
            >
              Descripción del reclamo
            </label>
            <Textarea
              id="complaint-text"
              value={complaintText}
              onChange={(e) => setComplaintText(e.target.value)}
              placeholder="Describa el evento de pérdida, los daños incurridos y el monto reclamado…"
              rows={4}
              className="font-sans text-sm resize-none"
              required
            />
            <p className="text-xs text-muted-foreground">
              Describa el incidente y lo que el reclamante está solicitando.
            </p>
          </div>

          {/* Contract clauses — optional */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <label
                htmlFor="contract-clauses"
                className="text-sm font-medium text-foreground"
              >
                Cláusulas del contrato{" "}
                <span className="text-muted-foreground font-normal">
                  (opcional)
                </span>
              </label>

              {clauseDocs.length > 0 && (
                <Select onValueChange={handleClauseSelect}>
                  <SelectTrigger className="h-7 w-auto max-w-xs text-xs font-mono border-border bg-input/30 hover:bg-input/50">
                    <SelectValue placeholder="Seleccionar cláusula…">
                      {(id: string) => {
                        const entry = clauseById[id];
                        if (!entry) return "Seleccionar cláusula…";
                        return `${entry.ref} ${entry.title}`;
                      }}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {clauseDocs.map((doc) =>
                      doc.sections.map((section) => (
                        <SelectGroup key={`${doc.id}-${section.id}`}>
                          <SelectLabel className="font-mono text-xs text-muted-foreground">
                            {doc.document} · {section.title}
                          </SelectLabel>
                          {section.clauses.map((clause) => (
                            <SelectItem key={clause.id} value={clause.id}>
                              <span className="font-mono text-xs text-muted-foreground mr-1">
                                {clause.ref}
                              </span>
                              {clause.title}
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      )),
                    )}
                  </SelectContent>
                </Select>
              )}
            </div>

            <Textarea
              id="contract-clauses"
              value={contractClauses}
              onChange={(e) => setContractClauses(e.target.value)}
              placeholder="Pegue las secciones de póliza o cláusulas contractuales relevantes, o seleccione una del menú desplegable…"
              rows={4}
              className="font-sans text-sm resize-none"
            />
            <p className="text-xs text-muted-foreground">
              Texto de póliza que el auditor cruzará con el reclamo. Puede
              editarlo libremente o dejarlo vacío.
            </p>
          </div>

          <div className="flex justify-end">
            <Button
              type="submit"
              disabled={isSubmitting || !complaintText.trim()}
            >
              {isSubmitting ? "Enviando…" : "Ejecutar auditoría"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
