# 🤖 Curso de Agentes con LangGraph y RAG

¡Bienvenido! Este repositorio contiene los materiales de un curso para aprender a crear agentes de IA usando **LangGraph**, **LangChain** y técnicas como **RAG (Retrieval-Augmented Generation)**. Incluye notas detalladas, notebooks interactivos, código fuente y ejemplos prácticos, ideal para principiantes y desarrolladores que quieren profundizar en agentes inteligentes.

## 🎯 ¿Qué aprenderás?
- Construir agentes que piensan y actúan como humanos.
- Usar modelos de lenguaje (como Ollama) para generar respuestas inteligentes.
- Implementar RAG para que tus agentes "recuerden" información de documentos.
- Crear flujos de trabajo con grafos (como diagramas de flujo para código).

No necesitas ser un experto en programación; empezaremos desde lo básico.

## 📁 Estructura del Proyecto
Aquí tienes una visión general actualizada de cómo está organizado el repositorio para que sea fácil de seguir:

```
my_course_agent/
├── .langgraph_api/              # Archivos relacionados con la API de LangGraph (checkpoints, etc.)
├── agents/                      # Implementaciones de agentes y nodos de soporte
│   └── support/                 # Nodos y herramientas de soporte para agentes
├── notebooks/                   # Notebooks interactivos de Jupyter para lecciones
│   ├── .rag_index/              # Índices para RAG (Retrieval-Augmented Generation)
│   ├── faiss-e5-small/          # Índice FAISS para embeddings
│   ├── PDF/                     # Documentos PDF para ejemplos
│   └── *.ipynb                  # Notebooks de lecciones (01_introduccion_agentes_langgraph.ipynb, etc.)
├── notes/                       # Notas detalladas en Markdown para cada lección
│   └── *.md                     # Archivos como 01_introduccion_langgraph_agentes_ia.md, etc.
├── src/                         # Código fuente modular
│   ├── agents/                  # Módulos de agentes (booking.py, rag.py, etc.)
│   └── api/                     # Módulos de API
├── .gitignore                   # Archivos a ignorar en Git
├── .python-version              # Versión de Python especificada
├── langgraph.json               # Configuración de LangGraph
├── pyproject.toml               # Configuración del proyecto y dependencias
├── README.md                    # Este archivo (¡estás aquí!)
└── uv.lock                      # Lockfile para dependencias con `uv`
```

### Consejos para Navegar:
- **Empieza por `notes/`:** Lee las notas en orden (como 01_introduccion_langgraph_agentes_ia.md) para entender los conceptos teóricos.
- **Prueba en `notebooks/`:** Abre los notebooks en Jupyter (ej: 01_introduccion_agentes_langgraph.ipynb) para ejecutar código y ver resultados interactivos.
- **Explora `src/` y `agents/`:** Mira el código fuente y agentes cuando estés listo para detalles técnicos y ejemplos prácticos.
- **Usa `notebooks/PDF/` y `.rag_index/`:** Para ejemplos con documentos reales y RAG.

## 🚀 Inicio Rápido
Sigue estos pasos simples para configurar y empezar a experimentar:

1. **Instala Python (si no lo tienes):**
   - Descarga Python 3.11+ desde [python.org](https://www.python.org/downloads/).
   - Asegúrate de marcar "Add to PATH" durante la instalación.

2. **Instala uv (gestor de dependencias):**
   - Ejecuta: `pip install uv` en tu terminal.

3. **Instala dependencias del proyecto:**
   - Abre una terminal en la carpeta del proyecto.
   - Ejecuta: `uv sync` para instalar todo lo necesario según `pyproject.toml`.

4. **Ejecuta un ejemplo simple:**
   - Abre un notebook en `notebooks/` (ej: `01_introduccion_agentes_langgraph.ipynb`).
   - Sigue las instrucciones para ejecutar código y ver resultados interactivos.

5. **Opcional: Instala Ollama para modelos locales:**
   - Ve a [ollama.ai](https://ollama.ai) y descarga la versión para tu sistema.
   - Ejecuta: `ollama run llama3.2` para probar modelos de IA local.

## 🛠️ Herramientas Recomendadas
- **Jupyter Notebook:** Para ejecutar código interactivo (instálalo con `pip install jupyter`).
- **VS Code:** Editor gratuito con soporte para Python y notebooks.
- **Git:** Para versionar tu código (ya tienes un repo iniciado).

## 📚 Recursos Adicionales
- [Documentación de LangGraph](https://langgraph-ai.github.io/langgraph/): Para detalles avanzados.
- [Ollama Docs](https://github.com/ollama/ollama): Modelos locales fáciles.
- [Comunidad en Discord](https://discord.gg/langchain): Preguntas y ayuda.

## 🤝 Contribuciones
¡Este es un proyecto de aprendizaje! Si encuentras errores o mejoras, edita archivos y haz un commit. Recuerda: todos empezamos como principiantes.

¡Diviértete construyendo agentes inteligentes! Si tienes dudas, revisa las notas o abre un issue en GitHub.

