# 💬 Clase 5: Gestión de **historial de mensajes** en LangGraph

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Modelar una **memoria conversacional** fiable con LangGraph: tipos de mensajes de LangChain, estado con `messages`, patrón de agregado sin sobrescribir y pruebas rápidas en consola/Studio.

---

## 🧠 Por qué importa el historial
Un buen agente necesita **contexto**. LangGraph integra el historial como parte del **estado compartido**, de modo que cada nodo “ve” la conversación y decide en consecuencia.

---

## 🧾 Tipos de mensajes (LangChain)
| Tipo | Para qué sirve | Nota |
|---|---|---|
| `HumanMessage` | Mensaje de la persona usuaria | Marca el rol de usuario |
| `AIMessage` | Respuesta del agente | El LLM “habla” con este rol |
| `SystemMessage` | Instrucciones de sistema | Guía estilo y políticas |
| `ToolMessage` | I/O con herramientas externas | Registra llamadas/resultados |
| `BaseMessage` | Clase base | Útil para tipar listas |

```python
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage
)

user = HumanMessage(content="Hola, soy Nico.")
ai   = AIMessage(content="¡Hola! ¿En qué te ayudo?")
```

---

## 🧩 Dos formas válidas de modelar el estado con historial

### Opción A (rápida): usar `MessagesState`
Cuando **solo** gestionas historial (y quizá alguna clave simple).

```python
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

def bot_node(state: MessagesState) -> dict:
    history = state["messages"]
    last_user = next((m for m in reversed(history) if isinstance(m, HumanMessage)), None)
    text = last_user.content if last_user else "Hola 👋"
    # Devolvemos SOLO lo nuevo; LangGraph lo agrega al final
    return {"messages": [AIMessage(content=f"Entendido: {text}")]}  # append

builder = StateGraph(MessagesState)
builder.add_node("bot", bot_node)
builder.add_edge(START, "bot")
builder.add_edge("bot", END)
app = builder.compile()
```

### Opción B (flexible): `TypedDict` + agregador `add_messages`
Cuando además del historial necesitas **otras claves** (memoria, flags, contadores…).

```python
from typing import TypedDict, Sequence, Optional
from typing_extensions import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class State(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]  # <- agrega, no pisa
    customer_name: Optional[str]
    turn_count: int

def ensure_name(state: State) -> dict:
    if not state.get("customer_name"):
        return {"customer_name": "John Doe"}
    return {}

def reply(state: State) -> dict:
    history = state.get("messages", [])
    last_user = next((m for m in reversed(history) if isinstance(m, HumanMessage)), None)
    text = last_user.content if last_user else "¿Seguimos?"
    turn = state.get("turn_count", 0) + 1
    return {
        "messages": [AIMessage(content=f"Turno {turn}: recibí “{text}”.")],
        "turn_count": turn,
    }
```

---

## 🕸️ Orquestación con `StateGraph`

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)  # o MessagesState si usas la opción A

builder.add_node("ensure_name", ensure_name)
builder.add_node("reply", reply)

builder.add_edge(START, "ensure_name")
builder.add_edge("ensure_name", "reply")
builder.add_edge("reply", END)

app = builder.compile()
```

> **Regla de oro:** cada nodo **devuelve solo** las claves que modificó. LangGraph se encarga de fusionarlas en el estado global.

---

## ➕ Añadir mensajes sin errores (patrón correcto)
Con el “messages stage” (`add_messages`) **no debes concatenar listas** a mano: simplemente retorna `{"messages": [nuevo_msg]}` y LangGraph **hace append**.

Si gestionas listas tú mismo (fuera del stage), recuerda:
```python
history = history + [AIMessage(content="nuevo")]  # ✅ lista + lista
# history = history + AIMessage(...)  # ❌ error: no concatenes objeto suelto
```

---

## 🔎 Depurar el historial rápidamente
No dependas de métodos mágicos. Imprime **rol y contenido** de forma explícita:

```python
def dump(history):
    for i, m in enumerate(history, 1):
        role = m.__class__.__name__.replace("Message","").lower()  # human/ai/system/tool
        print(f"{i:02d} [{role}] {m.content}")
```

---

## ▶️ Pruebas rápidas (CLI) y en Studio

**CLI (con helper):**
```python
from langchain_core.messages import HumanMessage

def ask(text: str) -> str:
    result = app.invoke({"messages": [HumanMessage(content=text)]})
    return result["messages"][-1].content
```

```bash
uv run python -c "from agents.main import ask; print(ask('Hola, soy Nico'))"
```

**LangGraph Studio:**
- `uv run langgraph dev`
- Crea un **thread** nuevo → envía un `HumanMessage` (“Hola…”) → observa cómo se agrega el `AIMessage` **sin borrar** lo anterior.

---

## 🧠 Estrategias de contexto (tokens/costos)
- **Ventana deslizante**: mantener los **k** últimos mensajes relevantes.  
- **Resumen**: pedir al LLM un **summary** periódico del historial para reducir tokens.  
- **Contexto por nodo**: decidir qué porción del historial **lee** cada nodo.  
- **Tool traces**: conserva `ToolMessage` cuando sea relevante para auditoría.

---

## 🛟 Problemas comunes y soluciones
- **`KeyError`** al leer estado → usa `state.get("clave", valor_por_defecto)`.  
- **Historial se sobreescribe** → define `messages` con `add_messages` (no reasignes).  
- **No aparece respuesta** → comprueba que el nodo retorna `{"messages": [AIMessage(...)]}`.  
- **Imports rotos** → confirma `__init__.py` y `uv pip install -e .` tras reordenar carpetas.

---

## ✅ Checklist
- [ ] Estado con `messages` definido (Opción A o B).  
- [ ] Nodos **devuelven solo cambios** (append implícito del historial).  
- [ ] Probado en CLI y en **LangGraph Studio**.  
- [ ] Estrategia básica de **contexto/tokens** decidida.

**Siguiente clase →** branching y tools: decisiones del agente y ejecución de acciones.
