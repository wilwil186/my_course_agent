# Clase 8 — RAG con Herramientas Open Source (PDFs y Documentos)

**Objetivo:** Implementar un sistema RAG (Retrieval-Augmented Generation) completamente open source para consultar documentos como PDFs, usando herramientas locales como LangChain, FAISS y Ollama, sin depender de APIs propietarias. Esto permite control total, privacidad y cero costos variables.

---

## 🧠 ¿Qué problema resuelve?
Los LLMs estándar tienen limitaciones inherentes que RAG ayuda a superar, pero usando herramientas open source mantenemos todo local y gratuito.

- **Los LLM tienen una ventana de conocimiento limitada**: Están entrenados hasta una fecha fija y no acceden a datos privados o recientes. No "saben" sobre eventos actuales, documentos internos o conocimiento personalizado.
- **Con RAG open source puedes adjuntar documentos (p. ej., PDFs)** y hacer que el modelo **razone con ese contexto** para responder con más precisión, relevancia y actualización, todo en tu máquina.
- **Beneficio clave**: Combina el poder generativo del LLM con información externa, evitando "alucinaciones" (respuestas inventadas) y mejorando exactitud en tareas como soporte técnico, análisis de docs o preguntas sobre datos privados. Además, es 100% privado y escalable sin costos.

RAG transforma un LLM genérico en un experto en tu dominio específico, usando solo software open source.

---

## 🔑 Ideas clave
Conceptos fundamentales para entender y usar RAG efectivamente con herramientas open source.

- **Vector stores locales**: Almacenes de embeddings (representaciones vectoriales de texto) que permiten búsquedas semánticas rápidas. Usa FAISS (de Facebook) o Chroma para control total, corriendo en tu máquina.
- **Embeddings locales**: Calcula embeddings con modelos open source como `sentence-transformers` o Hugging Face, sin enviar datos a servidores externos.
- **Estrategia de contexto**: Para evitar costos altos y confusiones, envía **solo el último mensaje** del usuario al LLM junto con resultados de búsqueda. Si necesitas memoria conversacional, resume historial o usa un sistema separado.
- **Flujo típico**: Usuario pregunta → Cargar documentos → Calcular embeddings → Buscar en vector store → Inyectar resultados relevantes en prompt → LLM responde con contexto.

Esta aproximación es ideal para privacidad y control; escala fácilmente sin límites de proveedores.

---

## ✅ Requisitos
Antes de empezar, asegúrate de tener estos elementos listos (todo open source y gratuito).

- **Ollama corriendo localmente**: Para el LLM (ej. `qwen2.5:7b-instruct`). Descárgalo de ollama.ai e inicia con `ollama serve`.
- **PDFs listos para procesar**: Prepara documentos relevantes (ej. manuales, FAQs, reportes). Asegúrate de que sean texto legible (no imágenes escaneadas) y de tamaño razonable.
- **Dependencias open source**: Instala con `uv add langchain langchain-community langchain-ollama faiss-cpu sentence-transformers pypdf` (para PDFs).

Una vez listo, procesa documentos localmente sin subir nada a servidores externos.

---

## ⚙️ Preparación (Vector Store Local)
Configura un vector store local con FAISS para almacenar y buscar en tus documentos de manera privada.

1. **Instala dependencias**:
   ```bash
   uv add langchain-community faiss-cpu sentence-transformers pypdf
   ```
   - `langchain-community`: Para loaders de documentos.
   - `faiss-cpu`: Vector store open source (usa CPU; para GPU instala `faiss-gpu`).
   - `sentence-transformers`: Modelos de embeddings gratuitos (ej. `all-MiniLM-L6-v2`).
   - `pypdf`: Para cargar PDFs.

2. **Carga y procesa documentos**:
   ```python
   from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
   from langchain_text_splitters import RecursiveCharacterTextSplitter

   # Carga PDFs de un directorio (ajusta path)
   loader = DirectoryLoader("PDF", glob="**/*.pdf", loader_cls=PyPDFLoader)
   docs = loader.load()

   # Divide en chunks (trozos) para mejor búsqueda
   splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
   chunks = splitter.split_documents(docs)
   print(f"Cargados {len(chunks)} chunks de documentos.")
   ```

3. **Calcula embeddings y crea vector store**:
   ```python
   from langchain_community.vectorstores import FAISS
   from langchain_huggingface import HuggingFaceEmbeddings

   # Modelo de embeddings open source (descarga automáticamente)
   embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

   # Crea vector store local
   vectorstore = FAISS.from_documents(chunks, embeddings)
   vectorstore.save_local("faiss_index")  # Guarda en disco para reutilizar
   print("Vector store creado y guardado localmente.")
   ```

- **Consejo**: Empieza con pocos PDFs para pruebas; agrega más después.
- **Ventajas open source**: Todo corre en tu máquina; no hay límites de almacenamiento ni costos.
- **Carga desde guardado**: Para reutilizar: `vectorstore = FAISS.load_local("faiss_index", embeddings)`.

---

## 🧩 Invocación con RAG Local
Integra el vector store en tu LLM local para búsquedas automáticas en documentos.

### Crear un retriever
```python
# Carga vector store (asumiendo ya creado)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})  # Top 5 chunks relevantes

# Función para buscar contexto
def get_context(query: str) -> str:
    results = retriever.get_relevant_documents(query)
    return "\n".join([doc.page_content for doc in results])
```

### Invocar LLM con contexto
```python
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

# LLM local
llm = ChatOllama(model="qwen2.5:7b-instruct", temperature=0.3)

# Ejemplo de uso (sin grafo, directo)
user_input = "Explica el concepto de RAG en base a los documentos cargados."
context = get_context(user_input)
prompt = f"Contexto: {context}\nPregunta: {user_input}"
response = llm.invoke([HumanMessage(content=prompt)])
print(response.content)  # Respuesta con contexto de PDFs locales
```

- **Comportamiento esperado**:
  - Si la pregunta requiere contexto de PDF (ej. "Qué dice el doc sobre X?") → Busca en vector store local y usa resultados en respuesta.
  - Si es trivial (ej. "Hola") → Responde directo sin búsqueda, ahorrando recursos.
- **Por qué solo último mensaje**: Evita procesamiento excesivo; si necesitas historial, resume previamente.

Esta integración es privada y rápida: todo en tu máquina.

---

## 🛠️ Integración rápida en tu repo
Añade RAG a tu proyecto existente con pocos cambios, usando herramientas open source.

1. **Crea archivo `src/agents/rag.py`** (basado en tu `main.py`):
   - Carga documentos, crea vector store y función para consultar.
   ```python
   # Ejemplo mínimo (adapta de tu main.py)
   from dotenv import load_dotenv
   from langchain_ollama import ChatOllama
   from langchain_community.vectorstores import FAISS
   from langchain_huggingface import HuggingFaceEmbeddings
   from langchain_core.messages import HumanMessage

   load_dotenv()

   # Carga vector store (crea si no existe)
   embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
   vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

   retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
   llm = ChatOllama(model="qwen2.5:7b-instruct", temperature=0.3)

   def get_context(query: str) -> str:
       results = retriever.get_relevant_documents(query)
       return "\n".join([doc.page_content for doc in results])

   def ask_rag(text: str) -> str:
       context = get_context(text)
       prompt = f"Contexto: {context}\nPregunta: {text}"
       response = llm.invoke([HumanMessage(content=prompt)])
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
   - Envía preguntas como "Qué es LangGraph según los docs?" y ve cómo usa documentos locales.

> Tip: Usa **Ollama** para todo (LLM y embeddings) para mantenerlo 100% local y gratuito.

---

## 📏 Buenas prácticas / límites
Maximiza efectividad y evita problemas comunes con RAG open source.

- **Prototipado rápido y privado**: Ideal para casos sensibles (ej. documentos internos). Procesa localmente sin subir nada.
- **Más personalizable**: Controla embeddings, chunking y búsqueda; ajusta modelos según necesidades.
- **Límites de contexto**: Si necesitas historial largo, usa resúmenes (pide al LLM resumir conversación) o integra con memoria externa. Evita enviar historial completo para reducir recursos.
- **Otras prácticas**:
  - **Chunking**: Usa `RecursiveCharacterTextSplitter` para dividir documentos en trozos relevantes (ajusta `chunk_size` y `chunk_overlap`).
  - **Calidad**: Usa documentos limpios (texto, no imágenes); prueba búsquedas con `retriever.get_relevant_documents("query")`.
  - **Recursos**: Corre en CPU (más lento pero gratis); para velocidad, usa GPU si disponible.
  - **Privacidad**: Todo local; no hay datos enviados a terceros.

Para producción avanzada, escala con más documentos o integra búsquedas web open source.

---

## 🧪 Checklist de verificación
Asegúrate de que RAG funcione correctamente antes de usar.

- [ ] Dependencias instaladas: `langchain-community`, `faiss-cpu`, `sentence-transformers`, `pypdf`.
- [ ] Documentos cargados y vector store creado/guardado localmente (ej. en `faiss_index`).
- [ ] Retriever configurado y probado directamente (busca contexto relevante).
- [ ] LLM local (Ollama) integrado con contexto de búsqueda.
- [ ] Invocación usando contexto inyectado en prompt.
- [ ] Agente registrado en `langgraph.json` (ej. nuevo grafo "rag") y probado en Studio (preguntas responden con contexto de documentos).

Si todo está marcado, tienes RAG open source funcionando.

---

## 🔗 Lecturas recomendadas
- **LangChain RAG Guide**: python.langchain.com/docs/how_to/#qa-with-rag (para RAG avanzado open-source).
- **FAISS Documentation**: github.com/facebookresearch/faiss (vector store local).
- **Sentence Transformers**: huggingface.co/sentence-transformers (modelos de embeddings gratuitos).
- **Ollama para LLMs locales**: ollama.ai (ejecuta modelos open source en tu máquina).

---

## 🧭 Próximos pasos (opcional)
- **Añadir más documentos**: Carga más PDFs/TXT y reconstruye el vector store.
- **Mejorar búsqueda**: Integra reranking (ej. con `sentence-transformers` para reordenar resultados).
- **Conectar búsquedas web**: Usa herramientas open source como `langchain-community` para buscar en web (ej. DuckDuckGo).
- **Medir calidad**: Implementa métricas como precisión de recuperación y relevancia de respuestas.
- **Escalar**: Para grandes datasets, usa Chroma o Pinecone open source para vector stores más avanzados.

Este es un buen inicio 100% open source; escala según necesidades sin costos.
