import type { ClaimRead, ClaimSummary } from "./types"

export const MOCK_CLAIM_1: ClaimRead = {
  claim_id: "CLM-2024-001847",
  complaint_text:
    "En la noche del 12 de marzo de 2024, una sobretensión eléctrica causada por un transformador defectuoso en nuestra calle provocó daños significativos en nuestro sistema de climatización y electrodomésticos de cocina. Según el registro de nuestro medidor inteligente, la sobretensión duró aproximadamente 4 segundos. Solicitamos el reembolso del costo de reposición de la unidad de climatización ($6.400), el refrigerador ($1.850) y el lavavajillas ($720), con un total de $8.970.",
  contract_clauses:
    "Sección 4.2 — Cobertura por daños eléctricos: La póliza cubre la pérdida o el daño físico directo causado por corriente eléctrica generada artificialmente, incluyendo sobretensiones originadas en infraestructura externa. La cobertura aplica a electrodomésticos instalados de forma permanente y sistemas de climatización. Quedan excluidos: el deterioro gradual, los defectos de fabricación y los daños a dispositivos electrónicos portátiles que no estén cableados de forma permanente a la vivienda.",
  status: "AUDITED",
  intent_label: "ELECTRICAL_FAILURE",
  confidence: 0.91,
  draft_verdict: "REJECTED",
  draft_justification:
    "El análisis inicial marcó el reclamo como potencialmente fuera del alcance de la cobertura debido a redacción ambigua en torno a las sobretensiones de origen externo. Sin embargo, la evidencia del registro del medidor inteligente no fue evaluada en su totalidad durante la etapa de borrador.",
  corrections_applied: true,
  final_verdict: "INSPECTION_REQUIRED",
  final_justification:
    "La Sección 4.2 de la póliza cubre explícitamente las sobretensiones provenientes de infraestructura externa, lo cual se ajusta al fallo del transformador reportado. El registro del medidor inteligente aporta evidencia corroborante del evento. No obstante, el costo de reposición de la unidad de climatización ($6.400) supera el umbral por artículo individual definido en el Anexo B sin que exista una tasación previa al siniestro registrada. Se requiere una inspección para verificar el estado anterior a la pérdida y confirmar los valores de reposición de los electrodomésticos antes de la aprobación definitiva.",
  rag_citation:
    "La póliza cubre la pérdida o el daño físico directo causado por corriente eléctrica generada artificialmente, incluyendo sobretensiones originadas en infraestructura externa.",
  rag_chunks: [
    {
      text: "Sección 4.2 — Cobertura por daños eléctricos: La póliza cubre la pérdida o el daño físico directo causado por corriente eléctrica generada artificialmente, incluyendo sobretensiones originadas en infraestructura externa. La cobertura aplica a electrodomésticos instalados de forma permanente y sistemas de climatización.",
      source_section: "§4.2 Cobertura por daños eléctricos",
      page: 12,
      score: 0.947,
    },
    {
      text: "Anexo B — Umbrales por artículo individual: Cualquier reclamo individual que supere los $5.000 requiere una tasación previa al siniestro con fecha dentro de los 36 meses anteriores a la fecha del reclamo, o una estimación certificada de costo de reposición emitida por un contratista habilitado y presentada dentro de los 30 días del evento.",
      source_section: "Anexo B — Umbrales por artículo individual",
      page: 34,
      score: 0.812,
    },
    {
      text: "Sección 4.5 — Requisitos de evidencia: Los registros de medidores inteligentes, los informes de incidentes de la empresa distribuidora y las evaluaciones eléctricas de terceros son aceptados como evidencia corroborante en reclamos por sobretensión. Los registros deben presentarse en formato de exportación sin procesar desde el portal de la empresa de servicios públicos.",
      source_section: "§4.5 Requisitos de evidencia",
      page: 13,
      score: 0.774,
    },
  ],
  received_at: "2024-03-14T09:22:11Z",
}

export const MOCK_CLAIM_2: ClaimRead = {
  claim_id: "CLM-2024-002103",
  complaint_text:
    "El 28 de febrero de 2024, durante la ola de frío, se produjo una rotura de cañería en el baño del segundo piso. Los daños por agua se extendieron al cielorraso inferior y saturaron aproximadamente 3,7 m² de piso de madera maciza en el dormitorio principal. Hemos obtenido tres presupuestos de contratistas con un promedio de $12.200 para la remediación, el reemplazo del revestimiento y el refinamiento del piso.",
  contract_clauses:
    "Sección 6.1 — Daños por agua — Súbitos y accidentales: La cobertura aplica a la descarga o desbordamiento súbito y accidental de agua proveniente de una instalación de plomería dentro de la vivienda. Los daños por cañerías congeladas están cubiertos siempre que la vivienda haya estado calefaccionada a un mínimo de 13 °C durante el período de congelamiento. Sección 6.3 — Exclusiones: La cobertura no aplica a filtraciones, goteras o daños continuos por agua que se hayan extendido por un período superior a 14 días y que el asegurado conocía o debería haber conocido.",
  status: "AUDITED",
  intent_label: "PHYSICAL_DAMAGE",
  confidence: 0.88,
  draft_verdict: "APPROVED",
  draft_justification:
    "El reclamo se encuadra claramente en el alcance de la Sección 6.1. Existe evidencia del evento de cañería congelada durante la ola de frío documentada. Los presupuestos de remediación se encuentran dentro de los rangos habituales para el área de daño reportada.",
  corrections_applied: false,
  final_verdict: "APPROVED",
  final_justification:
    "Los daños por agua resultantes de una cañería rota durante una ola de frío documentada están cubiertos bajo la Sección 6.1. El expediente incluye un registro del termostato que confirma que la vivienda se mantuvo por encima de 13 °C, cumpliendo la condición de cobertura por cañería congelada. Los tres presupuestos promedian $12.200, valor coherente con las tarifas actuales de remediación para el alcance del daño reportado. El reclamo es aprobado hasta el límite de la póliza para daños por agua por siniestro ($15.000). Aplica un deducible de $1.000.",
  rag_citation:
    "Los daños por cañerías congeladas están cubiertos siempre que la vivienda haya estado calefaccionada a un mínimo de 13 °C durante el período de congelamiento.",
  rag_chunks: [
    {
      text: "Sección 6.1 — Daños por agua — Súbitos y accidentales: La cobertura aplica a la descarga o desbordamiento súbito y accidental de agua proveniente de una instalación de plomería dentro de la vivienda. Los daños por cañerías congeladas están cubiertos siempre que la vivienda haya estado calefaccionada a un mínimo de 13 °C durante el período de congelamiento.",
      source_section: "§6.1 Daños por agua — Súbitos y accidentales",
      page: 18,
      score: 0.931,
    },
    {
      text: "Sección 6.3 — Exclusiones: La cobertura no aplica a filtraciones, goteras o daños continuos por agua que se hayan extendido por un período superior a 14 días y que el asegurado conocía o debería haber conocido. La remediación por hongos está cubierta únicamente cuando resulta de un evento de daño por agua cubierto y reportado dentro de las 72 horas.",
      source_section: "§6.3 Exclusiones por daños de agua",
      page: 19,
      score: 0.799,
    },
    {
      text: "Sección 9.4 — Presupuestos de contratistas: Cuando el costo total de remediación supera los $10.000, se requieren tres presupuestos independientes de contratistas habilitados. La aseguradora se reserva el derecho de seleccionar cualquier contratista habilitado dentro del 15% del presupuesto más bajo. Las medidas de protección de emergencia (extracción de agua, deshumidificación) están preaprobadas hasta $2.500 sin autorización previa.",
      source_section: "§9.4 Presupuestos de contratistas",
      page: 27,
      score: 0.743,
    },
  ],
  received_at: "2024-03-01T14:45:33Z",
}

export const MOCK_HISTORY: ClaimSummary[] = [
  {
    claim_id: "CLM-2024-001847",
    complaint_text:
      "En la noche del 12 de marzo de 2024, una sobretensión eléctrica causada por un transformador defectuoso provocó daños significativos en nuestro sistema de climatización y electrodomésticos.",
    intent_label: "ELECTRICAL_FAILURE",
    status: "AUDITED",
    final_verdict: "INSPECTION_REQUIRED",
    received_at: "2024-03-14T09:22:11Z",
  },
  {
    claim_id: "CLM-2024-002103",
    complaint_text:
      "El 28 de febrero de 2024, durante la ola de frío, se produjo una rotura de cañería en el baño del segundo piso. Los daños por agua se extendieron al cielorraso inferior.",
    intent_label: "PHYSICAL_DAMAGE",
    status: "AUDITED",
    final_verdict: "APPROVED",
    received_at: "2024-03-01T14:45:33Z",
  },
  {
    claim_id: "CLM-2024-001622",
    complaint_text: "Reclamo en procesamiento — pendiente de evaluación.",
    intent_label: "OTHER",
    status: "PROCESSING",
    final_verdict: null,
    received_at: "2024-02-22T11:03:57Z",
  },
]
