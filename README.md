# SmartClaim-Auditor

SmartClaim-Auditor es una plataforma impulsada por inteligencia artificial diseñada para auditar reclamos de seguros y quejas de garantías. Utiliza un pipeline de múltiples capas que clasifica reclamos, recupera evidencia documental mediante RAG (Generación Aumentada por Recuperación) y ejecuta una auditoría a través de un grafo de razonamiento para emitir un veredicto fundamentado.

## Prerrequisitos

Para ejecutar este proyecto, asegúrese de contar con:
- Python 3.11 o superior.
- Node.js (se recomienda la última versión LTS).
- [uv](https://github.com/astral-sh/uv) para la gestión de dependencias de Python.
- [pnpm](https://pnpm.io/) para la gestión de paquetes del frontend.

## Instalación

El proyecto se divide en dos componentes principales: el backend y el frontend.

### Backend

1. Navegue al directorio del backend:
   ```bash
   cd backend
   ```
2. Instale las dependencias y configure el entorno virtual con `uv`:
   ```bash
   uv sync
   ```

### Frontend

1. Navegue al directorio del frontend:
   ```bash
   cd frontend
   ```
2. Instale las dependencias de Node:
   ```bash
   pnpm install
   ```

## Ejecución en local

Se requieren dos terminales separadas para ejecutar ambos servicios simultáneamente.

**Terminal 1: Backend**
```bash
cd backend
uv run uvicorn app.main:app --reload
```

**Terminal 2: Frontend**
```bash
cd frontend
pnpm dev
```

La interfaz web estará disponible en `http://localhost:3000` y la API del backend en `http://localhost:8000`.

## Estructura de carpetas

- `/backend`: Lógica central del sistema, API FastAPI, pipeline de LangGraph y base de datos.
- `/frontend`: Interfaz de usuario tipo consola/chat construida con Next.js 16.
- `/docs`: Documentación técnica extendida (arquitectura, guías de usuario y referencia de la API).