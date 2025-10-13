# Clase 8 — RAG con OpenAI *File Search* (PDFs)

**Objetivo:** Implementar un RAG sencillo para consultar **PDFs** con la *tool* **file search** de OpenAI, sin montar tu propia base vectorial.

---

## 🧠 ¿Qué problema resuelve?
Los LLMs estándar tienen limitaciones inherentes que RAG ayuda a superar.

- **Los LLM tienen una ventana de conocimiento limitada**: Están entrenados hasta una fecha fija (ej. GPT-4 hasta 2023) y no acceden a datos privados o recientes. No "saben" sobre eventos actuales, documentos internos o conocimiento personalizado.
- **Con RAG (Retrieval-Augmented Generation) puedes adjuntar documentos (p. ej., PDFs)** y hacer que el modelo **razone con ese contexto** para responder con más precisión, relevancia y actualización.
- **Beneficio clave**: Combina el poder generativo del LLM con información externa, evitando "alucinaciones" (respuestas inventadas) y mejorando exactitud en tareas como soporte técnico, análisis de docs o preguntas sobre datos privados.

RAG transforma un LLM genérico en un experto en tu dominio específico.

---

## 🔑 Ideas clave
Conceptos fundamentales para entender y usar RAG efectivamente.

- **Vector stores**: Almacenes de embeddings (representaciones vectoriales de texto) que permiten búsquedas semánticas rápidas. OpenAI proporciona uno gestionado, pero puedes usar open-source como FAISS o Chroma para control total.
- **file search**: Herramienta específica de OpenAI que integra búsquedas en vector stores con el LLM. Cuando el usuario pregunta, el modelo "busca" en tus documentos y usa resultados como contexto para responder.
- **Estrategia de contexto**: Para evitar costos altos y confusiones, envía **solo el último mensaje** del usuario al LLM junto con resultados de búsqueda. Si necesitas memoria conversacional, resume historial o usa un sistema separado.
- **Flujo típico**: Usuario pregunta → Buscar en vector store → Inyectar resultados relevantes en prompt → LLM responde con contexto.

Esta aproximación es rápida para prototipos, pero para producción avanzada considera RAG propio con embeddings locales.

---

## ✅ Requisitos
Antes de empezar, asegúrate de tener estos elementos listos.

- **Cuenta y API Key de OpenAI**: Necesaria para usar file search. Crea cuenta en platform.openai.com si no tienes, y genera una API key en el dashboard (guárdala en `.env` como `OPENAI_API_KEY`).
- **Proyecto creado en la plataforma de OpenAI**: Ve a platform.openai.com, crea un proyecto nuevo (gratuito para empezar) y copia el Project ID si lo necesitas (aunque para file search básico no es esencial).
- **PDFs listos para subir**: Prepara documentos relevantes (ej. manuales, FAQs, reportes). Asegúrate de que sean texto legible (no imágenes escaneadas) y de tamaño razonable (<100MB por archivo para límites iniciales).

Una vez listo, puedes subir PDFs directamente desde el código o el dashboard.

---

## ⚙️ Preparación (Vector Store)
Configura el vector store en OpenAI para almacenar y buscar en tus documentos.

1. **Accede al dashboard**: Ve a platform.openai.com → Storage → Vector stores (o busca "Vector stores" en la barra lateral).
2. **Crea un vector store nuevo**: Haz clic en "Create vector store", nómbralo (ej. `my-docs` para documentos del curso) y selecciona configuración básica (OpenAI maneja embeddings automáticamente).
3. **Sube tus PDFs**: En el vector store creado, usa "Upload files" para subir documentos. OpenAI procesa y crea embeddings (puede tomar minutos para archivos grandes).
4. **Copia el `vector_store_id`**: Una vez subido, ve a los detalles del vector store y copia el ID (formato: `vs_xxxxxxxx`). Lo necesitarás en el código para conectar.

- **Consejo**: Empieza con pocos PDFs para pruebas; agrega más después.
- **Límites**: Revisa quotas en tu plan (ej. almacenamiento gratis limitado).
- **Alternativa open-source**: Si prefieres control total, usa librerías como LangChain + FAISS para vector stores locales (tema para clases futuras).

---

## 🧩 Invocación con *file search*
Integra file search en tu LLM para búsquedas automáticas en documentos.

### Definir la tool
```python
# IDs de tus vector stores (copia de dashboard)
vector_store_ids = ["vs_XXXXXXXX"]  # Reemplaza con tu ID real

# Definir tools para el LLM
tools = [
    {
        "type": "file_search",
        "vector_store_ids": vector_store_ids
    }
]

# Instancia LLM de OpenAI con tools
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="gpt-4o-mini",  # O el modelo que uses
    tools=tools
)
```

### Invocar con contexto
```python
# Ejemplo de uso (sin grafo, directo)
from langchain_core.messages import HumanMessage

# Envía solo el último mensaje (para simplicidad)
user_input = "Explica el concepto de RAG en base a los documentos subidos."
response = llm.invoke([HumanMessage(content=user_input)])
print(response.content)  # Respuesta con contexto de PDFs
```

- **Comportamiento esperado**:
  - Si la pregunta requiere contexto de PDF (ej. "Qué dice el doc sobre X?") → El modelo llama a la tool automáticamente, busca en vector store y usa resultados en respuesta.
  - Si es trivial (ej. "Hola") → Responde directo sin tool, ahorrando costos.
- **Por qué solo último mensaje**: Evita tokens excesivos; si necesitas historial, resume previamente.

Esta integración es automática: el LLM decide cuándo usar la tool basado en la consulta.

---

## 🛠️ Integración rápida en tu repo
Añade RAG a tu proyecto existente con pocos cambios.

1. **Crea archivo `src/agents/rag.py`** (basado en tu `main.py`):
   - Carga `.env` e instancia LLM de OpenAI con `tools=[file_search]`.
   - Función que recibe texto, pasa solo el último mensaje al LLM y devuelve respuesta.
   ```python
   # Ejemplo mínimo (adapta de tu main.py)
   from dotenv import load_dotenv
   from langchain_openai import ChatOpenAI
   from langchain_core.messages import HumanMessage

   load_dotenv()
   vector_store_ids = ["vs_XXXXXXXX"]  # Tu ID
   tools = [{"type": "file_search", "vector_store_ids": vector_store_ids}]
   llm = ChatOpenAI(model="gpt-4o-mini", tools=tools)

   def ask_rag(text: str) -> str:
       response = llm.invoke([HumanMessage(content=text)])
       return response.content

   # Para grafo (opcional)
   # ... (usa como nodo en StateGraph)
   ```

2. **Registra en `langgraph.json`** (agrega entrada):
   ```json
   {
     "dependencies": ["."],
     "graphs": {
       "agent": "./src/agents/main.py:app",
       "rag": "./src/agents/rag.py:ask_rag"  # O app si usas grafo
     },
     "env": ".env"
   }
   ```

3. **Reinicia y prueba en Studio**:
   - Corre `uv run langgraph dev`.
   - Selecciona el grafo "rag" en Studio.
   - Envía preguntas como "Qué es LangGraph según los docs?" y ve cómo usa PDFs.

> Tip: Usa **Ollama** para agentes locales (gratis) y **OpenAI** solo para RAG con file search. Cambia `PROVIDER` en `.env` según tarea.

---

## 📏 Buenas prácticas / límites
Maximiza efectividad y evita problemas comunes con RAG.

- **Prototipado rápido**: Ideal para PoCs y casos iniciales (ej. chatbot de soporte con manuales PDF). Sube docs, configura tool y listo.
- **Menos personalizable**: OpenAI maneja embeddings y búsqueda; no controlas detalles como chunking o reranking. Para customización, usa RAG propio (ej. LangChain + Chroma).
- **Límites de contexto**: Si necesitas historial largo, usa resúmenes (pide al LLM resumir conversación) o integra con memoria externa. Evita enviar historial completo para reducir costos.
- **Otras prácticas**:
  - **Chunking**: OpenAI chunk automaticamente; para control, preprocesa PDFs en texto pequeño.
  - **Calidad**: Usa PDFs limpios (texto, no imágenes); prueba búsquedas manuales en dashboard.
  - **Costos**: Monitorea uso (cada búsqueda consume tokens); optimiza con filtros o resúmenes.
  - **Privacidad**: Datos en OpenAI (revisa políticas); para sensible, usa vector stores locales.

Para producción avanzada, evoluciona a RAG híbrido (local + API).

---

## 🧪 Checklist de verificación
Asegúrate de que RAG funcione correctamente antes de usar.

- [ ] Vector store creado en OpenAI dashboard y PDFs subidos/procesados.
- [ ] `vector_store_id` copiado y configurado en código (ej. en `tools`).
- [ ] LLM de OpenAI instanciado con `tools=[file_search]` y probado directamente.
- [ ] Invocación usando solo el último mensaje (o resumen si necesitas contexto).
- [ ] Agente registrado en `langgraph.json` (ej. nuevo grafo "rag") y probado en Studio (preguntas responden con contexto de PDFs).

Si todo está marcado, tienes RAG básico funcionando.

---
## 🔗 Lecturas recomendadas
- **Documentación de Agents (OpenAI)**: platform.openai.com/docs/guides/agents (guías oficiales para file search y tools).
- **LangChain RAG Guide**: python.langchain.com/docs/how_to/#qa-with-rag (para RAG avanzado open-source).
- **Vector Stores Open-Source**: github.com/facebookresearch/faiss (FAISS para búsquedas locales).

---
## 🧭 Próximos pasos (opcional)
- **Añadir varios PDFs**: Sube más documentos y prueba recuperación semántica (ej. preguntas sobre secciones específicas).
- **Conectar APIs externas**: Integra web search (ej. Tavily) como tool adicional para info reciente.
- **Medir calidad**: Implementa métricas como fuentes citadas, precisión de chunking y reranking para mejorar respuestas.
- **Evolucionar a RAG propio**: Usa LangChain + Chroma para control total (embeddings locales, filtros custom).

Este es un buen inicio; escala según necesidades.
