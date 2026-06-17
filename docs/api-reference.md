# Referencia de la API

Esta referencia detalla los endpoints RESTful expuestos por el backend de SmartClaim-Auditor. El servidor opera de manera síncrona, devolviendo las respuestas consolidadas en cada petición.

## Esquemas de datos clave

### `ClaimBase`
- `complaint_text` (string, requerido): Descripción textual del problema o reclamo.
- `contract_clauses` (string | null, opcional): Texto explícito de cláusulas aplicables provistas por el usuario.

### `ClaimSummary`
- `claim_id` (UUID): Identificador único del reclamo.
- `complaint_text` (string): Vista previa o texto completo del reclamo original.
- `intent_label` (string): Clasificación de la intención (ej. REEMBOLSO, REPARACION).
- `status` (string): Estado de la auditoría.
- `final_verdict` (string): Veredicto final emitido por la IA.
- `received_at` (datetime): Fecha y hora de recepción de la solicitud.

## Endpoints de Reclamos

### Crear un reclamo
**POST** `/api/claims`

Evalúa un reclamo ejecutando el pipeline completo (clasificación, recuperación de contexto y auditoría) y devuelve el veredicto final.

**Cuerpo de la petición (JSON):**
```json
{
  "complaint_text": "La pantalla del televisor llegó rota al sacarlo de la caja.",
  "contract_clauses": null
}
```

**Respuesta Exitosa (200 OK):** Devuelve un objeto detallando el resultado de la evaluación (traza de razonamiento y veredicto final).

### Listar historial de reclamos
**GET** `/api/claims`

Recupera una lista resumida de todos los reclamos procesados en el sistema.

**Respuesta Exitosa (200 OK):** Un arreglo de objetos `ClaimSummary`.

### Obtener detalles de un reclamo
**GET** `/api/claims/{id}`

Recupera la información completa de un reclamo específico, incluyendo la traza de auditoría y los fragmentos recuperados por RAG.

**Respuesta Exitosa (200 OK):** Detalles completos del reclamo evaluado.

### Eliminar un reclamo
**DELETE** `/api/claims/{id}`

Elimina un reclamo del historial de manera definitiva.

**Respuesta Exitosa:** `204 No Content`.
**Error (404 Not Found):** Si el ID especificado no existe.

## Endpoints de Documentos

### Listar documentos indexados
**GET** `/api/documents`

Devuelve una lista de los documentos en formato PDF disponibles en el sistema que alimentan la base de conocimiento RAG.

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "filename": "02_Poliza_Seguro_Hogar_Premium_2026.pdf",
    "label": "Póliza Seguro Hogar Premium 2026",
    "size_bytes": 102400
  }
]
```

### Visualizar documento fuente
**GET** `/api/documents/{filename}`

Sirve el archivo PDF crudo. Este endpoint incluye medidas de seguridad contra ataques de cruce de directorios (path traversal).

**Respuesta Exitosa (200 OK):** Archivo `application/pdf`.
**Error (404 Not Found):** Si el archivo no existe en el repositorio o el acceso es inválido.

## Endpoints de Cláusulas

### Obtener base de cláusulas
**GET** `/api/clauses`

Devuelve el corpus estructurado de cláusulas extraídas de los documentos originales. Se utiliza en la interfaz para popular los selectores rápidos.

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": "doc_1",
    "document": "Seguro de Hogar",
    "sections": [
      {
        "id": "sec_1",
        "title": "Coberturas Generales",
        "clauses": [
          {
            "id": "cl_1",
            "ref": "1.1",
            "title": "Daños por agua",
            "text": "La póliza cubre daños ocasionados por filtraciones accidentales..."
          }
        ]
      }
    ]
  }
]
```
