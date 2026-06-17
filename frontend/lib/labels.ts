export const verdictLabels: Record<string, string> = {
  APPROVED: "Aprobado",
  REJECTED: "Rechazado",
  INSPECTION_REQUIRED: "Requiere inspección",
};

export const statusLabels: Record<string, string> = {
  RECEIVED: "Recibido",
  CLASSIFIED: "Clasificado",
  AUDITED: "Auditado",
  LOW_CONFIDENCE: "Confianza baja",
  PENDING: "Pendiente",
  PROCESSING: "Procesando…",
  FAILED: "Fallido",
};

export const intentLabels: Record<string, string> = {
  ELECTRICAL_FAILURE: "Falla eléctrica",
  OPERATION_ERROR: "Error de operación",
  FINANCIAL_WARRANTY: "Garantía financiera",
  PHYSICAL_DAMAGE: "Daño físico",
  OTHER: "Otro",
};

export function getVerdictLabel(verdict: string | null): string {
  if (!verdict) return "Sin clasificar";
  return verdictLabels[verdict] ?? verdict;
}

export function getStatusLabel(status: string): string {
  return statusLabels[status] ?? status;
}

export function getIntentLabel(intent: string | null): string {
  if (!intent) return "Sin clasificar";
  return intentLabels[intent] ?? intent.replace(/_/g, " ");
}

export const evidenceLabels = {
  ragChunksHeading: "Evidencia recuperada",
  contractClausesHeading: "Cláusulas del contrato",
  noRagChunks: "No se recuperaron fragmentos de evidencia.",
  noContractClauses: "Sin cláusulas contractuales registradas.",
  citationNotFound: "Cita — no localizada verbatim en la evidencia",
  citationNotFoundDetail:
    "La cita no pudo localizarse de forma exacta en los fragmentos recuperados ni en las cláusulas del contrato (puede haber sido parafraseada).",
} as const;

export const navLabels = {
  appTitle: "SmartClaim Auditor",
  appSubtitle: "Consola de auditoría de seguros asistida por ORION",
  documents: "Documentos",
  clauses: "Ver cláusulas",
  newClaim: "Nuevo reclamo",
  deleteClaim: "Eliminar",
  historyHeading: "Historial de reclamos",
  noHistory: "Aún no hay reclamos.",
  emptyState:
    "Envíe un reclamo para ver su traza de auditoría, o seleccione uno del historial.",
  auditTraceTitle: "Traza de razonamiento de auditoría",
  auditTraceDescription:
    "Cadena de evidencia paso a paso desde la clasificación hasta el veredicto final.",
} as const;
