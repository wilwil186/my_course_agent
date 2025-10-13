# 💬 Clase 5: Gestión de **historial de mensajes** en LangGraph

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Modelar una **memoria conversacional** fiable con LangGraph: tipos de mensajes de LangChain, estado con `messages`, patrón de agregado sin sobrescribir y pruebas rápidas en consola/Studio.

---

## 🧠 Por qué importa el historial
Un buen agente necesita **contexto** para mantener conversaciones coherentes y útiles. Sin historial, cada interacción sería aislada, como hablar con alguien con amnesia cada vez.

LangGraph integra el historial como parte del **estado compartido**, de modo que cada nodo “ve” la conversación completa y decide en consecuencia. Por ejemplo, si el usuario dice "Recuérdame mi nombre" en el turno 3, el nodo puede acceder a mensajes previos para responder "Te llamas Nicolás, como dijiste al inicio".

- **Beneficios**: Evita repeticiones, permite referencias cruzadas y mejora la personalización.
- **Desafíos**: Historiales largos consumen tokens (costos) y pueden confundir al LLM si no se gestionan.
- **Solución en LangGraph**: Usa agregadores como `add_messages` para acumular mensajes automáticamente, y estrategias como ventanas deslizantes para controlar el tamaño.

---

## 🧾 Tipos de mensajes (LangChain)
LangChain define tipos de mensajes para estructurar conversaciones de manera estándar. Cada tipo tiene un rol específico en el flujo.

| Tipo | Para qué sirve | Ejemplo de uso | Nota |
|---|---|---|---|
| `HumanMessage` | Mensaje de la persona usuaria | Entrada del usuario | Marca el rol de usuario; siempre inicia con esto en consultas |
| `AIMessage` | Respuesta del agente | Salida del LLM | El modelo responde con este tipo; se acumula en historial |
| `SystemMessage` | Instrucciones de sistema | Guía estilo, reglas o contexto | Invisible al usuario; establece comportamiento del agente |
| `ToolMessage` | I/O con herramientas externas | Registra llamadas a tools y resultados | Usado en agentes con herramientas; incluye tool name y output |
| `BaseMessage` | Clase base | Tipo genérico para listas mixtas | Útil para tipar `list[BaseMessage]` sin especificar |

### Ejemplos de creación:
```python
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage
)

# Mensaje del usuario
user = HumanMessage(content="Hola, soy Nico.")

# Respuesta del agente
ai = AIMessage(content="¡Hola Nico! ¿En qué te ayudo?")

# Instrucción del sistema
system = SystemMessage(content="Eres un asistente útil y siempre respondes en español.")

# Resultado de una tool (ej. búsqueda)
tool = ToolMessage(content="El clima en Bogotá es 22°C.", tool_call_id="search_01")

# Lista mixta
messages: list[BaseMessage] = [system, user, ai, tool]
```

Estos tipos permiten al LLM entender el contexto y roles en la conversación, mejorando la calidad de respuestas.

---

## 🧩 Dos formas válidas de modelar el estado con historial

Elige la opción que mejor se adapte a tu agente: simple si solo necesitas historial, flexible si agregas más datos.

### Opción A (rápida): usar `MessagesState`
Ideal cuando **solo** gestionas historial de mensajes (y quizás 1-2 claves simples). Es predefinido y minimalista.

```python
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

def bot_node(state: MessagesState) -> dict:
    """
    Nodo simple: lee historial, encuentra último HumanMessage,
    responde basado en él.
    """
    history = state["messages"]
    last_user = next((m for m in reversed(history) if isinstance(m, HumanMessage)), None)
    text = last_user.content if last_user else "Hola 👋"
    # Devuelve SOLO lo nuevo; LangGraph lo agrega al final automáticamente
    return {"messages": [AIMessage(content=f"Entendido: {text}")]}

# Construir grafo
builder = StateGraph(MessagesState)
builder.add_node("bot", bot_node)
builder.add_edge(START, "bot")
builder.add_edge("bot", END)
app = builder.compile()
```

- **Ventajas**: Código corto; `MessagesState` maneja agregación por defecto.
- **Limitaciones**: Difícil agregar claves extras (necesitas `TypedDict` personalizado).
- **Uso típico**: Agentes básicos de chat sin memoria adicional.

### Opción B (flexible): `TypedDict` + agregador `add_messages`
Cuando necesitas historial **más otras claves** (memoria persistente, flags, contadores, etc.). Más extensible para agentes complejos.

```python
from typing import TypedDict, Sequence, Optional
from typing_extensions import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class State(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]  # Agrega, no pisa
    customer_name: Optional[str]  # Memoria de usuario
    turn_count: int              # Contador de turnos

def ensure_name(state: State) -> dict:
    """Nodo: Establece nombre si falta."""
    if not state.get("customer_name"):
        return {"customer_name": "John Doe"}
    return {}

def reply(state: State) -> dict:
    """Nodo: Responde usando historial y estado."""
    history = state.get("messages", [])
    last_user = next((m for m in reversed(history) if isinstance(m, HumanMessage)), None)
    text = last_user.content if last_user else "¿Seguimos?"
    turn = state.get("turn_count", 0) + 1
    return {
        "messages": [AIMessage(content=f"Turno {turn}: recibí “{text}”.")],
        "turn_count": turn,
    }

# Construir grafo (agrega nodos y edges según necesites)
# builder = StateGraph(State)
# ...
```

- **Ventajas**: Flexible para crecer; combina historial con lógica de negocio.
- **Agregador `add_messages`**: Acumula mensajes sin sobrescribir; clave para mantener conversación.
- **Uso típico**: Agentes con memoria, herramientas o múltiples ramas.

---

## 🕸️ Orquestación con `StateGraph`

Conecta nodos en un flujo usando `StateGraph`. Aquí un ejemplo con la opción B (flexible).

```python
from langgraph.graph import StateGraph, START, END

# Usa tu State personalizado (o MessagesState para opción A)
builder = StateGraph(State)

# Agregar nodos (funciones definidas arriba)
builder.add_node("ensure_name", ensure_name)
builder.add_node("reply", reply)

# Definir flujo secuencial con edges
builder.add_edge(START, "ensure_name")  # Inicio → ensure_name
builder.add_edge("ensure_name", "reply") # ensure_name → reply
builder.add_edge("reply", END)            # reply → Fin

# Compilar en app invocable
app = builder.compile()
```

- **Proceso**:
  1. `StateGraph(State)`: Crea builder con tu tipo de estado.
  2. `add_node`: Registra funciones como nodos ejecutables.
  3. `add_edge`: Conecta nodos en orden (secuencial aquí).
  4. `compile()`: Genera `app` listo para `invoke()`.
- **Flujo resultante**: START → ensure_name (establece nombre si falta) → reply (responde usando historial) → END.

> **Regla de oro:** Cada nodo **devuelve solo** las claves que modificó (ej. `{"messages": [...], "turn_count": 1}`). LangGraph fusiona automáticamente en el estado global, evitando conflictos.

---

## ➕ Añadir mensajes sin errores (patrón correcto)
El agregador `add_messages` simplifica la acumulación de mensajes. Sigue estos patrones para evitar errores comunes.

- **Con `add_messages` (recomendado)**:
  - No concatenes listas manualmente.
  - Simplemente retorna `{"messages": [nuevo_msg]}`; LangGraph hace append automáticamente.
  - Ejemplo: `return {"messages": [AIMessage(content="Hola")]}` agrega al historial existente.

- **Si gestionas listas tú mismo** (menos común, fuera de `add_messages`):
  - Usa concatenación correcta para listas:
    ```python
    history = state.get("history", []) + [AIMessage(content="nuevo")]  # ✅ lista + lista
    # history = history + AIMessage(...)  # ❌ error: no concatenes objeto suelto
    ```
  - Razón: Python requiere tipos compatibles; `list + obj` falla.

- **Consejo**: Siempre usa `add_messages` en `State` para mensajes; es más seguro y automático.

Este patrón asegura que el historial crezca correctamente sin perder mensajes previos.

---

## 🔎 Depurar el historial rápidamente
Para entender qué pasa en el historial, imprime mensajes de forma clara y legible. Evita depender de métodos internos.

```python
def dump_messages(history):
    """
    Función helper: imprime historial con número, rol y contenido.
    Úsala en nodos para debugging: dump_messages(state.get("messages", []))
    """
    for i, m in enumerate(history, 1):
        # Extrae rol del tipo de mensaje (HumanMessage -> human)
        role = m.__class__.__name__.replace("Message", "").lower()
        print(f"{i:02d} [{role}] {m.content}")

# Ejemplo de uso en nodo
def debug_node(state: State) -> dict:
    print("Historial actual:")
    dump_messages(state.get("messages", []))
    return {}  # Sin cambios
```

- **Por qué útil**: Muestra el flujo real de mensajes (ej. "01 [human] Hola", "02 [ai] ¡Hola!").
- **Consejo**: Agrega prints temporales en nodos para rastrear cómo crece el historial.
- **Avanzado**: Usa en combinación con `thread_id` en Studio para ver persistencia.

Esta función te ayuda a detectar problemas como mensajes duplicados o perdidos.

---

## ▶️ Pruebas rápidas (CLI) y en Studio

Prueba tu agente para verificar que el historial se acumule correctamente.

### En CLI (con helper function):
Agrega esto a tu `main.py` para pruebas rápidas:
```python
from langchain_core.messages import HumanMessage

def ask(text: str) -> str:
    """
    Helper: Toma texto, lo envuelve en HumanMessage,
    invoca el grafo y devuelve la última respuesta.
    """
    result = app.invoke({"messages": [HumanMessage(content=text)]})
    return result["messages"][-1].content

# Prueba en terminal
# uv run python -c "from agents.main import ask; print(ask('Hola, soy Nico'))"
```

- **Ejemplo output**: "¡Hola Nico! ¿En qué te ayudo?" (usa nombre si disponible).
- **Consejo**: Invoca múltiples veces para ver acumulación: el segundo mensaje debería recordar el contexto.

### En LangGraph Studio (visual):
1. Ejecuta `uv run langgraph dev` (servidor en localhost:2024).
2. Abre el navegador y selecciona tu grafo (ej. "agent").
3. Crea un **thread** nuevo (para estado aislado).
4. Envía un `HumanMessage` como "Hola, soy Nico".
5. Observa: Se agrega un `AIMessage` de respuesta **sin borrar** mensajes previos.
6. Envía otro mensaje: El historial completo se usa para contexto.

Studio muestra el flujo en tiempo real, ideal para ver cómo `add_messages` acumula mensajes.

---

## 🧠 Estrategias de contexto (tokens/costos)
Historiales largos consumen tokens (costos en APIs como OpenAI) y pueden confundir al LLM. Usa estas estrategias para optimizar.

- **Ventana deslizante**: Mantén solo los **k** últimos mensajes (ej. últimos 10). Implementa en un nodo: `recent = state["messages"][-10:]`.
- **Resumen periódico**: Cada N turnos, pide al LLM un resumen del historial y reemplaza mensajes antiguos. Ejemplo: nodo `summarize` que genera un `SystemMessage` con summary.
- **Contexto por nodo**: Cada nodo decide qué leer. Ej: nodo de herramientas usa solo últimos mensajes; nodo de memoria usa todo.
- **Tool traces**: Conserva `ToolMessage` para auditoría (qué tools se llamaron y resultados), pero resume si es largo.
- **Otras**: Filtra por tipo (solo Human/AI, ignora System viejos) o usa embeddings para seleccionar mensajes relevantes.

Elige basado en costos vs precisión: más contexto = mejor respuestas, pero más tokens.

---

## 🛟 Problemas comunes y soluciones
Errores frecuentes con historial y cómo resolverlos rápidamente.

- **`KeyError` al leer estado** (ej. "customer_name"):
  - Causa: Clave no existe en estado inicial.
  - Solución: Usa `state.get("clave", "default")` en lugar de `state["clave"]`.

- **Historial se sobreescribe** (pierdes mensajes previos):
  - Causa: No usas agregador o reasignas `messages` directamente.
  - Solución: Define `messages` con `add_messages` en `State`; devuelve `{"messages": [nuevo]}`.

- **No aparece respuesta** (nodo no agrega mensaje):
  - Causa: Nodo no retorna `{"messages": [AIMessage(...)]}`.
  - Solución: Verifica que el nodo devuelva el dict correcto; prueba con prints.

- **Imports rotos** (ModuleNotFoundError al importar):
  - Causa: Carpetas sin `__init__.py` o instalación editable rota.
  - Solución: Agrega `__init__.py` en `src/agents/`; corre `uv pip install -e .` tras cambios.

Usa `dump_messages` (definida arriba) en nodos para inspeccionar el estado en tiempo real.

---

## ✅ Checklist
Verifica que tu agente maneje historial correctamente antes de añadir complejidad.

- [ ] Estado definido con `messages` (usa `MessagesState` para simple o `TypedDict` + `add_messages` para flexible).
- [ ] Nodos implementados devolviendo solo cambios (ej. `{"messages": [AIMessage(...)]}` para append automático).
- [ ] Grafo compilado y probado en CLI (respuestas coherentes con contexto).
- [ ] Probado en LangGraph Studio (crea thread, envía mensajes, verifica acumulación sin sobrescritura).
- [ ] Estrategia básica de contexto/tokens decidida (ej. ventana deslizante si necesitas optimizar costos).

Si todo está marcado, tu agente mantiene conversaciones coherentes.

**Siguiente clase →** Branching y tools: cómo hacer que el agente tome decisiones condicionales y ejecute acciones externas (como búsquedas o cálculos).
