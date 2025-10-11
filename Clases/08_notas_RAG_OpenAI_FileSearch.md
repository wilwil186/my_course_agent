# Clase 8 — RAG con OpenAI *File Search* (PDFs)

**Objetivo:** Implementar un RAG sencillo para consultar **PDFs** con la *tool* **file search** de OpenAI, sin montar tu propia base vectorial.

---

## 🧠 ¿Qué problema resuelve?
- Los LLM tienen una **ventana de conocimiento limitada** (no “saben” lo más reciente ni tu info privada).
- Con **RAG** puedes **adjuntar documentos** (p. ej., PDFs) y hacer que el modelo **razone con ese contexto** para responder con más precisión.

---

## 🔑 Ideas clave
- **Vector stores**: almacenes de embeddings (OpenAI ofrece uno listo).
- **file search**: *tool* del proveedor que permite **buscar semánticamente** dentro de tus PDFs.
- **Estrategia de contexto**: enviar **solo el último mensaje** al LLM para evitar errores por historiales largos (o resumir si necesitas memoria).

---

## ✅ Requisitos
- Cuenta y **API Key** de OpenAI.
- Proyecto creado en la plataforma.
- PDFs listos para subir.

---

## ⚙️ Preparación (Vector Store)
1. En **OpenAI → Storage → Vector stores**, crea uno (ej. `my-docs`).
2. **Sube** tus PDFs.
3. Copia el **`vector_store_id`** (lo usarás desde el código).

---

## 🧩 Invocación con *file search*
- Define la *tool* con tus `vector_store_ids`.
- Instancia el LLM **de OpenAI** (esta *tool* es específica del proveedor).
- Envía **solo el último mensaje** del usuario al invocar.

```python
# IDs de tus vector stores
vector_store_ids = ["vs_XXXXXXXX"]

tools = [
    {"type": "file_search", "vector_store_ids": vector_store_ids}
]

# Ejemplo de invocación (esquemático)
llm = LLM(provider="openai", tools=tools)

last_message = history[-1].text  # o un resumen si necesitas memoria
response = llm.invoke(user_input=last_message)
print(response)
```

**Comportamiento esperado**
- Si la pregunta requiere contexto de PDF → el modelo **usa la tool**.
- Si es trivial → **responde directo** sin llamar a la tool.

---

## 🛠️ Integración rápida en tu repo
1. **Crea** `src/agents/rag.py` (partiendo de tu `simple`):
   - Carga `.env`, instancia LLM de OpenAI con `tools=[file_search]`.
   - Recibe prompt y **pasa solo el último mensaje**.
2. **Registra** el agente en `langgraph.json` (ej. `"RAG": "./src/agents/rag.py:app"`).
3. **Reinicia** `langgraph dev` y prueba en la UI de chat.

> Tip: mantén **Qwen/Ollama** para tus agentes locales y usa **OpenAI** solo para este flujo de *file search*.

---

## 📏 Buenas prácticas / límites
- **Prototipado rápido**: ideal para *PoC* y *first use-cases* (p. ej., soporte con manuales PDF).
- **Menos personalizable** que un RAG propio (Chroma, PGVector, MongoDB+embeddings, etc.).
- Si necesitas **historial largo**, usa **resúmenes** o pasa a un **RAG más avanzado** (memoria + herramientas adicionales).

---

## 🧪 Checklist de verificación
- [ ] Vector store creado y **PDFs subidos**  
- [ ] `vector_store_id` copiado  
- [ ] LLM de **OpenAI** configurado con *file search*  
- [ ] Invocación usando **solo el último mensaje**  
- [ ] Agente **registrado** en `langgraph.json` y probado en la UI  

---

## 🔗 Lecturas recomendadas
- Documentación de **Agents** (OpenAI): https://platform.openai.com/docs/guides/agents

---

## 🧭 Próximos pasos (opcional)
- Añadir **varios PDFs** y probar recuperación por secciones.
- Conectar **APIs externas** (ej., web search) para complementar contenido.
- Medir calidad: **fuentes citadas**, *chunking*, *reranking*.
