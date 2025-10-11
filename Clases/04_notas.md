# 🧠 Clase 4: Cómo funciona el **estado compartido** en LangGraph

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Comprender cómo funciona el **estado** como memoria compartida entre nodos: leerlo sin errores, actualizarlo correctamente y orquestar el flujo con `StateGraph` (START → NODOS → END).

---

## 🔑 Conceptos esenciales

- El **estado** es un diccionario (`dict`) compartido entre los nodos del grafo.  
- Cada **nodo**:
  - Lee datos del estado.
  - Modifica solo lo necesario.
  - Devuelve un `dict` con las claves que actualizó.  
- LangGraph fusiona automáticamente los cambios en el estado global.  
- Si una clave no existe, usa `state.get("clave")` para evitar errores (`KeyError`).  
- Para listas o secuencias, define un **agregador** que acumule en lugar de sobrescribir.

---

## 🧩 Modelo mental

```
input → [ START ] → (nodo A) → (nodo B) → ... → [ END ] → output
              \_______ estado compartido (dict) _______/
```

El estado fluye entre nodos que pueden representar modelos de lenguaje (LLMs), memorias, retrievals o tools.

---

## ✅ Buenas prácticas con `dict`

- Usa `get` para leer claves opcionales:
  ```python
  nombre = state.get("customer_name")          # None si no existe
  nombre = state.get("customer_name", "N/A")   # Valor por defecto
  ```
- Devuelve solo lo que cambias:
  ```python
  return {"customer_name": "John Doe"}  # ✅ correcto
  # return state  # ❌ evita sobreescribir todo el estado
  ```
- Añade claves solo cuando tengas datos válidos.

---

## 🛠️ Definir un **State** tipado

```python
from typing import TypedDict, Sequence
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class State(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    customer_name: str
    my_age: int
```

> `total=False` indica que todas las claves son opcionales.  
> `add_messages` permite acumular mensajes a lo largo del grafo.

---

## 🧱 Nodo que actualiza el estado

```python
def ensure_name(state: State) -> dict:
    '''Si no hay nombre, lo establece; si ya existe, no hace cambios.'''
    if state.get("customer_name") is None:
        return {"customer_name": "John Doe"}
    return {}
```

- Usa `get` para evitar errores.
- Devuelve solo las claves que modifica.

---

## 🤖 Nodo con modelo (Ollama)

```python
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()
MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

llm = ChatOllama(model=MODEL, base_url=BASE_URL)

def call_model(state: State) -> dict:
    '''Genera una respuesta usando el nombre si existe.'''
    nombre = state.get("customer_name", "amigo")
    user_text = f"Preséntate y saluda a {nombre}."
    return {
        "messages": llm.invoke([
            SystemMessage(content="Eres un asistente breve y claro."),
            HumanMessage(content=user_text),
        ])
    }
```

---

## 🕸️ Construcción del grafo con `StateGraph`

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

> Flujo: **START → ensure_name → llm → END**

---

## ▶️ Probar desde la terminal

```bash
uv run python -c "from agents.main import app; print(app.invoke({'customer_name': 'Nicolás'})['messages'][-1].content)"
```

O usando una función auxiliar:

```python
from langchain_core.messages import HumanMessage

def ask(text: str) -> str:
    result = app.invoke({"messages": [HumanMessage(content=text)]})
    return result["messages"][-1].content
```

```bash
uv run python -c "from agents.main import ask; print(ask('Dime algo amable.'))"
```

---

## 🗺️ Visualización del grafo (opcional)

Para mostrar el grafo en formato ASCII, instala la dependencia de desarrollo:

```bash
uv add grandalf --dev
```

Y en tu código:

```python
print(app.get_graph().draw_ascii())
```

Esto imprime una vista rápida del grafo directamente en consola.

---

## 🧪 Ejercicios prácticos

1. Si `customer_name` no existe, define `"John Doe"`; si existe, agrega `my_age = 30`.  
2. Crea una clave `facts: list[str]` y agrega elementos en cada ejecución.  
3. Añade un nodo que inserte un mensaje adicional antes del modelo y observa el flujo.

---

## 🛟 Errores comunes

- **KeyError:** usa `state.get()` con valor por defecto.  
- **Sobrescribir mensajes:** usa `add_messages`.  
- **Devolver todo el estado:** devuelve solo las claves modificadas.  
- **Imports rotos:** revisa `__init__.py` y reinstala con `uv pip install -e .`.

---

## ✅ Checklist

- [ ] State definido con `TypedDict` y claves opcionales.  
- [ ] Nodos devuelven solo los cambios.  
- [ ] `messages` usa agregador `add_messages`.  
- [ ] Grafo `START → ... → END` compilado.  
- [ ] Prueba exitosa con `uv run ...`.  
- [ ] (Opcional) Grafo visible con `grandalf`.

**Siguiente clase →** añadiremos **branching** y **tools** para decisiones y acciones automáticas.
