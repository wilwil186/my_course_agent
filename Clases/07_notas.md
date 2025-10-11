# 🧠 Clase 7: Integración de **LLM en grafos** para agentes que razonan

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Convertir un flujo de datos en un **agente que razona** integrando un LLM dentro de un **grafo**: memoria por hilo, decisiones con **ramas**, y estado compartido que crece con la conversación.

---

## 🧩 Idea central
- **LangGraph** orquesta el **flujo** (nodos, edges, estado).
- **LangChain** conecta el **LLM** (usaremos **Ollama** 100% open‑source).
- El **estado** guarda mensajes y variables (p. ej., `customer_name`).
- Con **threads** (IDs de hilo) y un **checkpointer** el estado **persiste** entre turnos.

---

## 🧱 Estado tipado + agregador de mensajes
```python
from typing import TypedDict, Sequence, Optional
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class State(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]  # append automático
    customer_name: Optional[str]
    turn_count: int
```
> `add_messages` asegura que cada nodo **agregue** al historial en lugar de sobrescribirlo.

---

## 🤖 LLM local (Ollama) y system prompt
```python
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()
MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

llm = ChatOllama(model=MODEL, base_url=BASE_URL, temperature=0.2)

SYSTEM_BASE = (
    "Eres un asistente útil y conciso. "
    "Si el usuario no ha compartido su nombre, pídeselo amablemente. "
    "Usa el nombre si está disponible para personalizar tus respuestas."
)
```

---

## 🧠 Nodos: asegurar nombre, decidir ruta y razonar
```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def ensure_name(state: State) -> dict:
    '''Si detectas un nombre explícito en el último mensaje humano, guárdalo.'''
    history = state.get("messages", [])
    last_human = next((m for m in reversed(history) if isinstance(m, HumanMessage)), None)
    if last_human:
        text = last_human.content.lower()
        # Regla simple de extracción (ejemplo mínimo):
        # "me llamo X" -> toma lo que sigue a 'me llamo'
        if "me llamo" in text:
            name = text.split("me llamo", 1)[1].strip(" .,:;!?\n\t").split()[0].title()
            return {"customer_name": name}
    return {}

def router(state: State) -> str:
    '''Decide a dónde ir: si falta nombre -> "ask_name", si no -> "reason".'''
    if not state.get("customer_name"):
        return "ask_name"
    return "reason"

def ask_name(state: State) -> dict:
    '''Pide el nombre del usuario (no sobrescribe historial, solo agrega).'''
    return {"messages": [AIMessage(content="¿Cómo te llamas?")]}

def reason(state: State) -> dict:
    '''Llama al LLM con todo el historial + system prompt personalizado.'''
    name = state.get("customer_name", None)
    system_text = SYSTEM_BASE + (f" Tu nombre es {name}." if name else "")
    msgs = [SystemMessage(content=system_text)] + list(state.get("messages", []))
    reply = llm.invoke(msgs)  # -> AIMessage
    turn = state.get("turn_count", 0) + 1
    return {"messages": [reply], "turn_count": turn}
```

---

## 🕸️ Grafo con **ramas** (conditional edges) y **memoria por hilo**
```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver  # persistencia en memoria

builder = StateGraph(State)
builder.add_node("ensure_name", ensure_name)
builder.add_node("ask_name", ask_name)
builder.add_node("reason", reason)

# START → ensure_name → (router) → ask_name/reason → END
builder.add_edge(START, "ensure_name")
builder.add_conditional_edges("ensure_name", router, {
    "ask_name": "ask_name",
    "reason": "reason",
})
builder.add_edge("ask_name", END)
builder.add_edge("reason", END)

# Checkpointer para persistir por thread_id
memory = MemorySaver()
app = builder.compile(checkpointer=memory)
```

---

## ▶️ Ejecución con **thread_id** (estado persistente)
```python
from langchain_core.messages import HumanMessage

# Turno 1 (no das el nombre)
out1 = app.invoke(
    {"messages": [HumanMessage(content="Hola, ¿me ayudas con un tip de Python?")]},
    config={"configurable": {"thread_id": "demo-01"}}
)
print(out1["messages"][-1].content)
# → El agente probablemente pedirá tu nombre

# Turno 2 (das el nombre)
out2 = app.invoke(
    {"messages": [HumanMessage(content="Me llamo Nicolás")]},
    config={"configurable": {"thread_id": "demo-01"}}
)
print(out2["messages"][-1].content)
# → Respuesta personalizada usando "Nicolás" y conservando el historial
```

> En **LangGraph Studio**, crea un **thread** y reutilízalo para ver cómo el estado (nombre, turnos y mensajes) se conserva entre interacciones.

---

## 🧱 Patrón de “new_state” (explícito)
Si prefieres construir un estado parcial y retornarlo al final del nodo:
```python
def node_with_new_state(state: State) -> dict:
    new_state: State = {}
    # ... lee del estado, decide y agrega solo cambios ...
    return new_state  # LangGraph lo fusiona con el estado global
```

---

## 🛟 Buenas prácticas
- **Nunca** retornes todo el estado: devuelve **solo** lo que cambias.  
- Si tu nodo usa historial, **prepende** un `SystemMessage` con reglas claras.  
- Evita invocar el LLM con historial vacío; asegúrate de tener al menos un prompt.  
- Usa `thread_id` constante para persistir contexto entre turnos.  
- Controla **temperature**: `0.0–0.3` para respuestas estables; `>0.7` más creativas.

---

## 🧪 Retos propuestos
1. **Nueva rama**: si el usuario pregunta por “fecha/hora”, dirígete a un nodo `tool_time` que responda con la hora local (sin LLM).  
2. **Memory extendida**: guarda una lista `facts: list[str]` con datos del usuario y úsala en `reason`.  
3. **Política de tokens**: crea un nodo `summarize` que resuma el historial cuando supere N mensajes.

---

## ✅ Checklist
- [ ] Estado con `messages` (agregador) + claves de negocio.  
- [ ] Nodos `ensure_name`, `router`, `ask_name`, `reason` definidos.  
- [ ] `add_conditional_edges` para ramificar decisiones.  
- [ ] `MemorySaver` + `thread_id` para persistencia por hilo.  
- [ ] Probado en CLI/Studio con dos turnos (sin y con nombre).
