# Enrutamiento de Agentes con Conditional Edge en LangGraph

## Curso para Crear Agentes de AI con LangGraph - Clase 17

### Resumen
¿Quieres que tus agentes decidan por sí mismos y deriven la conversación al flujo correcto? Aquí verás cómo aplicar el patrón de routing con conditional edge para integrar un booking agent en una arquitectura con nodos, estado compartido y un grafo modular. Basado en un flujo real con REACT, tools y chain, entenderás qué decide el agente y qué controlas tú, enfocándote en herramientas open source como Ollama.

### ¿Qué es routing en agentes y por qué importa?
El patrón de routing permite que un agente elija el siguiente paso sin seguir un camino rígido. En un soporte con chain, extractor y conversation, este enfoque habilita enviar al usuario a un booking agent cuando desea “reservar una cita”, o mantenerlo en el agente de conversation (con un RAG con Ollama) cuando no necesita agendamiento. Esa capacidad de bifurcar el flujo, con reglas controladas por ti, hace que el sistema sea flexible y eficiente.

### ¿Qué diferencia hay entre nodos y edges?
- Nodos: actualizan el estado o generan nuevos estados en la memoria compartida.
- Edges: solo derivan hacia otros nodos. No actualizan el estado.
Ambos pueden leer el estado, pero solo el nodo lo persiste. Un edge de routing devuelve los nodos posibles a los que puede enviar, con su tipado correspondiente.

### ¿Cómo se decide a dónde ir?
- Por lógica programada y técnicas de prompt.
- Por datos en la memoria compartida.
- Por salida del language model o uso de tools.
- Por azar, usando un umbral de random (por ejemplo, -0.5) para elegir entre dos nodos.

### ¿Cómo implementar un conditional edge en tu grafo?
Primero se replica el patrón de prompt chain en un notebook: nodo inicial, nodo 1, nodo 2, nodo 3 y nodo final. Luego se introduce una función tipo “route edge” cuyo objetivo es decidir el siguiente nodo y retornar los destinos posibles. Esa función puede leer el estado, pero no lo modifica.

```python
from langgraph.graph import StateGraph
from langchain_ollama import OllamaLLM

# Ejemplo de función de routing
def route_edge(state):
    if state.get("intent") == "book_appointment":
        return "booking"
    else:
        return "conversation"

# Definir el grafo con conditional edge
builder = StateGraph(State)
builder.add_node("start", start_node)
builder.add_node("booking", booking_node)
builder.add_node("conversation", conversation_node)
builder.add_conditional_edges("start", route_edge, {"booking": "booking", "conversation": "conversation"})
builder.set_finish_points(["booking", "conversation"])
```

### ¿Qué pasos componen la integración en el builder?
- Agregar un conditional edge en el builder como pieza de routing.
- Definir el flujo: start → nodo 1 → routing (conditional edge) → nodo 2 o nodo 3.
- Quitar conexiones directas innecesarias entre nodos cuando el edge ya decide el destino.
- Hacer que nodo 2 y nodo 3 terminen en end.
Al compilar y graficar, el conditional edge no se dibuja; verás aristas a los nodos destino, y solo se tomará uno de ellos.

### ¿Qué reglas clave debes recordar?
- El edge puede acceder al estado, pero no lo actualiza.
- El nodo es el único responsable de persistir cambios en la memoria compartida.
- El flujo resultante crea bifurcaciones claras y controladas.

### ¿Puede el nodo start derivar directamente con routing?
Sí. No siempre necesitas un “nodo 1” antes de derivar. Se puede conectar el nodo start directamente a un conditional edge y, desde ahí, enviar al nodo 2 o nodo 3 para finalizar. Este patrón es útil cuando el enrutador analiza toda la conversación desde el inicio y decide el mejor camino sin procesamiento intermedio.

### ¿Qué te permite este patrón desde el inicio?
- Evaluar la intención del usuario al primer paso.
- Enviar de inmediato al booking agent si pide “reservar una cita”.
- Mantener al usuario en conversation con un RAG con Ollama si no requiere agendamiento.
- Reducir complejidad cuando un edge inicial puede tomar decisiones robustas.

### ¿Qué reto práctico puedes intentar ahora?
- Derivar a cuatro nodos en lugar de tres.
- Cambiar la lógica del routing edge: reemplazar random por reglas basadas en memoria.
- Colocar routing en otros nodos: por ejemplo, que el nodo 2 derive a más destinos.
Comparte tu gráfico en los comentarios y cuéntame qué flujos de conversación estás creando.

### Lecturas recomendadas
- [Agents - Docs by LangChain](https://python.langchain.com/docs/modules/agents/)
- [Graph API overview - Docs by LangChain](https://python.langchain.com/docs/langgraph/)

### Comentarios
¿Te gustaría comentar cómo integrar este patrón con Ollama y qué validaciones agregarías para un flujo open source?
