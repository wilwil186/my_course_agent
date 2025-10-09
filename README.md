# 🚀 Configuración del Proyecto con `uv` + LangGraph (arquitectura `src/`)

> Guía completa para levantar el entorno, instalar dependencias, compilar/instalar el proyecto y ejecutar tu agente.

---

## 🧩 Requisitos previos

- Python ≥ **3.11** (recomendado 3.13)  
- [Ollama](https://ollama.ai) corriendo localmente  
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) instalado  

---

## ⚙️ Instalar `uv` (una vez)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
uv --version
````

---

## 🧹 Limpiar entornos previos (pip/venv)

```bash
deactivate 2>/dev/null || true
rm -rf .venv
```

---

## 🏗️ Crear el entorno con `uv`

```bash
uv venv
# (opcional) fijar versión exacta de Python
# uv python pin 3.13
```

---

## 📦 Dependencias (producción)

```bash
uv add \
  "langgraph>=0.2.33" \
  "langgraph-api>=0.4.35" \
  "langchain>=0.3" \
  "langchain-core>=0.3" \
  "langchain-ollama>=0.1.0" \
  "pydantic<3" \
  "python-dotenv>=1.0"
```

---

## 🧰 Dependencias de desarrollo

```bash
uv add "langgraph-cli[inmem]" jupyter --dev
```

> Mantén separadas las dependencias de **producción** y **desarrollo** en tu `pyproject.toml`.

---

## 🔄 Sincronizar e instalar el proyecto (editable)

> Como usamos arquitectura `src/`, es importante **instalar el proyecto localmente** para que Python reconozca los paquetes (`agents`, `api`, etc.)

```bash
# sincroniza dependencias
uv sync

# instala el paquete local en modo editable
uv pip install -e .
```

---

## 🧠 Ejecutar el agente

```bash
# si el entrypoint está en src/agents/main.py (variable exportada: app)
uv run python -c "from agents.main import ask; print(ask('¿Cuál es el clima en Bogotá?'))"
```

### Interfaz visual (LangGraph Studio)

```bash
# requiere langgraph-cli (instalado arriba)
uv run langgraph dev
# o de forma temporal:
# uvx langgraph dev
```

---

## 🧪 Verificar el entorno

```bash
uv pip list
ollama run qwen2.5:7b-instruct
```

---

## 📂 Estructura recomendada del proyecto

```
.
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── main.py         # exporta 'app' (grafo principal)
│   └── api/
│       ├── __init__.py
│       └── server.py       # API para exponer el agente
│
├── notebooks/
│   └── grafo_visual.ipynb
│
├── .env
├── .gitignore
├── langgraph.json
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## 🧩 Configuración de LangGraph Studio

**Archivo `langgraph.json`:**

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agents/main.py:app"
  },
  "env": ".env"
}
```

> El campo `"agent"` apunta al grafo compilado `app` dentro de `src/agents/main.py`.

---

## 🧩 Variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
MODEL=qwen2.5:7b-instruct
OLLAMA_BASE_URL=http://localhost:11434
# LANGSMITH_API_KEY=...
# LANGCHAIN_TRACING_V2=false
```

Y cárgalas en el código con:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## ✅ Resumen de comandos clave

| Acción                         | Comando                    |
| ------------------------------ | -------------------------- |
| Crear entorno                  | `uv venv`                  |
| Añadir librería                | `uv add paquete`           |
| Añadir librerías de desarrollo | `uv add paquete --dev`     |
| Sincronizar entorno            | `uv sync`                  |
| **Instalar proyecto local**    | `uv pip install -e .`      |
| Ejecutar script                | `uv run python archivo.py` |
| Abrir LangGraph Studio         | `uv run langgraph dev`     |

---

## 🧰 `.gitignore` recomendado

```gitignore
# Python / uv
.venv/
.uv/
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
.eggs/
.build/
dist/
.cache/
uv.lock.lock

# Config local / credenciales
.env
.env.*
*.env
*.secret
*.secrets

# IDEs / editores
.vscode/
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json
.idea/
*.iml

# Notebooks
.ipynb_checkpoints/
*.ipynb_convert/
*.nbconvert/

# Logs
*.log
logs/
**/wandb/
**/mlruns/

# Datos / artefactos
data/
data_raw/
data_tmp/
data_cache/
outputs/
artifacts/
models/
checkpoints/
runs/

# SO
.DS_Store
Thumbs.db
```

---

## 🔍 Visualización de grafos

* En Jupyter o VSCode Notebook:

  ````python
  from agents.main import app
  mermaid = app.get_graph().draw_mermaid()

  from IPython.display import Markdown, display
  display(Markdown(f"```mermaid\n{mermaid}\n```"))
  ````

* Si tu entorno no soporta Mermaid:

  * [https://mermaidviewer.com/editor](https://mermaidviewer.com/editor)
  * [https://mermaid.live](https://mermaid.live)

---

## 🧵 Orquestación y depuración

LangGraph Studio permite abrir múltiples **threads** y visualizar cómo el grafo recorre los nodos (`ensure_input`, `agent`, `tools`, `END`), lo que facilita depurar conversaciones en paralelo.

---

## 🛠️ Troubleshooting

* **Error:** `Package 'langgraph' does not provide any executables`
  → Instala el CLI:

  ```bash
  uv add "langgraph-cli[inmem]" --dev
  ```

* **Error:** `ImportError: cannot import name 'agent' from 'main'`
  → En esta estructura, el grafo exportado se llama `app`.
  Usa:

  ```python
  from agents.main import app
  ```

* **Studio falla sin input**
  → Usa el nodo `ensure_input` que inyecta un mensaje “Hola” cuando LangGraph Studio llama sin mensajes previos.

---

## 📈 Próximos pasos

1. Exponer el grafo `app` con **FastAPI** en `src/api/server.py`.
2. Integrar métricas con **LangSmith** o **Prometheus**.
3. Crear notebooks de prueba e integración.
4. Desplegar la API en **Railway**, **Render** o **Fly.io**.

---

> 💡 Con esta guía tienes un entorno reproducible, modular y compatible con `LangGraph Studio`, gestionado con `uv`, y listo para escalar tu agente a producción.

