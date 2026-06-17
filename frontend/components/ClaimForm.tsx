"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

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

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!complaintText.trim() || !contractClauses.trim()) return;
    onSubmit({
      complaint_text: complaintText,
      contract_clauses: contractClauses,
    });
  }

  return (
    <Card className="border-border bg-card">
      <CardHeader className="pb-4">
        <CardTitle className="font-display text-xl text-foreground">
          Enviar reclamo para auditoría
        </CardTitle>
        <CardDescription className="text-muted-foreground text-sm">
          Proporcione la descripción del reclamo y las cláusulas contractuales
          relevantes. El auditor de IA recuperará evidencia de respaldo y
          emitirá un veredicto con cita completa.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div className="flex flex-col gap-5">
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
            <div className="flex flex-col gap-2">
              <label
                htmlFor="contract-clauses"
                className="text-sm font-medium text-foreground"
              >
                Cláusulas del contrato
              </label>
              <Textarea
                id="contract-clauses"
                value={contractClauses}
                onChange={(e) => setContractClauses(e.target.value)}
                placeholder="Pegue las secciones de póliza o cláusulas contractuales relevantes para este tipo de reclamo…"
                rows={4}
                className="font-sans text-sm resize-none"
                required
              />
              <p className="text-xs text-muted-foreground">
                Las secciones de póliza que el sistema de IA cruzará con el
                reclamo.
              </p>
            </div>
          </div>
          <div className="flex justify-end">
            <Button
              type="submit"
              disabled={
                isSubmitting || !complaintText.trim() || !contractClauses.trim()
              }
            >
              {isSubmitting ? "Enviando…" : "Ejecutar auditoría"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
