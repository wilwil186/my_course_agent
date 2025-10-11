# 🔌 Clase 6: Integración de **OpenAI** y **Anthropic** con LangChain (agnóstico y fácil de cambiar)

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Conectar modelos de distintos proveedores sin reescribir el flujo. Mantener una **API homogénea** (con `invoke`), enviar **historial** (`System/Human/AI`) y alternar proveedor con una sola variable.

---

## 🧠 Arquitectura en una frase
- **LangGraph**: orquesta el **flujo** (grafos, estado compartido, branching).  
- **LangChain**: estandariza la **conexión a modelos** (OpenAI, Anthropic, Ollama, etc.).  
- **Tú** eliges el **proveedor** por entorno/variable; el grafo y la lógica **no cambian**.

---

## ⚙️ Instalación (dependencias de producción)

```bash
uv add langchain-openai langchain-anthropic
# (opcional, para seguir 100% open-source también):
uv add langchain-ollama
```

---

## 🔑 Variables de entorno (`.env` y `.env.example`)

`.env.example` (no subas claves reales):
```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini   # o el que prefieras

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-latest

# Open-source (Ollama)
PROVIDER=ollama            # "openai" | "anthropic" | "ollama"
MODEL=qwen2.5:7b-instruct
OLLAMA_BASE_URL=http://localhost:11434

# Hiperparámetros comunes
TEMPERATURE=0.3
```

Carga las variables en tu código:
```python
import os
from dotenv import load_dotenv
load_dotenv()
```

> **Buenas prácticas**: nunca imprimas tus claves; usa `assert os.getenv("OPENAI_API_KEY") is not None` si quieres verificar.

---

## 🧾 Tipos de mensajes (recordatorio rápido)

```python
from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage, BaseMessage
)
```

- `SystemMessage`: instrucciones del “sistema” (estilo, reglas).  
- `HumanMessage`: entrada de usuario.  
- `AIMessage`: respuesta del modelo.  
- `BaseMessage`: tipo base útil para listas heterogéneas.

---

## 🤝 Enfoque **agnóstico** con un pequeño inicializador

Crea un helper que **selecciona proveedor y modelo** usando variables de entorno. Así cambias de OpenAI ⇄ Anthropic ⇄ Ollama sin tocar el grafo.

```python
import os
from dotenv import load_dotenv
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama  # opcional si usas modelos locales

load_dotenv()

def init_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
):
    provider = (provider or os.getenv("PROVIDER", "ollama")).lower()
    temperature = temperature if temperature is not None else float(os.getenv("TEMPERATURE", "0.3"))
    if provider == "openai":
        return ChatOpenAI(
            model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            model=model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
            temperature=temperature,
        )
    elif provider == "ollama":
        return ChatOllama(
            model=model or os.getenv("MODEL", "qwen2.5:7b-instruct"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=temperature,
        )
    else:
        raise ValueError(f"Proveedor no soportado: {provider}")
```

---

## 🧩 Enviar **historial** (system/human/ai) y mantenerlo en el estado

```python
from typing import TypedDict, Sequence
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages

class State(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]  # se concatena
```

Nodo que usa el historial y **agrega** la nueva respuesta (no pisa lo anterior):

```python
llm = init_llm()  # toma PROVIDER/MODELO/TEMPERATURE desde .env

def llm_node(state: State) -> dict:
    msgs = list(state.get("messages", []))

    # Garantiza que exista un system prompt al inicio
    has_system = any(isinstance(m, SystemMessage) for m in msgs)
    if not has_system:
        msgs = [SystemMessage(content="Eres breve, claro y útil.")] + msgs

    # Invoca el modelo con todo el historial
    response = llm.invoke(msgs)  # -> AIMessage

    # Devuelve SOLO lo nuevo (messages stage hará append)
    return {"messages": [response]}
```

Orquestación mínima:

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)
builder.add_node("llm", llm_node)
builder.add_edge(START, "llm")
builder.add_edge("llm", END)
app = builder.compile()
```

Prueba rápida (CLI):
```bash
uv run python -c "from agents.main import app; \
from langchain_core.messages import HumanMessage; \
print(app.invoke({'messages':[HumanMessage(content='Dime un tip rápido de Python')]} )['messages'][-1].content)"
```

---

## 🧪 Probar **cada proveedor** en segundos

**OpenAI** (requiere `OPENAI_API_KEY` y `OPENAI_MODEL`):
```bash
PROVIDER=openai uv run python -c "from agents.main import app; \
from langchain_core.messages import HumanMessage; \
print(app.invoke({'messages':[HumanMessage(content='Resume esto en 1 línea: List comprehensions')]} )['messages'][-1].content)"
```

**Anthropic** (requiere `ANTHROPIC_API_KEY` y `ANTHROPIC_MODEL`):
```bash
PROVIDER=anthropic uv run python -c "from agents.main import app; \
from langchain_core.messages import HumanMessage; \
print(app.invoke({'messages':[HumanMessage(content='Explica “decorators” en Python en 1 línea')]} )['messages'][-1].content)"
```

**Ollama** (local, open‑source):
```bash
PROVIDER=ollama uv run python -c "from agents.main import app; \
from langchain_core.messages import HumanMessage; \
print(app.invoke({'messages':[HumanMessage(content='¿Qué es un grafo en 1 línea?')]} )['messages'][-1].content)"
```

---

## 🧪 Ejemplo directo (sin grafo) para validar instalación

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
resp = llm.invoke([HumanMessage(content="Hola, hola, ¿cómo estás?")])
print(type(resp))   # AIMessage
print(resp.content) # texto
```

Cambiar de modelo es **cambiar una cadena**. Con Anthropic:
```python
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0.3)
```

---

## 🎛️ Hiperparámetros y contexto
- **temperature**: creatividad (alto = más creativo).  
- **top_p / top_k**: algunos proveedores lo exponen adicionalmente.  
- **historial**: envía todo o aplica ventana/sumario según costos y necesidades.

---

## 🛟 Troubleshooting

- **`ValueError: Proveedor no soportado`** → revisa `PROVIDER` en `.env`.  
- **`401/403`** → clave inválida o falta de permisos (revisa cuenta/plan).  
- **`429 RateLimit`** → límite de cuota; espera, baja concurrencia o ajusta plan.  
- **`Model not found`** → nombre incorrecto; valida `OPENAI_MODEL` / `ANTHROPIC_MODEL`.  
- **Ollama no responde** → verifica `OLLAMA_BASE_URL` y que `ollama serve` esté activo.  
- **Mensajes se borran** → define `messages` con `add_messages` y devuelve solo lo nuevo.

---

## ✅ Checklist
- [ ] Instalaste `langchain-openai` y/o `langchain-anthropic` (y `langchain-ollama` si usas local).  
- [ ] Variables en `.env` (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `PROVIDER`, modelos…).  
- [ ] Helper `init_llm` funcionando; `invoke` devuelve `AIMessage`.  
- [ ] Grafo mínimo integrado y probado en CLI/Studio.  
- [ ] Historial en el estado con `add_messages` (no se pisa).

**Siguiente clase →** branching y tools: decisiones automáticas y acciones (búsqueda, cálculo, I/O).
