# 🧠 Clase 4: Cómo funciona el **estado compartido** en LangGraph

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Entender y aplicar el **estado** como “memoria compartida” entre nodos: cómo leerlo sin errores, cómo **actualizar solo lo necesario** y cómo **orquestarlo** con `StateGraph` (start → nodos → end).  

---

## 🔑 Ideas clave (en claro)

- El **estado** es un **diccionario** (dict) compartido que pasa por todos los nodos.  
- Cada **nodo**:
  - **lee** del estado,
  - **modifica** solo lo que necesita,
  - **devuelve un diccionario** *solo con las claves que cambió*.  
- Al compilar el grafo, LangGraph **fusiona** (merge) esas devoluciones con el estado global.  
- Si una clave **no existe**, usa `state.get("clave")` y define **valores por defecto** para evitar `KeyError`.  
- Para listas de mensajes u otros acumuladores, usa un **agregador** (append en vez de sobrescribir).

---

## 🧩 Modelo mental

```

input  →  [ START ] → (nodo A) → (nodo B) → ... → [ END ]  →  output
___________  estado (dict)  ___________/

````

En los nodos puedes tener: LLM, retrieval (PDF/BD), memoria, tools (acciones), etc.  
Todos comparten y actualizan el **mismo estado**.

---

## ✅ Buenas prácticas con `dict`

- `get` para leer campos opcionales:
  ```py
  nombre = state.get("customer_name")          # None si no existe
  nombre = state.get("customer_name", "N/A")   # valor por defecto
````

* **No** devuelvas todo el estado; **solo** lo que cambias:

  ```py
  return {"customer_name": "John Doe"}  # OK
  # return state  # ❌ evita sobreescrituras innecesarias
  ```
* Añade claves **solo** cuando tengas datos válidos.

---

## 🛠️ Definiendo un **State** tipado (recomendado)

Usaremos `TypedDict` (tipo de Python) y un **agregador** de mensajes para **acumular** respuestas (append) en vez de sobrescribir.

```python
from typing import TypedDict, Sequence
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages  # agregador para "messages"

class State(TypedDict, total=False):
    # "messages" se acumula (append) en cada paso del grafo
    messages: Annotated[Sequence[BaseMessage], add_messages]
    customer_name: str
    my_age: int
```

> `total=False` hace que todas las claves sean **opcionales**: útil para construir el estado paso a paso.

---

## 🧱 Un nodo que **actualiza** el estado

```python
def ensure_name(state: State) -> dict:
    """Si no hay nombre, lo establece. Si ya hay, no cambia nada."""
    if state.get("customer_name") is None:
        return {"customer_name": "John Doe"}
    return {}
```

* **Lee** con `get`.
* **Devuelve** solo lo que cambia (o `{}` si no hay cambios).

---

## 🤖 Nodo que llama al modelo (ejemplo con Ollama)

*(Se apoya en lo que hiciste en la clase 2: `ChatOllama` y variables `.env`)*

```python
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()
MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
llm = ChatOllama(model=MODEL, base_url=BASE_URL)

def call_model(state: State) -> dict:
    """Genera una respuesta usando el nombre si existe."""
    nombre = state.get("customer_name", "amigo")
    user_text = f"Preséntate en una frase y saluda a {nombre}."
    return {
        "messages": llm.invoke([
            SystemMessage(content="Eres un asistente breve y claro."),
            HumanMessage(content=user_text),
        ])
        # Gracias al agregador `add_messages`, esto se **añade** a state["messages"]
    }
```

---

## 🕸️ Construir el grafo con `StateGraph`

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)

builder.add_node("ensure_name", ensure_name)
builder.add_node("llm", call_model)

builder.add_edge(START, "ensure_name")
builder.add_edge("ensure_name", "llm")
builder.add_edge("llm", END)

app = builder.compile()
```

> Flujo: **START → ensure_name → llm → END**.

---

## ▶️ Probar rápido (CLI)

```bash
uv run python -c "from agents.main import app; print(app.invoke({'customer_name': 'Nicolás'})['messages'][-1].content)"
```

O con un helper:

```python
from langchain_core.messages import HumanMessage, SystemMessage

def ask(text: str) -> str:
    result = app.invoke({"messages": [HumanMessage(content=text)]})
    return result["messages"][-1].content
```

```bash
uv run python -c "from agents.main import ask; print(ask('Dime algo amable.'))"
```

---

## 🗺️ Visualizar el grafo en **ASCII** (opcional)

1. Instala la dependencia de desarrollo:

```bash
uv add grandalf --dev
```

2. En código:

```python
print(app.get_graph().draw_ascii())
```

Esto imprime el grafo en ASCII (sencillo pero útil).

---

## 🧪 Ejercicios rápidos

1. **Condicional**: si `customer_name` no existe, pon `"John Doe"`; si existe, añade `my_age = 30`.
2. **Memoria**: crea una clave `facts: list[str]` y haz que un nodo la **acumule** (usa un agregador o maneja la lista con `get` y `+ [nuevo]`).
3. **Mensajes**: agrega otro nodo que **append** un `HumanMessage` extra antes del LLM y mira cómo cambia la respuesta.

---

## 🛟 Errores comunes y cómo evitarlos

* **`KeyError`** al leer el estado → usa `state.get(...)` y valores por defecto.
* **Sobrescribir mensajes** → define `messages` con agregador (`add_messages`).
* **Devolver todo el estado** → devuelve **solo** lo que cambias.
* **Imports rotos** tras mover carpetas → asegúrate de `__init__.py` y `uv pip install -e .`.

---

## ✅ Checklist

* [ ] State definido con `TypedDict` y claves opcionales (`total=False`)
* [ ] Nodos que devuelven **solo** los cambios
* [ ] `messages` con agregador para **acumular**
* [ ] Grafo **START → ... → END** compilado
* [ ] Prueba con `uv run ...`
* [ ] (Opcional) Grafo en ASCII con `grandalf`

**Siguiente clase →** añadiremos **ramas (branching)** y **tools** para decisiones y acciones del agente.

