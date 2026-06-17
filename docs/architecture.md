# Arquitectura del Sistema

SmartClaim-Auditor utiliza una arquitectura cliente-servidor con un enfoque modular centrado en el procesamiento de lenguaje natural y motores de reglas aumentados por LLMs.

## Stack Tecnológico

- **Backend:** Python 3.11+, FastAPI (API REST síncrona), SQLModel (ORM), SQLite (Base de datos de desarrollo local), Torch y Transformers.
- **Flujo Lógico de IA:** LangGraph para la orquestación del grafo de razonamiento, FAISS para la indexación y búsqueda vectorial.
- **Frontend:** Next.js 16.2.9 (App Router), React 19, TypeScript, TailwindCSS v4, shadcn/ui.

## Las 5 Capas del Pipeline

1. **API Gateway:** Controlado por FastAPI, gestiona las peticiones HTTP de entrada, la serialización y validación de datos, y el enrutamiento.
2. **Classifier:** Un módulo ligero que identifica la intención principal del usuario a partir del texto de la queja para encaminar la lógica de análisis posterior.
3. **RAG (FAISS):** Recupera contexto relevante de un repositorio de manuales y pólizas indexados localmente en formato PDF para fundamentar sólidamente las decisiones de la IA.
4. **LangGraph (Auditoría):** Un grafo lineal y determinista que pasa por distintos nodos (`analyst`, `auditor`) para ponderar las cláusulas recuperadas frente a la situación descrita. Incorpora una compuerta estricta de validación de citas como control de veracidad (alucinaciones).
5. **Frontend (UI):** Una interfaz de usuario interactiva tipo consola (o entorno de chat) que expone el historial de evaluación, facilita la entrada de reclamos y visualiza la traza de razonamiento paso a paso.

## Flujo de Datos: Ciclo de Vida de un Reclamo

1. **Recepción:** El usuario envía el reclamo mediante el frontend, ingresando el texto descriptivo del incidente y, opcionalmente, una cláusula de referencia elegida del corpus.
2. **Contextualización:** El backend ejecuta una búsqueda de similitud en FAISS para recuperar los fragmentos más relevantes de los manuales almacenados (configurado mediante `RAG_TOP_K`).
3. **Análisis y Auditoría:** LangGraph toma los fragmentos recuperados y la queja original, pasando por un análisis de hechos y emitiendo un juicio técnico bajo reglas predefinidas.
4. **Validación de Citas:** Se verifica imperativamente que las citas referenciadas por la IA existan textualmente en los documentos recuperados o en las cláusulas provistas por el usuario. Si la cita es inválida o inventada, el veredicto desciende preventivamente a estado de inspección manual (`INSPECTION_REQUIRED`).
5. **Persistencia y Respuesta:** El resultado y la traza de ejecución se guardan en SQLite mediante SQLModel, y se expone de vuelta la traza completa al cliente web.

## Decisiones de Diseño Clave

- **Evolución de la UI a Consola/Chat:** El sistema evolucionó desde un formulario monolítico rígido hacia un modelo de interfaz tipo chat interactivo, reduciendo enormemente la fricción cognitiva y mejorando la asimilación al revelar los resultados del auditor progresivamente (staged reveal).
- **Opcionalidad de las Cláusulas de Contrato:** Se removió la barrera que obligaba a los usuarios a adjuntar manualmente la cláusula legal durante la creación del reclamo. Para compensar la menor certeza inicial, el sistema RAG aumentó su umbral de búsqueda (`TOP_K` de 2 a 4) y el frontend ahora ofrece un selector predictivo basado en un corpus estructurado. Esto garantiza que la herramienta sea amigable para operadores generales sin sacrificar rigor.
- **Fuente Única de Verdad (Backend-led):** En lugar de duplicar o sincronizar lógicas de corpus entre frontend y backend, el backend es el propietario absoluto y expone dinámicamente el listado de documentos indexados (`/api/documents`) y las cláusulas en formato JSON (`/api/clauses`), garantizando consistencia pura en toda la arquitectura.
