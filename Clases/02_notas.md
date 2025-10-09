¡de una! Te dejo el **README de la Clase 2** (100% open-source) listo para pegar en tu repo del curso dentro de `clases/` como `02_Notas.md`. Lo basé en cómo ya montaste tu repo `my_course_agent` (estructura `src/`, `langgraph.json`, uso de Ollama y `uv`) para que todo corra tal cual en local. Referencio dónde ya tienes cada cosa. ([GitHub][1])

---

````markdown
# ⚙️ Clase 2: Configuración de entorno Python y tu primer agente (100% Open Source)

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Dejar listo tu entorno con `uv` + `Ollama` + `LangGraph` (arquitectura `src/`) y levantar un agente mínimo que podrás debuggear en **LangGraph Studio**, sin depender de APIs cerradas.

---

## 🧩 Qué aprenderás
- Crear y **aislar el entorno** con `uv`.
- Instalar dependencias abiertas: `langgraph`, `langchain`, `langchain-ollama`.
- Usar **Ollama** para correr modelos locales (ej. `qwen2.5:7b-instruct`).
- Exportar un **grafo `app`** y abrirlo en **LangGraph Studio**.
- Buenas prácticas con `.env` y arquitectura `src/`.

> Nota: Tu repo ya sigue este enfoque (estructura `src/`, `langgraph.json`, variables `MODEL` y `OLLAMA_BASE_URL`). Si sigues estas notas, todo encaja con lo que ya tienes. :contentReference[oaicite:1]{index=1}

---

## ✅ Requisitos
- **Python ≥ 3.11** (recomendado 3.13)
- **Ollama** corriendo localmente (para modelos open-source)
- **uv** instalado (gestiona venv y dependencias)

Instala `uv` una vez:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
uv --version
````

> En tu README ya tienes estos pasos y comandos útiles para `uv`. ([GitHub][1])

---

## 🧱 Crear el entorno y dependencias

1. **Venv** con `uv`:

```bash
uv venv
# (opcional) fijar versión exacta de Python
# uv python pin 3.13
```

2. **Dependencias de producción**:

```bash
uv add \
  "langgraph>=0.2" \
  "langchain>=0.3" \
  "langchain-core>=0.3" \
  "langchain-ollama>=0.3" \
  "pydantic<3" \
  "python-dotenv>=1.0"
```

3. **Dependencias de desarrollo** (Studio + Jupyter):

```bash
uv add "langgraph-cli[inmem]" jupyter --dev
```

4. **Sincroniza e instala el paquete local (arquitectura `src/`)**:

```bash
uv sync
uv pip install -e .
```

> Este flujo (sync + editable) es clave con `src/` para que `agents.main` se resuelva bien. Lo documentaste ya en tu README. ([GitHub][1])

---

## 🔑 Variables de entorno (`.env`)

Crea un `.env` en la raíz:

```env
MODEL=qwen2.5:7b-instruct
OLLAMA_BASE_URL=http://localhost:11434
# LANGSMITH_API_KEY=...
# LANGCHAIN_TRACING_V2=false
```

> Coincide con tu configuración actual y con la guía de Ollama/LangChain para correr modelos locales. ([GitHub][1])

---

## 🗂️ Configuración de LangGraph Studio (`langgraph.json`)

Tu archivo debe apuntar al **grafo exportado `app`** dentro de `src/agents/main.py`:

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agents/main.py:app"
  },
  "env": ".env"
}
```

> Este mapping ya lo tienes tal cual en tu repo. ([GitHub][1])

---

## 🤖 Código base de tu primer agente (open-source)

Archivo: `src/agents/main.py`

```python
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, MessagesState, START, END

# 1) Cargar .env
load_dotenv()

# 2) Instanciar LLM local vía Ollama (100% open source)
#    Usa variables MODEL y OLLAMA_BASE_URL desde el .env
llm = ChatOllama()

# 3) Nodo que llama al modelo
def call_model(state: MessagesState):
    """Recibe la lista de mensajes y devuelve la respuesta del LLM."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 4) Definir el grafo de LangGraph
builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_edge(START, "model")
builder.add_edge("model", END)

# 5) Compilar el grafo
app = builder.compile()

# 6) Helper para invocar en código/CLI
def ask(text: str) -> str:
    messages: List[BaseMessage] = [
        SystemMessage(content="Eres un asistente útil que contesta de forma breve y clara."),
        HumanMessage(content=text),
    ]
    result = app.invoke({"messages": messages})
    return result["messages"][-1].content
```

* Este patrón **MessagesState + un nodo** es el “hola mundo” recomendado en la doc oficial de LangGraph. Luego podrás añadir ramas, herramientas, memoria, etc. ([LangChain Docs][2])
* `ChatOllama` viene de `langchain-ollama` (paquete oficial) y te conecta a cualquier modelo local de Ollama respetando `MODEL` y `OLLAMA_BASE_URL`. ([LangChain][3])

---

## ▶️ Ejecutar y probar

**Desde Python/CLI**:

```bash
uv run python -c "from agents.main import ask; print(ask('¿Cuál es el clima en Bogotá?'))"
```

**Abrir LangGraph Studio** (modo visual para debug):

```bash
uv run langgraph dev
# o temporalmente:
# uvx langgraph dev
```

* Verás el grafo `agent` y podrás enviar mensajes. Si Studio llama sin input, puedes añadir más adelante un nodo `ensure_input` que inyecte un “Hola” por defecto (lo documentaste en tu README). ([GitHub][1])

---

## 🧪 Verificaciones rápidas

```bash
uv pip list
ollama run qwen2.5:7b-instruct   # prueba el modelo directo en Ollama
```

> Guía oficial de integración con Ollama en LangChain (instalación/uso). ([LangChain][4])

---

## 🛠️ Troubleshooting

* **`Package 'langgraph' does not provide any executables`**
  Instala el CLI:
  `uv add "langgraph-cli[inmem]" --dev`  ([GitHub][1])

* **`ImportError: cannot import name 'app'`**
  Asegúrate de exportar `app` en `src/agents/main.py` tal como arriba y que tu `langgraph.json` apunte a `./src/agents/main.py:app`. ([GitHub][1])

* **El modelo no existe en Ollama**
  Ejecuta `ollama pull qwen2.5:7b-instruct` o el modelo que quieras y (opcional) valida en init con `validate_model_on_init=True`. ([LangChain][5])

---

## 📚 Recursos abiertos

* **LangGraph – Overview & Graph API** (StateGraph, START/END, ejemplos) ([LangChain Docs][2])
* **LangChain + Ollama** (integración oficial y guía de instalación) ([LangChain][4])

---

## ✅ Checklist de esta clase

* [ ] `uv venv` creado y activo
* [ ] Dependencias instaladas (`langgraph`, `langchain`, `langchain-ollama`, CLI dev)
* [ ] `.env` con `MODEL` y `OLLAMA_BASE_URL`
* [ ] `src/agents/main.py` exporta `app` y función `ask`
* [ ] `langgraph.json` apunta a `./src/agents/main.py:app`
* [ ] `uv run langgraph dev` abre Studio y responde

**Siguiente clase →** añadiremos **herramientas (tools)** al agente y un **branching** básico en el grafo.

```

---

¿Lo pego también como `clases/02_Notas.md` y te propongo el `main.py` exacto según tu árbol actual? Si quieres, te lo adapto a tus nombres de paquete/funciones (por ejemplo, si ya tienes `ensure_input` o un `ask()` distinto).
::contentReference[oaicite:15]{index=15}
```

[1]: https://github.com/wilwil186/my_course_agent "GitHub - wilwil186/my_course_agent"
[2]: https://docs.langchain.com/oss/python/langgraph/overview?utm_source=chatgpt.com "LangGraph Overview - Docs by LangChain"
[3]: https://python.langchain.com/docs/integrations/llms/ollama/?utm_source=chatgpt.com "OllamaLLM"
[4]: https://python.langchain.com/docs/integrations/providers/ollama/?utm_source=chatgpt.com "Ollama"
[5]: https://python.langchain.com/api_reference/ollama/?utm_source=chatgpt.com "langchain-ollama: 0.3.8"
