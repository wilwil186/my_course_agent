¡listo! Aquí tienes el archivo para tu repo, como
📄 `clases/03_Notas.md`

---

````markdown
# ⚙️ Clase 3: Configuración de **uv** para escalar agentes de IA en producción

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Pasar de prototipos sueltos a un **proyecto escalable**: aislar entornos, separar dependencias **prod/dev**, ordenar el repo, habilitar **LangGraph Studio** y **notebooks** para depuración y visualización.

---

## 🧩 ¿Por qué `uv`?
- **Unifica** lo que antes hacías con `pip`, `virtualenv`, `pip-tools`, `poetry`.
- **Aísla** entornos y **acelera** instalaciones (muy rápido).
- Usa un **`pyproject.toml`** estándar y genera **`uv.lock`** para reproducibilidad.
- Facilita separar **producción** de **desarrollo** (dependency groups).

---

## ✅ Requisitos
- Python **≥ 3.11** (recomendado 3.13)
- `uv` instalado
- (Opcional) **Ollama** para correr modelos locales
- Tu repo con arquitectura `src/` (como en la clase 2)

**Instalar `uv` (una vez):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
uv --version
````

---

## 🗂️ Inicializar proyecto y archivos base

> Si ya tienes proyecto, **no borres nada**; usa esto como guía para consolidar.

1. **Inicializa** (si empiezas de cero):

```bash
uv init
```

Esto crea:

* `pyproject.toml` (metadatos del proyecto + dependencias)
* `.gitignore` (puedes ampliarlo)
* Estructura básica

2. **.gitignore** recomendado (añade):

```
# entornos y caches
.venv/
__pycache__/
.ipynb_checkpoints/
# llaves/secrets
.env
.env.*
# sistema
.DS_Store
# langgraph (si genera carpeta local)
.langgraph/
```

> **No ignores** `uv.lock`: conviene **committearlo** para builds reproducibles.

---

## 🧱 Estructura sugerida del repo

Manteniendo tu enfoque `src/` y pensando en escalar:

```
repo/
├─ pyproject.toml
├─ uv.lock
├─ langgraph.json
├─ .env.example
├─ .gitignore
├─ clases/
│  ├─ 01_Notas.md
│  └─ 02_Notas.md
├─ src/
│  ├─ agents/
│  │  ├─ __init__.py
│  │  └─ main.py          # exporta `app` (LangGraph)
│  ├─ tools/
│  │  ├─ __init__.py
│  │  └─ weather.py       # ejemplo de tool
│  ├─ api/
│  │  ├─ __init__.py
│  │  └─ http.py          # (FastAPI) expone el agente
│  └─ config/
│     ├─ __init__.py
│     └─ settings.py      # lectura de .env
└─ notebooks/
   └─ 01_sanity_check.ipynb
```

> Asegúrate de tener **`__init__.py`** en cada subcarpeta de `src/` para que Python las trate como **paquetes**.

---

## 📦 Dependencias: prod vs dev

### `pyproject.toml` (ejemplo)

```toml
[project]
name = "my-course-agent"
version = "0.1.0"
description = "Agentes de IA con LangGraph (open source)"
readme = "README.md"
requires-python = ">=3.11"

# Dependencias de PRODUCCIÓN
dependencies = [
    "langgraph>=0.2",
    "langchain>=0.3",
    "langchain-core>=0.3",
    "langchain-ollama>=0.3",
    "python-dotenv>=1.0"
]

[dependency-groups]
# Dependencias de DESARROLLO (no se empaquetan en prod)
dev = [
    "langgraph-cli[inmem]",
    "jupyter",
    "ipykernel",
    "ruff",
    "pytest"
]
```

### Comandos útiles con `uv`

* Agregar deps de **producción**:

  ```bash
  uv add "langgraph>=0.2" "langchain>=0.3" "langchain-ollama>=0.3" "python-dotenv>=1.0"
  ```
* Agregar deps de **desarrollo**:

  ```bash
  uv add "langgraph-cli[inmem]" jupyter ipykernel ruff pytest --dev
  ```
* **Sincronizar** e instalar:

  ```bash
  uv sync
  ```
* **Modo editable** para `src/` (si aún no lo hiciste):

  ```bash
  uv pip install -e .
  ```

---

## 🔑 Variables de entorno (`.env`)

Crea `.env` en la raíz (y un `.env.example` sin claves reales):

```env
# Modelo local con Ollama (open source)
MODEL=qwen2.5:7b-instruct
OLLAMA_BASE_URL=http://localhost:11434

# Observabilidad (opcional)
LANGCHAIN_TRACING_V2=false
```

---

## 🧭 LangGraph Studio y ejecución

### `langgraph.json` (ejemplo)

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agents/main.py:app"
  },
  "env": ".env"
}
```

### Correr en **Studio** (debug visual):

```bash
uv run langgraph dev
# Opcional: especificar puerto
# uv run langgraph dev --port 2024
```

* Crea un **thread** nuevo y prueba con un “hola”.
* Si el puerto está ocupado: cierra el proceso previo o usa otro `--port`.

### Ejecutar sin Studio:

```bash
uv run python -c "from agents.main import ask; print(ask('Ping de salud?'))"
```

---

## 📒 Notebooks (Jupyter)

1. Instala kernel para este entorno:

```bash
uv run python -m ipykernel install --user --name my-course-agent
```

2. En el notebook, selecciona kernel **my-course-agent**.
3. Si reorganizas paquetes y falla un import:

   * Reinicia kernel.
   * Asegura `uv pip install -e .`.
   * Verifica `__init__.py` en los paquetes.

---

## 🌐 Exponer API (FastAPI minimal)

Archivo: `src/api/http.py` (opcional para producción)

```python
from fastapi import FastAPI
from pydantic import BaseModel
from agents.main import ask  # tu helper

app = FastAPI()

class Query(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/ask")
def ask_route(q: Query):
    return {"answer": ask(q.text)}
```

Ejecutar local:

```bash
uv run uvicorn api.http:app --reload --port 8000
```

---

## 🔍 Visualización de grafos

* En Studio verás el **trazo** (trace) del flujo.
* Si exportas el grafo a **Mermaid**/DOT (según tu helper), pega el resultado en un editor de Mermaid para renderizarlo.
* Útil cuando tengas **múltiples nodos/ramas**.

---

## 🛠️ Troubleshooting

* **`ModuleNotFoundError`**: faltan `__init__.py` o no instalaste `-e .`.
* **Puerto ocupado**: `pkill -f "langgraph"` o usa `--port` distinto.
* **Kernel no aparece**: reinstala `ipykernel` y el kernel del proyecto.
* **Ollama no responde**: verifica `ollama serve`, `OLLAMA_BASE_URL` y `ollama pull <modelo>`.

---

## 📚 Lecturas recomendadas (abierto)

* **uv** (gestor de paquetes y entornos)
* **LangGraph – conceptos y API de grafos**
* **Extensión Jupyter** (VS Code)

*(Evito enlaces cerrados; puedes buscar estos recursos por nombre en sus sitios oficiales.)*

---

## ✅ Checklist de la clase

* [ ] `pyproject.toml` con **prod** y **dev** separados
* [ ] `uv.lock` committeado
* [ ] `.env` y `.env.example` listos
* [ ] `src/agents/main.py` exporta `app` (LangGraph)
* [ ] `langgraph.json` apunta a `./src/agents/main.py:app`
* [ ] `uv run langgraph dev` abre Studio y responde
* [ ] (Opcional) `src/api/http.py` sirve `/ask` y `/health`

**Siguiente clase →** añadir **tools** (herramientas), control de **estado** y **ramas** (branching) para comportamientos más inteligentes.

```

---
::contentReference[oaicite:0]{index=0}
```
