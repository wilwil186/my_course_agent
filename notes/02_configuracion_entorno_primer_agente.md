# ⚙️ Clase 2: Configuración de entorno Python y tu primer agente (100% Open Source)

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Dejar listo tu entorno con `uv` + `Ollama` + `LangGraph` (arquitectura `src/`) y levantar un agente mínimo que podrás debuggear en **LangGraph Studio**, sin depender de APIs cerradas.

---

## 🧩 Qué aprenderás
En esta clase, construirás una base sólida para desarrollar agentes de IA de manera profesional y reproducible:

- **Crear y aislar el entorno con `uv`**: Aprenderás a usar `uv` como alternativa moderna a `pip` y `virtualenv`, creando entornos virtuales aislados que evitan conflictos de dependencias y facilitan la colaboración.
- **Instalar dependencias abiertas**: Configurarás paquetes clave como `langgraph` (para grafos), `langchain` (para integración con LLMs) y `langchain-ollama` (para modelos locales), asegurando un stack 100% open-source.
- **Usar Ollama para correr modelos locales**: Instalarás y configurarás Ollama para ejecutar LLMs como `qwen2.5:7b-instruct` directamente en tu máquina, sin depender de APIs externas ni costos variables.
- **Exportar un grafo `app` y abrirlo en LangGraph Studio**: Crearás un agente mínimo y lo visualizarás en Studio, una herramienta gráfica para depurar y probar grafos en tiempo real.
- **Buenas prácticas con `.env` y arquitectura `src/`**: Gestionarás variables sensibles (como claves API) y organizarás el código en una estructura modular para escalabilidad futura.

> Nota: Tu repo ya sigue este enfoque (estructura `src/`, `langgraph.json`, variables `MODEL` y `OLLAMA_BASE_URL`). Si sigues estas notas, todo encaja con lo que ya tienes. :contentReference[oaicite:1]{index=1}

---

## ✅ Requisitos
Antes de empezar, asegúrate de tener estos componentes básicos instalados y configurados:

- **Python ≥ 3.11** (recomendado 3.13): LangGraph requiere versiones modernas de Python para soporte completo de tipos y async. Puedes verificar con `python --version` o instalar desde python.org si es necesario.
- **Ollama corriendo localmente**: Una herramienta open-source para ejecutar LLMs en tu máquina. La usaremos para modelos como `qwen2.5:7b-instruct` sin necesidad de internet ni claves API. Descárgala de ollama.ai e inicia con `ollama serve`.
- **uv instalado**: Un gestor de paquetes rápido y moderno que reemplaza a `pip` + `virtualenv`. Gestiona entornos virtuales, dependencias y locks de forma eficiente.

### Instalación de `uv` (una sola vez por máquina)
Ejecuta estos comandos en tu terminal para instalar `uv` globalmente:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
uv --version
```

Esto descarga el instalador oficial, lo ejecuta y agrega `uv` a tu PATH. El comando `uv --version` confirma que está listo. Si usas zsh u otro shell, ajusta el archivo correspondiente (ej. `~/.zshrc`).

> Nota: En tu README ya tienes estos pasos documentados con comandos útiles para `uv`, incluyendo ejemplos de instalación y uso básico. Puedes referenciarlo para detalles adicionales. ([GitHub][1])

---

## 🧱 Crear el entorno y dependencias

Sigue estos pasos para configurar un entorno aislado y reproducible. Cada comando está explicado para que entiendas por qué es necesario.

1. **Crear entorno virtual con `uv`**:
   ```bash
   uv venv
   # (opcional) fijar versión exacta de Python si tienes múltiples instaladas
   # uv python pin 3.13
   ```
   - `uv venv` crea un directorio `.venv` con una instalación aislada de Python y paquetes. Esto evita conflictos con instalaciones globales (ej. si tienes otros proyectos con versiones diferentes de las mismas librerías).
   - El pin de Python asegura consistencia si tu sistema tiene varias versiones; omítelo si ya usas la recomendada.

2. **Agregar dependencias de producción**:
   ```bash
   uv add \
     "langgraph>=0.2" \
     "langchain>=0.3" \
     "langchain-core>=0.3" \
     "langchain-ollama>=0.3" \
     "pydantic<3" \
     "python-dotenv>=1.0"
   ```
   - Estas son las librerías esenciales para el curso: `langgraph` para grafos, `langchain` para integración con LLMs, `langchain-ollama` para modelos locales, `pydantic` para validación de datos y `python-dotenv` para cargar variables de entorno.
   - `uv add` las agrega a `pyproject.toml` y las instala automáticamente. Usa versiones mínimas para compatibilidad, pero permite actualizaciones.

3. **Agregar dependencias de desarrollo** (para herramientas como Studio y Jupyter):
   ```bash
   uv add "langgraph-cli[inmem]" jupyter --dev
   ```
   - `langgraph-cli[inmem]` instala el comando `langgraph dev` para abrir LangGraph Studio sin necesidad de una base de datos externa.
   - `jupyter` permite notebooks para prototipado interactivo. El flag `--dev` las marca como opcionales para producción, manteniendo el entorno ligero.

4. **Sincronizar e instalar el paquete local (arquitectura `src/`)**:
   ```bash
   uv sync
   uv pip install -e .
   ```
   - `uv sync` instala todas las dependencias listadas en `pyproject.toml` y genera un `uv.lock` para reproducibilidad (similar a `poetry.lock`).
   - `uv pip install -e .` instala tu propio código en modo "editable", permitiendo que imports como `from agents.main import app` funcionen sin reinstalar tras cambios. Es crucial para la arquitectura `src/` porque hace que el paquete sea importable como cualquier librería.

> Este flujo (sync + editable) es clave con `src/` para que módulos como `agents.main` se resuelvan correctamente. Lo documentaste ya en tu README con ejemplos prácticos. ([GitHub][1])

---

## 🔑 Variables de entorno (`.env`)

Las variables de entorno permiten configurar el comportamiento de tu agente sin hardcodear valores sensibles o específicos de ambiente. Crea un archivo `.env` en la raíz del proyecto (y agrégalo a `.gitignore` para evitar subir claves reales).

Ejemplo de contenido para `.env`:
```env
# Modelo local con Ollama (elige uno disponible en ollama pull)
MODEL=qwen2.5:7b-instruct
# URL donde Ollama escucha (por defecto en local)
OLLAMA_BASE_URL=http://localhost:11434
# Opcional: para tracing en LangSmith (desactiva si no usas)
# LANGSMITH_API_KEY=sk-...
# LANGCHAIN_TRACING_V2=false
```

- `MODEL`: Especifica el LLM a usar. Puedes cambiarlo a otros como `llama2:7b` o `mistral:7b` sin tocar código.
- `OLLAMA_BASE_URL`: Apunta a la instancia de Ollama. Si corres en una máquina remota, cámbialo a `http://tu-ip:11434`.
- Comentarios: Usa `#` para notas; líneas comentadas se ignoran.

Carga estas variables en tu código con `from dotenv import load_dotenv; load_dotenv()` (ya incluido en los ejemplos).

> Esta configuración coincide con tu repo actual y sigue las mejores prácticas de Ollama/LangChain para modelos locales, evitando APIs cerradas. Consulta tu README para más detalles y ejemplos. ([GitHub][1])

---

## 🗂️ Configuración de LangGraph Studio (`langgraph.json`)

LangGraph Studio necesita saber dónde encontrar tu grafo y qué entorno usar. Crea o edita `langgraph.json` en la raíz del proyecto con esta estructura:

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agents/main.py:app"
  },
  "env": ".env"
}
```

- `"dependencies": ["."]`: Indica que el proyecto actual es la dependencia principal (útil si tienes múltiples módulos).
- `"graphs"`: Mapea nombres de grafos a archivos. Aquí, `"agent"` apunta a la variable `app` exportada en `src/agents/main.py`.
- `"env": ".env"`: Carga variables de entorno desde `.env` al iniciar Studio.

Este archivo actúa como un "índice" para Studio: cuando corres `uv run langgraph dev`, busca este JSON y carga el grafo para visualización y pruebas.

> Esta configuración ya está implementada en tu repo exactamente como se muestra. Puedes verificar en tu `langgraph.json` y ajustarla si cambias la estructura de archivos. ([GitHub][1])

---

## 🤖 Código base de tu primer agente (open-source)

Crea el archivo `src/agents/main.py` con este código inicial. Es un agente mínimo que responde a mensajes usando un LLM local vía Ollama.

```python
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, MessagesState, START, END

# 1) Cargar variables de entorno desde .env
load_dotenv()

# 2) Instanciar el LLM local vía Ollama (100% open source)
#    Usa las variables MODEL y OLLAMA_BASE_URL definidas en .env
llm = ChatOllama()

# 3) Definir un nodo que llama al modelo
def call_model(state: MessagesState):
    """
    Función del nodo: recibe el estado (incluyendo lista de mensajes),
    invoca el LLM con esos mensajes y devuelve la respuesta agregada.
    """
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 4) Construir el grafo de LangGraph
builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_edge(START, "model")
builder.add_edge("model", END)

# 5) Compilar el grafo en una aplicación ejecutable
app = builder.compile()

# 6) Función helper para invocar el agente desde código o CLI
def ask(text: str) -> str:
    """
    Toma un texto de usuario, lo envuelve en mensajes (system + human),
    invoca el grafo y devuelve la respuesta del agente.
    """
    messages: List[BaseMessage] = [
        SystemMessage(content="Eres un asistente útil que contesta de forma breve y clara."),
        HumanMessage(content=text),
    ]
    result = app.invoke({"messages": messages})
    return result["messages"][-1].content
```

### Explicación paso a paso del código:
- **Imports**: `TypedDict` para tipos, mensajes de LangChain para estructurar conversaciones, `ChatOllama` para el LLM local, y componentes de LangGraph para el grafo.
- **Carga de .env**: `load_dotenv()` lee `MODEL` y `OLLAMA_BASE_URL` para configurar el LLM sin hardcodear.
- **Nodo `call_model`**: Es una función pura que toma el estado (diccionario con mensajes), llama al LLM y devuelve cambios (solo la nueva respuesta). LangGraph maneja la fusión automática.
- **Grafo**: `StateGraph` define el flujo; `MessagesState` es un tipo predefinido para manejar listas de mensajes. `START` y `END` son puntos especiales.
- **Compilación**: `app.compile()` convierte el builder en un objeto invocable.
- **Helper `ask`**: Facilita pruebas rápidas; construye mensajes iniciales y extrae la respuesta final.

* Este patrón **MessagesState + un nodo** es el “hola mundo” recomendado en la documentación oficial de LangGraph. Es simple pero extensible: luego añadirás ramas, herramientas y memoria. ([LangChain Docs][2])
* `ChatOllama` es parte de `langchain-ollama` (paquete oficial) y conecta con cualquier modelo de Ollama, respetando tus variables de entorno. ([LangChain][3])

---

## ▶️ Ejecutar y probar

Una vez configurado, prueba tu agente de dos formas: vía código/CLI para pruebas rápidas o en LangGraph Studio para depuración visual.

**Desde Python/CLI** (pruebas rápidas):
```bash
uv run python -c "from agents.main import ask; print(ask('¿Cuál es el clima en Bogotá?'))"
```
- `uv run` activa el entorno virtual y ejecuta el comando.
- Importa la función `ask` y pásale un texto; debería responder usando el LLM local.
- Si falla (ej. "Module not found"), verifica que instalaste con `-e .` y que `src/agents/__init__.py` existe.

**Abrir LangGraph Studio** (modo visual para debug):
```bash
uv run langgraph dev
# Alternativa temporal (sin instalar globalmente):
# uvx langgraph dev
```
- Esto inicia un servidor local (por defecto en http://localhost:2024).
- Abre tu navegador y verás el grafo `agent` cargado desde `langgraph.json`.
- Crea un "thread" nuevo, envía mensajes y observa el flujo en tiempo real: cómo se ejecuta cada nodo y cómo fluye el estado.
- Útil para depurar: si el agente no responde, inspecciona el estado en cada paso.

* Si Studio se queja de "no input", puedes añadir un nodo `ensure_input` que inyecte un mensaje por defecto como "Hola" (ya lo tienes documentado en tu README con ejemplos). ([GitHub][1])

---

## 🧪 Verificaciones rápidas

Antes de proceder, confirma que todo esté instalado y funcionando correctamente con estos comandos.

1. **Lista de paquetes instalados**:
   ```bash
   uv pip list
   ```
   - Deberías ver `langgraph`, `langchain`, `langchain-ollama`, etc. en la lista.
   - Si falta algo, revisa que corriste `uv sync` y `uv add` correctamente.

2. **Probar el modelo en Ollama directamente**:
   ```bash
   ollama run qwen2.5:7b-instruct
   ```
   - Esto descarga el modelo si no lo tienes (puede tomar tiempo la primera vez) y abre una sesión interactiva.
   - Escribe "Hola, ¿cómo estás?" y presiona Enter; debería responder coherentemente.
   - Sal con Ctrl+D. Si falla, verifica que Ollama esté corriendo (`ollama serve` en otra terminal).

Estas verificaciones aseguran que la integración entre `uv`, LangGraph y Ollama funcione antes de añadir complejidad.

> Consulta la guía oficial de integración con Ollama en LangChain para más detalles sobre instalación y uso avanzado. ([LangChain][4])

---

## 🛠️ Troubleshooting

Si encuentras errores comunes durante la configuración, aquí van soluciones paso a paso:

* **`Package 'langgraph' does not provide any executables`** (al correr `langgraph dev`):
  - Solución: Instala el CLI de desarrollo: `uv add "langgraph-cli[inmem]" --dev`.
  - Razón: El paquete base `langgraph` no incluye comandos; necesitas el extra `[inmem]` para Studio sin base de datos externa.
  - Referencia: Documentado en tu README con ejemplos. ([GitHub][1])

* **`ImportError: cannot import name 'app'`** (al importar desde `agents.main`):
  - Solución: Asegúrate de que `src/agents/main.py` exporte `app` (como en el código arriba) y que `langgraph.json` apunte exactamente a `./src/agents/main.py:app`.
  - Razón: Python necesita que el módulo sea importable; verifica `__init__.py` en `src/agents/` y reinstala con `uv pip install -e .` si cambiaste archivos.
  - Referencia: Tu repo ya tiene esta configuración; compara con el ejemplo. ([GitHub][1])

* **El modelo no existe en Ollama** (error al invocar LLM):
  - Solución: Ejecuta `ollama pull qwen2.5:7b-instruct` (o el modelo en `MODEL`) para descargarlo. Opcionalmente, agrega `validate_model_on_init=True` al `ChatOllama` para verificar al inicio.
  - Razón: Ollama necesita el modelo descargado localmente; no lo descarga automáticamente.
  - Referencia: Guía oficial de LangChain para integración con Ollama. ([LangChain][5])

Si persiste un error, busca en GitHub Issues de LangGraph o pregunta en la comunidad con detalles del traceback.

---

## 📚 Recursos abiertos

Estos recursos gratuitos y open-source te ayudarán a profundizar en los temas de esta clase:

* **LangGraph – Overview & Graph API** (StateGraph, START/END, ejemplos básicos y avanzados) ([LangChain Docs][2])
  - Explicaciones detalladas con código de muestra para construir grafos desde cero.
* **LangChain + Ollama** (integración oficial, instalación y uso con modelos locales) ([LangChain][4])
  - Guía paso a paso para conectar Ollama con LangChain, incluyendo troubleshooting y mejores prácticas.
* **uv Documentation** (gestor de paquetes y entornos) (busca "astral uv" en GitHub)
  - Tutoriales para proyectos Python, incluyendo grupos de dependencias y locks reproducibles.
* **Ollama GitHub** (modelos y configuración) (github.com/ollama/ollama)
  - Lista de modelos disponibles, guías de instalación y comunidad para soporte.

Usa estos para reforzar conceptos y resolver dudas específicas sin depender de proveedores cerrados.

---

## ✅ Checklist de esta clase

Usa esta lista para verificar que completaste todos los pasos antes de avanzar:

* [ ] Entorno virtual creado con `uv venv` y activado (verifica con `which python` apuntando a `.venv`).
* [ ] Dependencias instaladas correctamente (`langgraph`, `langchain`, `langchain-ollama`, `python-dotenv`, CLI dev con `jupyter`).
* [ ] Archivo `.env` creado con `MODEL=qwen2.5:7b-instruct` y `OLLAMA_BASE_URL=http://localhost:11434` (y cargado en código).
* [ ] Archivo `src/agents/main.py` existe, exporta `app` y la función `ask`, y se puede importar sin errores.
* [ ] Archivo `langgraph.json` apunta exactamente a `./src/agents/main.py:app` y carga `.env`.
* [ ] Comando `uv run langgraph dev` inicia Studio, carga el grafo `agent` y responde a mensajes de prueba.
* [ ] Modelo probado en Ollama directamente (`ollama run qwen2.5:7b-instruct` responde coherentemente).

Si todo está marcado, ¡felicidades! Tienes un agente básico funcionando con herramientas open-source.

**Siguiente clase →** Añadiremos **herramientas (tools)** al agente para que pueda realizar acciones externas, y introduciremos **branching** básico en el grafo para decisiones condicionales.

