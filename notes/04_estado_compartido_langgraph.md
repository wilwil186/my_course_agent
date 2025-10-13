# 🧠 Clase 4: Cómo funciona el **estado compartido** en LangGraph

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Comprender cómo funciona el **estado** como memoria compartida entre nodos: leerlo sin errores, actualizarlo correctamente y orquestar el flujo con `StateGraph` (START → NODOS → END).

---

## 🔑 Conceptos esenciales

El estado es el "corazón" de tu grafo en LangGraph: un diccionario compartido que fluye entre nodos, permitiendo que cada uno lea y modifique datos de manera controlada.

- **El estado es un diccionario (`dict`) compartido entre los nodos del grafo**: Imagínalo como una pizarra donde todos los nodos pueden leer y escribir. Claves comunes: `"messages"` (historial de conversación), `"customer_name"` (datos de usuario), `"turn_count"` (contadores).
- **Cada nodo** sigue un patrón estricto:
  - **Lee datos del estado**: Accede a valores existentes con `state["clave"]` o `state.get("clave")`.
  - **Modifica solo lo necesario**: No cambies todo el estado; enfócate en lo relevante para evitar efectos secundarios.
  - **Devuelve un `dict` con las claves que actualizó**: Por ejemplo, `{"customer_name": "John"}`. LangGraph fusiona estos cambios automáticamente en el estado global.
- **LangGraph fusiona automáticamente los cambios en el estado global**: Si dos nodos devuelven cambios simultáneos, se combinan sin conflictos (usando reglas de agregadores para listas).
- **Si una clave no existe, usa `state.get("clave")` para evitar errores (`KeyError`)**: Siempre maneja casos donde una clave opcional no esté presente, usando valores por defecto.
- **Para listas o secuencias, define un agregador que acumule en lugar de sobrescribir**: Por ejemplo, para mensajes, usa `add_messages` para append en lugar de reemplazar la lista entera.

---

## 🧩 Modelo mental

Visualiza el flujo de tu agente como un río de datos:

```
input inicial → [ START ] → (nodo A: procesa) → (nodo B: decide) → ... → [ END ] → output final
                          \________________ estado compartido (dict) ________________/
```

- **Flujo secuencial**: El estado pasa de nodo en nodo como un "paquete" de información.
- **Nodos representan acciones**: Cada nodo puede ser un LLM (razonamiento), una herramienta (búsqueda), una memoria (guardar datos) o lógica personalizada (validaciones).
- **Estado compartido**: Todos los nodos leen del mismo dict y contribuyen cambios. Ejemplo: nodo A agrega `"customer_name"`, nodo B lo usa para personalizar una respuesta.
- **Beneficio**: Evita pasar datos manualmente entre funciones; LangGraph maneja la orquestación automáticamente.

Este modelo hace que el agente sea modular: puedes añadir/remover nodos sin romper el flujo general.

---

## ✅ Buenas prácticas con `dict`

Sigue estas reglas para evitar errores y mantener el estado limpio y predecible.

- **Usa `get` para leer claves opcionales** (evita `KeyError` si la clave no existe):
  ```python
  nombre = state.get("customer_name")          # Devuelve None si no existe
  nombre = state.get("customer_name", "N/A")   # Usa "N/A" como valor por defecto
  edad = state.get("edad", 0)                  # 0 por defecto para números
  ```
  - Razón: El estado puede no tener todas las claves en todo momento; `get` hace tu código robusto.

- **Devuelve solo lo que cambias** (no todo el estado):
  ```python
  return {"customer_name": "John Doe"}  # ✅ Correcto: solo la clave modificada
  # return state  # ❌ Malo: sobreescribe todo, pierde cambios de otros nodos
  ```
  - Razón: LangGraph fusiona cambios; devolver todo causa conflictos o pérdida de datos.

- **Añade claves solo cuando tengas datos válidos**:
  - Verifica si el valor es útil antes de agregarlo (ej. no agregues `None` o strings vacíos).
  - Usa condiciones: `if nombre_valido: return {"customer_name": nombre_valido}`.

Estas prácticas hacen tu grafo eficiente y fácil de depurar.

---

## 🛠️ Definir un **State** tipado

Define el estado como una clase tipada para mayor claridad y validación automática. Esto ayuda a IDEs y evita errores de tipos.

```python
from typing import TypedDict, Sequence, Optional
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class State(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    customer_name: Optional[str]  # Opcional para flexibilidad
    my_age: int
```

- **Imports necesarios**:
  - `TypedDict`: Para definir el estado como un dict con claves tipadas.
  - `Sequence`: Para listas (ej. mensajes).
  - `Annotated`: Para agregar metadatos como agregadores.
  - `add_messages`: Agregador que acumula mensajes (append) en lugar de sobrescribir.

- **Explicación de opciones**:
  - `total=False`: Todas las claves son opcionales; el estado puede no tenerlas todas al inicio.
  - `messages: Annotated[Sequence[BaseMessage], add_messages]`: Lista de mensajes que se acumula automáticamente.
  - `customer_name: Optional[str]`: String opcional (puede ser `None`).
  - `my_age: int`: Entero requerido si se usa.

> `total=False` indica que todas las claves son opcionales, permitiendo estados parciales. `add_messages` permite acumular mensajes a lo largo del grafo sin perder historial.

---

## 🧱 Nodo que actualiza el estado

Los nodos son funciones que toman el estado actual, lo procesan y devuelven cambios. Aquí un ejemplo de nodo que establece un nombre por defecto si falta.

```python
def ensure_name(state: State) -> dict:
    """
    Nodo: Si no hay 'customer_name' en el estado, lo establece a 'John Doe'.
    Si ya existe, no hace cambios (devuelve dict vacío).
    """
    if state.get("customer_name") is None:
        return {"customer_name": "John Doe"}
    return {}  # No cambios necesarios

# Uso en grafo (más adelante)
# builder.add_node("ensure_name", ensure_name)
```

- **Lógica del nodo**:
  - Lee `state.get("customer_name")` (None si no existe).
  - Si falta, devuelve `{"customer_name": "John Doe"}` para actualizar.
  - Si existe, devuelve `{}` (sin cambios).
- **Mejores prácticas**:
  - Usa `get` para evitar `KeyError`.
  - Devuelve solo las claves que modifica (eficiencia).
  - Agrega comentarios/docstrings para claridad.

Este patrón es común para "nodos de inicialización" que preparan el estado para nodos posteriores.

---

## 🤖 Nodo con modelo (Ollama)

Aquí un nodo que integra un LLM local (Ollama) para generar respuestas, usando datos del estado.

```python
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# Cargar variables de entorno
load_dotenv()
MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Instanciar LLM (fuera del nodo para reutilizar)
llm = ChatOllama(model=MODEL, base_url=BASE_URL)

def call_model(state: State) -> dict:
    """
    Nodo: Genera una respuesta del LLM usando el nombre del estado si existe.
    Construye mensajes (system + human) y devuelve la respuesta agregada.
    """
    nombre = state.get("customer_name", "amigo")  # Por defecto "amigo"
    user_text = f"Preséntate y saluda a {nombre}."
    response = llm.invoke([
        SystemMessage(content="Eres un asistente breve y claro."),
        HumanMessage(content=user_text),
    ])
    return {"messages": [response]}  # Agrega al historial

# Uso en grafo
# builder.add_node("llm", call_model)
```

- **Configuración del LLM**:
  - Carga `.env` para `MODEL` y `BASE_URL`.
  - Instancia `ChatOllama` una vez (eficiencia).
- **Lógica del nodo**:
  - Lee `customer_name` con fallback.
  - Construye mensajes: system para estilo, human para consulta.
  - Invoca LLM y devuelve `{"messages": [response]}` para acumular en estado.
- **Por qué funciona**: El agregador `add_messages` en `State` maneja el append automáticamente.

Este nodo es el "corazón" de muchos agentes: razonamiento basado en contexto.

---

## 🕸️ Construcción del grafo con `StateGraph`

Une los nodos en un flujo lógico usando `StateGraph`. Aquí un grafo simple con dos nodos.

```python
from langgraph.graph import StateGraph, START, END

# Crear builder con tu tipo de estado
builder = StateGraph(State)

# Agregar nodos (funciones definidas arriba)
builder.add_node("ensure_name", ensure_name)
builder.add_node("llm", call_model)

# Definir flujo con edges (conexiones)
builder.add_edge(START, "ensure_name")  # Inicio → ensure_name
builder.add_edge("ensure_name", "llm")  # ensure_name → llm
builder.add_edge("llm", END)             # llm → Fin

# Compilar en app ejecutable
app = builder.compile()

# Uso: app.invoke({"messages": [...], ...})
```

- **Builder pattern**: `StateGraph(State)` crea el builder. `add_node` registra funciones.
- **Edges**: `START` y `END` son puntos especiales. Edges definen el flujo secuencial.
- **Compilación**: `app.compile()` genera un objeto invocable con `invoke()`.
- **Flujo resultante**: **START → ensure_name (establece nombre) → llm (responde) → END**.

Este grafo es lineal; en clases futuras añadirás ramas condicionales para decisiones.

---

## ▶️ Probar desde la terminal

Prueba tu grafo directamente desde la terminal para validar que el estado fluya correctamente.

### Prueba directa con `invoke`:
```bash
uv run python -c "from agents.main import app; result = app.invoke({'customer_name': 'Nicolás'}); print(result['messages'][-1].content)"
```
- Invoca el grafo con estado inicial (incluye `customer_name`).
- Accede a la última respuesta en `messages` y extrae el contenido.
- Ejemplo output: "Hola Nicolás, soy un asistente breve y claro."

### Usando una función auxiliar para simplicidad:
Agrega esto a tu `main.py` para pruebas rápidas:
```python
from langchain_core.messages import HumanMessage

def ask(text: str) -> str:
    """
    Helper: Toma texto, lo envuelve en HumanMessage,
    invoca el grafo y devuelve la respuesta.
    """
    result = app.invoke({"messages": [HumanMessage(content=text)]})
    return result["messages"][-1].content

# Prueba en terminal
# uv run python -c "from agents.main import ask; print(ask('Dime algo amable.'))"
```

- **Ventajas**: Envuelve mensajes automáticamente; fácil de usar en scripts.
- **Estado inicial**: Puedes pasar más claves como `{"messages": [...], "customer_name": "Nicolás"}`.

Estas pruebas confirman que el estado se comparte y modifica correctamente entre nodos.

---

## 🗺️ Visualización del grafo (opcional)

Visualiza el flujo de tu grafo para depuración o documentación.

### En consola (ASCII):
Instala la dependencia:
```bash
uv add grandalf --dev
```

Luego, en tu código o terminal:
```python
print(app.get_graph().draw_ascii())
```
- Imprime un diagrama simple como:
  ```
  +-------+     +-----+
  | START | --> | llm |
  +-------+     +-----+
   |
   v
  +-----+
  | END |
  +-----+
  ```
- Útil para grafos pequeños; no requiere herramientas externas.

### En herramientas externas:
- Usa `app.get_graph().draw_mermaid()` y pega en mermaid.live para un diagrama web.
- Para DOT: `app.get_graph().draw_dot()` y renderiza con Graphviz.

Esta visualización ayuda a verificar que el flujo sea el esperado antes de pruebas complejas.

---

## 🧪 Ejercicios prácticos

Practica manipulando el estado con estos ejercicios. Implementa en tu `main.py` y prueba en terminal/Studio.

1. **Modificar nodo existente**: En `ensure_name`, si `customer_name` no existe, define `"John Doe"`; si existe, agrega una nueva clave `my_age = 30`. Prueba invocando con y sin nombre.
2. **Crear clave de lista**: Agrega `facts: list[str]` a `State`. Crea un nodo que agregue un "fact" aleatorio (ej. "El cielo es azul") cada vez. Usa agregador para listas si es necesario.
3. **Nodo intermedio**: Añade un nodo `add_context` que inserte un `SystemMessage` adicional (ej. "Recuerda ser amable") antes del nodo `llm`. Observa cómo afecta el flujo en Studio.

Estos ejercicios refuerzan el manejo de estado y preparación para herramientas/ramas.

---

## 🛟 Errores comunes

Errores típicos al trabajar con estado y cómo evitarlos.

- **KeyError al leer estado**: Ocurre si accedes `state["clave"]` y no existe.
  - Solución: Usa `state.get("clave", "default")` siempre para claves opcionales.
- **Sobrescribir mensajes**: Si reasignas `messages` en lugar de acumular.
  - Solución: Define `messages` con `add_messages` en `State`; devuelve `{"messages": [nuevo_msg]}`.
- **Devolver todo el estado**: Causa pérdida de cambios de otros nodos.
  - Solución: Devuelve solo claves modificadas, ej. `{"customer_name": "John"}`.
- **Imports rotos (ModuleNotFoundError)**: Al importar `agents.main`.
  - Solución: Asegura `__init__.py` en `src/agents/`; reinstala con `uv pip install -e .` tras cambios.

Depura con prints en nodos: `print(f"Estado recibido: {state}")` para rastrear flujo.

---

## ✅ Checklist

Asegúrate de que tu grafo maneje el estado correctamente antes de avanzar.

- [ ] Estado definido como `TypedDict` con `total=False` y claves tipadas (opcionales donde corresponda).
- [ ] Nodos implementados devolviendo solo cambios (dict con claves modificadas).
- [ ] Clave `messages` definida con agregador `add_messages` para acumular historial.
- [ ] Grafo construido con `StateGraph`, nodos agregados y edges definidos (`START → ... → END`).
- [ ] Grafo compilado en `app` y probado exitosamente con `uv run python -c "..."` (respuestas coherentes).
- [ ] (Opcional) Visualización del grafo funcionando con `grandalf` o Mermaid para verificación.

Si todo está marcado, dominas el estado compartido básico.

**Siguiente clase →** Añadiremos **branching** (ramas condicionales) y **tools** (herramientas externas) para que el agente tome decisiones y realice acciones automáticas basadas en el estado.
