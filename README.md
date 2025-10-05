# 🚀 Configuración del Proyecto con `uv` + LangGraph

> _Guía completa para levantar tu entorno, instalar dependencias y ejecutar tu agente._

---

## 🧩 Requisitos previos

- Python ≥ **3.11** (recomendado 3.13)  
- [Ollama](https://ollama.ai) corriendo localmente  
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) instalado  

---

## ⚙️ Instalación de `uv` (solo una vez)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
uv --version
````

---

## 🧹 Eliminar entornos antiguos (de pip o venv)

Si ya habías usado `pip` o `virtualenv`:

```bash
deactivate 2>/dev/null || true
rm -rf .venv
```

---

## 🏗️ Crear el entorno con `uv`

```bash
# Crear entorno virtual gestionado por uv
uv venv
```

> `uv` detectará automáticamente tu versión de Python.
> Si quieres fijar una versión exacta (por ejemplo 3.13):
>
> ```bash
> uv python pin 3.13
> ```

---

## 📦 Instalar dependencias principales

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

## 🧰 Instalar dependencias de desarrollo

```bash
uv add "langgraph-cli[inmem]" jupyter --dev
```

> Así separas dependencias de **producción** y **desarrollo** en tu `pyproject.toml`.

---

## 🔄 Sincronizar e instalar el proyecto local

```bash
# Verifica o reinstala todo lo declarado en pyproject.toml
uv sync

# Instala el proyecto local como editable (opcional, para imports tipo agents.main)
uv pip install -e .
```

---

## 🧠 Ejecutar el agente

```bash
uv run python main.py
```

O usa la interfaz visual:

```bash
uv run langgraph dev
```

---

## 🧪 Verificar el entorno

Puedes revisar qué dependencias están instaladas:

```bash
uv pip list
```

Y comprobar que Ollama responde:

```bash
ollama run qwen2.5:7b-instruct
```

---

## 📂 Estructura recomendada del proyecto

```
CDC/
├── agents/
│   ├── main.py
│   ├── tools.py
│   └── __init__.py
│
├── api/
│   ├── server.py
│   └── __init__.py
│
├── notebooks/
│   ├── exploracion.ipynb
│   └── grafo_visual.ipynb
│
├── .env
├── .gitignore
├── pyproject.toml
└── README.md
```

> Cada subcarpeta debe tener `__init__.py` para que Python la trate como paquete.

---

## 🧩 Variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
MODEL=qwen2.5:7b-instruct
OLLAMA_BASE_URL=http://localhost:11434
```

Y cárgalas en tu código:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## ✅ Resumen de comandos clave

| Acción                          | Comando                    |
| ------------------------------- | -------------------------- |
| Crear entorno                   | `uv venv`                  |
| Agregar librería                | `uv add paquete`           |
| Agregar librerías de desarrollo | `uv add paquete --dev`     |
| Ejecutar código                 | `uv run python archivo.py` |
| Sincronizar entorno             | `uv sync`                  |
| Ejecutar Studio                 | `uvx langgraph dev`        |
| Instalar localmente             | `uv pip install -e .`      |

---

## 🧰 `.gitignore` recomendado

```gitignore
# --- Python / uv ---
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

# --- Configuración local / credenciales ---
.env
.env.*
*.env
*.secret
*.secrets

# --- IDEs / editores ---
.vscode/
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json
.idea/
*.iml

# --- Jupyter / notebooks ---
.ipynb_checkpoints/
*.ipynb_convert/
*.nbconvert/

# --- Logs / trazas ---
*.log
logs/
**/wandb/
**/mlruns/

# --- Datos / artefactos ---
data/
data_raw/
data_tmp/
data_cache/
outputs/
artifacts/
models/
checkpoints/
runs/

# --- SO / escritorio ---
.DS_Store
Thumbs.db
```

---

## 🧩 Visualización de grafos

* Desde notebooks:

  ```python
  from agents.main import app
  app.get_graph().draw_png("grafo.png")
  ```
* Si falla el renderizado PNG, copia el grafo en formato texto y pégalo en [GraphvizOnline](https://dreampuf.github.io/GraphvizOnline).

---

## 🧵 Orquestación y depuración

LangGraph Studio permite abrir múltiples **threads** para depurar conversaciones en paralelo.
Ideal si manejas varios agentes (`analyst_agent`, `planner_agent`, `qa_agent`, etc.).

---

## 🧠 Habilidades reforzadas

* Modularización y orquestación de agentes.
* Creación de APIs para consumo externo.
* Gestión profesional de dependencias con `uv`.
* Uso de LangGraph Studio y Jupyter.
* Visualización y depuración de grafos.
* Separación de entornos de producción y desarrollo.

---

## 🧩 Próximos pasos

1. Añadir un **servidor FastAPI** en `/api/server.py` para exponer el grafo.
2. Integrar métricas de uso con `LangSmith` o `Prometheus`.
3. Crear notebooks para pruebas e integración.
4. Desplegar la API en Railway / Fly.io / Render.

---

> 💡 Si ya tienes tu `pyproject.toml` y estructura creada, este README es tu guía base para mantener tu entorno limpio y reproducible con `uv`.
