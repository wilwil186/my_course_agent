# 🤖 Curso de Agentes con LangGraph y RAG

¡Bienvenido! Este repositorio es una guía práctica y paso a paso para aprender a construir agentes inteligentes usando **LangGraph** y **RAG (Retrieval-Augmented Generation)**. Está diseñado especialmente para principiantes, con explicaciones simples, ejemplos prácticos y notebooks interactivos.

## 🎯 ¿Qué aprenderás?
- Construir agentes que piensan y actúan como humanos.
- Usar modelos de lenguaje (como Ollama) para generar respuestas inteligentes.
- Implementar RAG para que tus agentes "recuerden" información de documentos.
- Crear flujos de trabajo con grafos (como diagramas de flujo para código).

No necesitas ser un experto en programación; empezaremos desde lo básico.

## 📁 Estructura del Proyecto
Aquí tienes una visión general de cómo está organizado el repositorio para que sea fácil de seguir:

```
my_course_agent/
├── src/                          # Código fuente del proyecto
│   ├── agents/                   # Agentes principales (ej: main.py, rag.py)
│   └── api/                      # APIs para conectar el agente
├── notes/                        # Notas y lecciones en español
│   ├── 01_notas.md              # Introducción básica
│   ├── 02_notas.md              # ...
│   └── ...                       # Más lecciones paso a paso
├── notebooks/                    # Notebooks interactivos de Jupyter
│   ├── 01_noootbook.ipynb       # Ejemplos simples
│   ├── 02_simple.ipynb          # ...
│   └── ...                       # Experimentos con código
├── data/                         # Archivos de datos (ej: PDFs para RAG)
│   └── 9587014499.PDF           # Documento de ejemplo
├── scripts/                      # Scripts útiles
│   └── build_index.py           # Para construir índices de búsqueda
├── .gitignore                   # Archivos a ignorar en Git
├── README.md                    # Este archivo (¡estás aquí!)
└── uv.lock                      # Gestión de dependencias con `uv`
```

### Consejos para Navegar:
- **Empieza por `notes/`:** Lee las notas en orden (01, 02, etc.) para entender los conceptos.
- **Prueba en `notebooks/`:** Abre los notebooks en Jupyter para ejecutar código y ver resultados.
- **Explora `src/`:** Mira el código fuente cuando estés listo para detalles técnicos.
- **Usa `data/`:** Para ejemplos con documentos reales.

## 🚀 Inicio Rápido
Sigue estos pasos simples para configurar y empezar a experimentar:

1. **Instala Python (si no lo tienes):**
   - Descarga Python 3.11+ desde [python.org](https://www.python.org/downloads/).
   - Asegúrate de marcar "Add to PATH" durante la instalación.

2. **Instala Ollama (para modelos de IA local):**
   - Ve a [ollama.ai](https://ollama.ai) y descarga la versión para tu sistema.
   - Ejecuta: `ollama run llama3.2` (o el modelo que prefieras) para probar.

3. **Instala dependencias:**
   - Abre una terminal en la carpeta del proyecto.
   - Ejecuta: `pip install uv` (o sigue la guía en las notas para más detalles).
   - Luego: `uv sync` para instalar todo lo necesario.

4. **Ejecuta un ejemplo simple:**
   - Abre un notebook en `notebooks/` (ej: `01_simple.ipynb`).
   - Sigue las instrucciones para hacer preguntas a tu agente.

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

