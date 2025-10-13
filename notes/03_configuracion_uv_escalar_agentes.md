# ⚙️ Clase 3: Configuración de **uv** para escalar agentes de IA en producción

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Pasar de prototipos sueltos a un **proyecto escalable**: aislar entornos, separar dependencias **prod/dev**, ordenar el repo, habilitar **LangGraph Studio** y **notebooks** para depuración y visualización.

---

## 🧩 ¿Por qué `uv`?
`uv` es una herramienta moderna que simplifica y acelera el desarrollo Python, especialmente para proyectos con múltiples dependencias como agentes de IA. Aquí por qué es superior a enfoques tradicionales:

- **Unifica herramientas fragmentadas**: Antes usabas `pip` para instalar, `virtualenv` para aislar, `pip-tools` para locks y `poetry` para gestión. `uv` hace todo esto en uno, reduciendo la curva de aprendizaje y errores de configuración.
- **Aísla entornos y acelera instalaciones**: Crea entornos virtuales rápidamente (mucho más rápido que `virtualenv`) y resuelve dependencias en paralelo, evitando conflictos entre proyectos (ej. si un proyecto usa `langchain==0.2` y otro `0.3`).
- **Usa estándares abiertos**: Se basa en `pyproject.toml` (estándar PEP 621) para metadatos y dependencias, generando un `uv.lock` para reproducibilidad exacta (similar a `poetry.lock` o `Pipfile.lock`). Esto asegura que tu equipo use las mismas versiones en cualquier máquina.
- **Facilita separación de entornos**: Soporta "dependency groups" para dividir **producción** (librerías esenciales) de **desarrollo** (herramientas como linters o notebooks), manteniendo imágenes de producción ligeras y evitando instalaciones innecesarias en CI/CD.

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

Si ya tienes un proyecto iniciado (como en la clase 2), no necesitas reinicializar; usa esta sección para refinar y consolidar archivos clave. Si empiezas de cero, sigue estos pasos para una base sólida.

1. **Inicializar proyecto con `uv`** (solo si no tienes nada):
   ```bash
   uv init
   ```
   - Crea una estructura básica de proyecto Python con `pyproject.toml`, `.gitignore` y carpetas estándar.
   - Esto es opcional si ya tienes tu repo; enfócate en editar archivos existentes.

2. **Contenido recomendado para `.gitignore`** (edita o crea el archivo):
   ```
   # Entornos virtuales y caches de Python
   .venv/
   __pycache__/
   .ipynb_checkpoints/
   # Archivos sensibles (claves, secrets)
   .env
   .env.*
   # Archivos del sistema
   .DS_Store
   # Carpetas generadas por herramientas (ej. LangGraph local)
   .langgraph/
   ```
   - Agrega estas líneas a tu `.gitignore` existente para evitar subir archivos innecesarios o sensibles a Git.
   - Razón: `.env` contiene claves API; `.venv/` es específico de tu máquina; `__pycache__/` son archivos temporales.

> **Importante**: No ignores `uv.lock` (si se genera); commitea este archivo para asegurar builds reproducibles en cualquier entorno (CI/CD o colegas).

Estos archivos base mantienen tu proyecto limpio, seguro y fácil de compartir.

---

## 🧱 Estructura sugerida del repo

Para escalar tu proyecto de agentes de IA, organiza el código de manera modular y mantenible. Esta estructura se basa en tu enfoque `src/` existente y añade capas para producción.

```
repo/
├─ pyproject.toml          # Metadatos, dependencias y configuración del proyecto
├─ uv.lock                 # Lock de versiones exactas (generado por uv, commitea)
├─ langgraph.json          # Configuración para LangGraph Studio
├─ .env.example            # Plantilla de variables (sin claves reales)
├─ .gitignore              # Archivos a ignorar en Git (edita según arriba)
├─ clases/                 # Notas del curso (MDs como este)
│  ├─ 01_Notas.md
│  └─ 02_Notas.md
├─ src/                    # Código fuente (paquete principal)
│  ├─ agents/              # Lógica de agentes y grafos
│  │  ├─ __init__.py       # Hace que 'agents' sea un paquete
│  │  └─ main.py           # Grafo principal, exporta 'app'
│  ├─ tools/               # Herramientas externas (APIs, cálculos)
│  │  ├─ __init__.py
│  │  └─ weather.py        # Ejemplo: tool para consultar clima
│  ├─ api/                 # Exposición de APIs (opcional para prod)
│  │  ├─ __init__.py
│  │  └─ http.py           # Servidor FastAPI que expone el agente
│  └─ config/              # Configuración y lectura de .env
│     ├─ __init__.py
│     └─ settings.py       # Funciones para cargar variables
└─ notebooks/              # Jupyter para prototipado y pruebas
   └─ 01_sanity_check.ipynb
```

### Explicación de la estructura:
- **Raíz**: Archivos de configuración (`pyproject.toml`, `uv.lock`) y documentación (`clases/`, `notebooks/`).
- **src/**: Todo el código fuente. Cada subcarpeta es un paquete Python (requiere `__init__.py` para imports como `from agents.main import app`).
- **Modularidad**: Separa agentes (lógica), tools (acciones externas), api (servicio web) y config (entorno). Facilita escalar añadiendo más archivos sin desorden.
- **Producción-ready**: Puedes empaquetar `src/` como una librería instalable con `uv pip install -e .`.

> Asegúrate de tener `__init__.py` vacío en cada subcarpeta de `src/` para que Python las trate como paquetes importables. Esto evita errores como "ModuleNotFoundError" al importar.

---

## 📦 Dependencias: prod vs dev

Una buena gestión de dependencias separa lo esencial para producción de herramientas de desarrollo. Esto mantiene imágenes de Docker ligeras y evita conflictos.

### Ejemplo de `pyproject.toml` (edita el tuyo)
```toml
[project]
name = "my-course-agent"
version = "0.1.0"
description = "Agentes de IA con LangGraph (open source)"
readme = "README.md"
requires-python = ">=3.11"
authors = [
    {name = "Tu Nombre", email = "tu@email.com"}
]

# Dependencias de PRODUCCIÓN (se instalan en prod/CI)
dependencies = [
    "langgraph>=0.2",
    "langchain>=0.3",
    "langchain-core>=0.3",
    "langchain-ollama>=0.3",
    "python-dotenv>=1.0"
]

[dependency-groups]
# Dependencias de DESARROLLO (solo local/dev, no en prod)
dev = [
    "langgraph-cli[inmem]",  # Para Studio sin DB externa
    "jupyter",               # Notebooks
    "ipykernel",             # Kernel para Jupyter
    "ruff",                  # Linter rápido
    "pytest"                 # Tests
]
```

- `[project]`: Metadatos estándar (nombre, versión, descripción). Útil para empaquetar tu proyecto como librería.
- `dependencies`: Librerías que siempre se necesitan (ej. en producción o CI). Usa versiones mínimas para flexibilidad.
- `[dependency-groups]`: Grupos opcionales. `dev` no se incluye en instalaciones de producción, ahorrando espacio.

### Comandos útiles con `uv` para gestionar dependencias
- **Agregar dependencias de producción** (se añaden a `dependencies`):
  ```bash
  uv add "langgraph>=0.2" "langchain>=0.3" "langchain-ollama>=0.3" "python-dotenv>=1.0"
  ```
  - Actualiza `pyproject.toml` y `uv.lock` automáticamente.

- **Agregar dependencias de desarrollo** (se añaden a `dev`):
  ```bash
  uv add "langgraph-cli[inmem]" jupyter ipykernel ruff pytest --dev
  ```
  - Usa `--dev` para asignar al grupo `dev`.

- **Sincronizar e instalar todo**:
  ```bash
  uv sync
  ```
  - Instala todas las dependencias listadas y genera/actualiza `uv.lock` para versiones exactas.

- **Instalar en modo editable para `src/`** (necesario para imports locales):
  ```bash
  uv pip install -e .
  ```
  - Hace que tu código en `src/` sea importable como una librería instalada, permitiendo `from agents.main import app` sin errores.

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

Las variables de entorno permiten configurar el comportamiento sin hardcodear valores sensibles. Crea estos archivos en la raíz del proyecto.

### `.env` (con tus claves reales, no commitear)
```env
# Modelo local con Ollama (elige uno de ollama pull)
MODEL=qwen2.5:7b-instruct
OLLAMA_BASE_URL=http://localhost:11434

# Observabilidad (opcional, para tracing en LangSmith)
LANGCHAIN_TRACING_V2=false
# Si usas tracing: LANGSMITH_API_KEY=sk-...
```

### `.env.example` (plantilla sin claves, commitea esto)
```env
# Copia esto a .env y agrega tus valores reales
MODEL=qwen2.5:7b-instruct
OLLAMA_BASE_URL=http://localhost:11434
LANGCHAIN_TRACING_V2=false
```

- **Carga en código**: Usa `from dotenv import load_dotenv; load_dotenv()` al inicio de tus scripts.
- **Seguridad**: Nunca commitees `.env` real; usa `.env.example` para que otros sepan qué variables necesitan.
- **Flexibilidad**: Cambia `MODEL` para probar diferentes LLMs sin tocar código.

Esto mantiene tu configuración flexible y segura para entornos locales y producción.

---

## 🧭 LangGraph Studio y ejecución

LangGraph Studio es una interfaz web para visualizar y depurar grafos en tiempo real. Configúralo correctamente para una experiencia fluida.

### Configuración en `langgraph.json` (edita el tuyo)
```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agents/main.py:app"
  },
  "env": ".env"
}
```

- `"dependencies"`: Lista de paquetes necesarios (tu proyecto actual).
- `"graphs"`: Mapea nombres de grafos a archivos. Aquí, `agent` carga la variable `app` de `src/agents/main.py`.
- `"env"`: Archivo de variables a cargar (`.env`).

### Ejecutar en Studio (debug visual)
```bash
uv run langgraph dev
# Opcional: cambiar puerto si 2024 está ocupado
uv run langgraph dev --port 2024
```
- Inicia un servidor local en http://localhost:2024 (o el puerto especificado).
- Abre el navegador, selecciona el grafo `agent` y crea un "thread" nuevo.
- Envía mensajes y observa el flujo: ejecución de nodos, cambios de estado y respuestas.
- Útil para depurar ramas o herramientas; pausa y inspecciona en cualquier punto.
- Si el puerto está ocupado, cierra procesos previos con `pkill -f langgraph` o usa `--port` diferente.

### Ejecutar sin Studio (pruebas rápidas en terminal)
```bash
uv run python -c "from agents.main import ask; print(ask('Ping de salud?'))"
```
- Invoca el agente directamente desde código.
- Útil para tests automatizados o integración en scripts.

Studio es ideal para desarrollo interactivo; el CLI para automatización.

---

## 📒 Notebooks (Jupyter)

Los notebooks son ideales para prototipado interactivo de agentes, pruebas de herramientas y visualización de datos.

1. **Instalar kernel para este entorno** (conecta Jupyter a tu venv de `uv`):
   ```bash
   uv run python -m ipykernel install --user --name my-course-agent
   ```
   - Crea un kernel personalizado llamado `my-course-agent` que usa tu entorno virtual.
   - Razón: Sin esto, Jupyter usaría Python global, sin acceso a tus dependencias instaladas con `uv`.

2. **Usar el kernel en un notebook**:
   - Abre Jupyter con `uv run jupyter notebook` o desde VS Code.
   - En el notebook, selecciona el kernel **my-course-agent** en el menú (Kernel > Change Kernel).
   - Ahora puedes importar `from agents.main import app` y experimentar interactivamente.

3. **Troubleshooting de imports** (si falla al importar paquetes locales):
   - Reinicia el kernel del notebook (Kernel > Restart).
   - Asegura que corriste `uv pip install -e .` para modo editable.
   - Verifica que cada subcarpeta en `src/` tenga `__init__.py` (hace que sean paquetes).
   - Si reorganizas código, reinstala el kernel con el comando de arriba.

Notebooks facilitan iteración rápida: prueba cambios en el grafo, visualiza resultados y documenta experimentos.

---

## 🌐 Exponer API (FastAPI minimal)

Para producción o integración con otras apps, expón tu agente como una API web usando FastAPI (rápido y moderno).

### Código para `src/api/http.py` (crea el archivo)
```python
from fastapi import FastAPI
from pydantic import BaseModel
from agents.main import ask  # Importa tu función helper

app = FastAPI(title="My Course Agent API", description="Agente de IA con LangGraph")

class Query(BaseModel):
    text: str  # Modelo para validar entrada

@app.get("/health")
def health():
    """Endpoint de salud para monitoreo."""
    return {"status": "ok", "message": "Agente funcionando"}

@app.post("/ask")
def ask_route(q: Query):
    """Endpoint para consultar el agente."""
    answer = ask(q.text)  # Usa tu helper existente
    return {"question": q.text, "answer": answer}
```

- **FastAPI**: Framework web ligero para APIs REST. Usa Pydantic para validación automática.
- **Endpoints**: `/health` para checks de monitoreo; `/ask` para consultas (acepta JSON con `{"text": "pregunta"}`).
- **Integración**: Llama a tu `ask` existente, manteniendo consistencia.

### Ejecutar la API localmente
```bash
uv run uvicorn src.api.http:app --reload --port 8000
```
- `uvicorn`: Servidor ASGI rápido (instálalo con `uv add uvicorn` si falta).
- `--reload`: Recarga automáticamente al cambiar código (solo desarrollo).
- Accede en http://localhost:8000/docs para documentación interactiva (Swagger UI).

Esta API permite integrar tu agente en apps web, móviles o sistemas externos de forma escalable.

---

## 🔍 Visualización de grafos

Visualizar el grafo ayuda a entender y depurar el flujo de tu agente, especialmente con ramas complejas.

- **En LangGraph Studio**: Verás el grafo como un diagrama interactivo. Cada ejecución deja un "trace" (trazo) mostrando el camino tomado, estados en cada nodo y tiempos de ejecución.
- **Exportar a formatos externos**:
  - Usa herramientas como Mermaid (para docs) o DOT (para Graphviz).
  - Ejemplo: Si tienes un helper que exporta `app.get_graph().draw_mermaid()`, pega el output en un editor online como mermaid.live para renderizarlo como imagen.
- **Cuándo es útil**: Cuando tengas múltiples nodos o ramas condicionales; facilita explicar el flujo a tu equipo o documentar en README.

Esta visualización complementa el código, haciendo el comportamiento del agente más transparente.

---

## 🛠️ Troubleshooting

Errores comunes en esta configuración y cómo resolverlos paso a paso:

- **`ModuleNotFoundError` (ej. "no module named 'agents'")**:
  - Causa: Faltan `__init__.py` en subcarpetas de `src/` o no instalaste en modo editable.
  - Solución: Agrega `__init__.py` vacío en cada paquete (ej. `src/agents/`). Luego, corre `uv pip install -e .` para hacer el paquete importable.

- **Puerto ocupado al correr `langgraph dev`**:
  - Causa: Otro proceso usa el puerto 2024.
  - Solución: Cierra procesos previos con `pkill -f "langgraph"` o especifica otro puerto: `uv run langgraph dev --port 2025`.

- **Kernel de Jupyter no aparece o falla**:
  - Causa: Kernel no instalado o entorno no conectado.
  - Solución: Reinstala con `uv run python -m ipykernel install --user --name my-course-agent`. Reinicia Jupyter y selecciona el kernel correcto.

- **Ollama no responde o modelo no encontrado**:
  - Causa: Ollama no corriendo o modelo no descargado.
  - Solución: Inicia `ollama serve` en otra terminal. Verifica `OLLAMA_BASE_URL` en `.env`. Descarga modelo con `ollama pull qwen2.5:7b-instruct`.

Si persiste, busca en GitHub Issues de `uv` o LangGraph con el mensaje de error exacto.

---

## 📚 Lecturas recomendadas (abierto)

Estos recursos gratuitos y open-source profundizan en los temas de esta clase:

- **uv Documentation** (gestor de paquetes moderno para Python):
  - Busca "astral uv" en GitHub o docs.astral.sh/uv. Incluye tutoriales para proyectos, grupos de dependencias y CI/CD.
- **LangGraph – conceptos y API de grafos** (LangChain Docs):
  - Sección "Tutorials" y "Graph API". Ejemplos de StateGraph, edges y checkpointers.
- **FastAPI Documentation** (para APIs web):
  - fastapi.tiangolo.com. Guías para endpoints, Pydantic y despliegue.
- **Jupyter y VS Code Extension**:
  - jupyter.org para instalación; extensión "Jupyter" en VS Code para integración.

*(Evito enlaces cerrados; busca por nombre en sitios oficiales para acceso directo.)*

---

## ✅ Checklist de la clase

Verifica que completaste todos los aspectos para un proyecto escalable:

* [ ] Archivo `pyproject.toml` configurado con secciones `[project]` y `[dependency-groups]` (prod vs dev separados).
* [ ] Archivo `uv.lock` generado y committeado para reproducibilidad.
* [ ] Archivos `.env` (con claves reales) y `.env.example` (plantilla) creados y `.env` en `.gitignore`.
* [ ] Código en `src/agents/main.py` exporta `app` y se importa sin errores.
* [ ] Archivo `langgraph.json` apunta correctamente a `./src/agents/main.py:app` y carga `.env`.
* [ ] Comando `uv run langgraph dev` inicia Studio, carga el grafo y responde a pruebas.
* [ ] (Opcional) Archivo `src/api/http.py` creado y sirve endpoints `/ask` y `/health` con `uvicorn`.
* [ ] Kernel de Jupyter instalado y funcional para prototipado.
* [ ] Estructura de repo organizada con `__init__.py` en paquetes.

Si todo está marcado, tu proyecto está listo para desarrollo avanzado y producción.

**Siguiente clase →** Añadiremos **tools** (herramientas externas como APIs o cálculos), control de **estado** avanzado y **ramas** (branching) para que el agente tome decisiones inteligentes basadas en condiciones.

