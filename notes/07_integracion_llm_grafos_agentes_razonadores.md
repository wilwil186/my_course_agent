# 🧠 Clase 7: Integración de **LLM en grafos** para agentes que razonan

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Convertir un flujo de datos en un **agente que razona** integrando un LLM dentro de un **grafo**: memoria por hilo, decisiones con **ramas**, y estado compartido que crece con la conversación.

---

## 🧩 Idea central
Esta clase combina todo lo aprendido para crear agentes que razonan de manera estructurada y persistente.

- **LangGraph**: Orquesta el **flujo** del agente mediante grafos (nodos representan acciones como razonamiento o decisiones, edges definen transiciones basadas en condiciones, estado compartido pasa datos entre nodos).
- **LangChain**: Conecta el **LLM** (usaremos **Ollama** para 100% open-source y privacidad).
- **El estado** guarda mensajes y variables (p. ej., `customer_name`, `turn_count`) que persisten y se comparten entre nodos.
- **Con threads (IDs de hilo) y un checkpointer** el estado **persiste** entre turnos, permitiendo conversaciones continuas con memoria (ej. recordar el nombre del usuario en sesiones posteriores).

Resultado: Agente que razona paso a paso, recuerda contexto y toma decisiones basadas en estado, todo local y open-source.

---

## 🧱 Estado tipado + agregador de mensajes
Define el estado como un dict tipado para claridad y validación, incluyendo historial que se acumula automáticamente.

```python
from typing import TypedDict, Sequence, Optional
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class State(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]  # Acumula mensajes
    customer_name: Optional[str]  # Nombre del usuario (opcional)
    turn_count: int              # Contador de turnos (inicia en 0)
```

- **Explicación**:
  - `TypedDict, total=False`: Estado como dict con claves opcionales (puede no tener todas al inicio).
  - `messages: Annotated[Sequence[BaseMessage], add_messages]`: Lista de mensajes que se acumula (append) con cada nodo que devuelve `{"messages": [nuevo_msg]}`.
  - `customer_name: Optional[str]`: Para personalización (None si no se ha dado).
  - `turn_count: int`: Contador para rastrear interacciones.

> `add_messages` asegura que cada nodo **agregue** al historial en lugar de sobrescribirlo, manteniendo la conversación completa.

---

## 🤖 LLM local (Ollama) y system prompt
Configura el LLM local con Ollama y define un system prompt para guiar el comportamiento del agente.

```python
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Cargar variables de entorno
load_dotenv()
MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Instanciar LLM (reutilizable en nodos)
llm = ChatOllama(model=MODEL, base_url=BASE_URL, temperature=0.2)

# System prompt base (guía el estilo y lógica del agente)
SYSTEM_BASE = (
    "Eres un asistente útil y conciso. "
    "Si el usuario no ha compartido su nombre, pídeselo amablemente. "
    "Usa el nombre si está disponible para personalizar tus respuestas. "
    "Mantén respuestas breves y relevantes."
)
```

- **Configuración**:
  - `load_dotenv()`: Lee `MODEL` y `BASE_URL` de `.env`.
  - `ChatOllama`: Conecta con Ollama local (gratis, privado).
  - `temperature=0.2`: Bajo para respuestas consistentes (ajusta según creatividad needed).
- **System prompt**: Instrucciones invisibles al usuario que definen personalidad y reglas. Se prependea al historial en nodos.

Este setup asegura respuestas coherentes y personalizadas usando datos del estado.

---

## 🧠 Nodos: asegurar nombre, decidir ruta y razonar
Define nodos como funciones que procesan el estado y devuelven cambios. Aquí un flujo con detección de nombre y razonamiento.

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def ensure_name(state: State) -> dict:
    """
    Nodo: Detecta nombre en último HumanMessage y lo guarda en estado.
    Usa regla simple: busca "me llamo X" y extrae X.
    """
    history = state.get("messages", [])
    last_human = next((m for m in reversed(history) if isinstance(m, HumanMessage)), None)
    if last_human:
        text = last_human.content.lower()
        # Extracción básica (mejora con NLP si necesitas)
        if "me llamo" in text:
            name = text.split("me llamo", 1)[1].strip(" .,:;!?\n\t").split()[0].title()
            return {"customer_name": name}
    return {}  # Sin cambios

def router(state: State) -> str:
    """
    Nodo router: Decide siguiente nodo basado en estado.
    Si falta nombre -> "ask_name"; si tiene -> "reason".
    """
    if not state.get("customer_name"):
        return "ask_name"
    return "reason"

def ask_name(state: State) -> dict:
    """
    Nodo: Pide nombre al usuario agregando AIMessage.
    No modifica otras claves.
    """
    return {"messages": [AIMessage(content="¿Cómo te llamas?")]}

def reason(state: State) -> dict:
    """
    Nodo: Razona con LLM usando historial completo + system personalizado.
    Actualiza contador de turnos.
    """
    name = state.get("customer_name", None)
    system_text = SYSTEM_BASE + (f" El usuario se llama {name}." if name else "")
    msgs = [SystemMessage(content=system_text)] + list(state.get("messages", []))
    reply = llm.invoke(msgs)  # Invoca LLM
    turn = state.get("turn_count", 0) + 1
    return {"messages": [reply], "turn_count": turn}
```

- **ensure_name**: Lee historial, extrae nombre si presente (lógica simple; mejora con regex o NLP).
- **router**: Función de decisión (devuelve string con nombre del siguiente nodo).
- **ask_name**: Agrega pregunta al historial.
- **reason**: Construye mensajes (system + historial), invoca LLM, actualiza contador.

Estos nodos ilustran flujo condicional: detección → decisión → acción.

---

## 🕸️ Grafo con **ramas** (conditional edges) y **memoria por hilo**
Construye el grafo con ramas condicionales y persistencia para conversaciones continuas.

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver  # Persistencia en memoria

# Crear builder con estado
builder = StateGraph(State)

# Agregar nodos
builder.add_node("ensure_name", ensure_name)
builder.add_node("ask_name", ask_name)
builder.add_node("reason", reason)

# Definir flujo con rama condicional
builder.add_edge(START, "ensure_name")  # Inicio → ensure_name
builder.add_conditional_edges(
    "ensure_name",  # Nodo origen
    router,         # Función de decisión
    {
        "ask_name": "ask_name",  # Si router devuelve "ask_name" → ask_name
        "reason": "reason",      # Si "reason" → reason
    }
)
builder.add_edge("ask_name", END)  # ask_name → Fin
builder.add_edge("reason", END)    # reason → Fin

# Checkpointer para persistencia por thread_id
memory = MemorySaver()
app = builder.compile(checkpointer=memory)
```

- **Flujo**: START → ensure_name (detecta nombre) → router (decide) → ask_name (pregunta) o reason (responde) → END.
- **Ramas condicionales**: `add_conditional_edges` usa función `router` para elegir siguiente nodo basado en estado.
- **Persistencia**: `MemorySaver` guarda estado por `thread_id`, permitiendo conversaciones continuas (ej. recordar nombre en sesiones futuras).
- **Compilación**: `app.compile(checkpointer=memory)` crea app con memoria.

Este grafo introduce decisiones dinámicas, clave para agentes inteligentes.

---

## ▶️ Ejecución con **thread_id** (estado persistente)
Usa `thread_id` para mantener estado entre invocaciones, simulando conversaciones reales.

```python
from langchain_core.messages import HumanMessage

# Turno 1: Usuario pregunta sin dar nombre
out1 = app.invoke(
    {"messages": [HumanMessage(content="Hola, ¿me ayudas con un tip de Python?")]},
    config={"configurable": {"thread_id": "demo-01"}}  # ID único para hilo
)
print("Turno 1:", out1["messages"][-1].content)
# Output ejemplo: "¿Cómo te llamas?" (agente pide nombre porque falta)

# Turno 2: Usuario da nombre (mismo thread_id para continuidad)
out2 = app.invoke(
    {"messages": [HumanMessage(content="Me llamo Nicolás")]},
    config={"configurable": {"thread_id": "demo-01"}}
)
print("Turno 2:", out2["messages"][-1].content)
# Output ejemplo: "¡Hola Nicolás! Claro, aquí un tip de Python: usa list comprehensions para listas concisas."
# Nota: Usa "Nicolás" y recuerda contexto del turno 1

# Ver estado completo
print("Estado final:", out2)  # Incluye customer_name, turn_count, messages
```

- **thread_id**: Identificador único para cada conversación (ej. por usuario). El checkpointer guarda estado por ID.
- **Persistencia**: Entre turnos, el estado (nombre, contador, historial) se recupera automáticamente.
- **Beneficio**: Simula chat real; el agente "recuerda" interacciones previas.

> En **LangGraph Studio**, crea un **thread** (usa el mismo ID) y envía mensajes para ver cómo el estado (nombre, turnos y mensajes) se conserva entre interacciones. Inspecciona el flujo en tiempo real.

---

## 🧱 Patrón de “new_state” (explícito)
Para nodos complejos, construye un estado parcial explícitamente y devuélvelo al final.

```python
def node_with_new_state(state: State) -> dict:
    """
    Patrón alternativo: Construye new_state paso a paso,
    agregando solo cambios necesarios.
    """
    new_state: State = {}  # Inicia vacío

    # Lee del estado actual
    current_count = state.get("turn_count", 0)

    # Decide y agrega cambios
    if some_condition:
        new_state["turn_count"] = current_count + 1
        new_state["messages"] = [AIMessage(content="Respuesta basada en lógica.")]

    # Retorna solo cambios; LangGraph fusiona con estado global
    return new_state

# Uso en grafo
# builder.add_node("custom", node_with_new_state)
```

- **Ventajas**: Más legible para lógica compleja; evita efectos secundarios.
- **Fusión automática**: LangGraph combina `new_state` con el estado existente (agregadores como `add_messages` aplican reglas).
- **Cuándo usar**: Nodos con múltiples decisiones o cálculos intermedios.

Este patrón es opcional; el directo (devolver cambios inmediatos) suele ser suficiente.

---

## 🛟 Buenas prácticas
Sigue estas reglas para agentes robustos y fáciles de mantener.

- **Nunca retornes todo el estado**: Devuelve **solo** lo que cambias (ej. `{"messages": [reply]}`). Razón: Evita conflictos y mejora eficiencia; LangGraph fusiona automáticamente.
- **Si tu nodo usa historial, prepende un `SystemMessage` con reglas claras**: Asegura comportamiento consistente (ej. "Eres útil y breve.").
- **Evita invocar el LLM con historial vacío**: Siempre incluye al menos un `SystemMessage` o `HumanMessage` para contexto mínimo.
- **Usa `thread_id` constante para persistir contexto entre turnos**: El mismo ID mantiene estado (nombre, contador) en conversaciones largas.
- **Controla `temperature`**: `0.0–0.3` para respuestas estables y precisas; `>0.7` para más creativas/diversas. Ajusta por tarea.
- **Otras**: Usa `state.get()` para claves opcionales; agrega logs temporales para debugging; prueba en Studio para visualizar flujo.

Estas prácticas evitan errores comunes y hacen el agente predecible.

---

## 🧪 Retos propuestos
Practica añadiendo complejidad a tu agente con estos ejercicios. Implementa y prueba en CLI/Studio.

1. **Nueva rama condicional**: Agrega detección para "fecha/hora" en `ensure_name` o un nodo nuevo. Crea nodo `tool_time` que use `datetime` para responder hora local (sin LLM). Ruta: si pregunta por hora → `tool_time` → END.
2. **Memoria extendida**: Agrega `facts: list[str]` a `State` (usa agregador para listas). En `reason`, guarda "facts" del usuario (ej. "Le gusta Python"). Usa en respuestas para personalización.
3. **Política de tokens**: Crea nodo `summarize` que resuma historial si > N mensajes (ej. 10). Pide al LLM un summary y reemplaza mensajes antiguos. Llama desde `reason` si condición.

Estos retos introducen herramientas, memoria avanzada y optimización, preparando para agentes reales.

---

## ✅ Checklist
Verifica que tu agente razone y recuerde correctamente.

- [ ] Estado definido con `messages` (agregador `add_messages`) + claves como `customer_name` y `turn_count`.
- [ ] Nodos implementados: `ensure_name` (detecta nombre), `router` (decide rama), `ask_name` (pregunta), `reason` (razona con LLM).
- [ ] Grafo con `add_conditional_edges` para ramificar basado en estado (ej. con/sin nombre).
- [ ] `MemorySaver` configurado + `thread_id` usado en `invoke` para persistencia por hilo.
- [ ] Probado en CLI con múltiples turnos (turno 1: pregunta sin nombre → pide nombre; turno 2: da nombre → responde personalizado).
- [ ] Probado en LangGraph Studio (crea thread, envía mensajes, verifica que estado persista y ramas funcionen).

Si todo está marcado, tienes un agente básico que razona y recuerda.

**Siguiente clase →** RAG con OpenAI File Search para consultar documentos externos.
