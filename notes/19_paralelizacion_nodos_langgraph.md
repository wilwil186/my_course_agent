# Paralelización de Nodos en Agentes con LangGraph

## Curso para Crear Agentes de AI con LangGraph - Clase 19

### Resumen
Acelera la respuesta de tu agente dividiendo el problema en pasos independientes y ejecutándolos a la vez. Con el patrón de paralelización, varios nodos corren en paralelo y un nodo final, el aggregator, condensa todo en una única salida confiable. Así evitas esperas innecesarias y resultados duplicados.

### ¿Qué es el patrón de paralelización y cómo acelera a tu agente?
La paralelización permite que un agente envíe tareas a varios workers o nodos simultáneamente. A diferencia de chaining (secuencial) y routing (elige uno u otro), aquí se ejecutan varios caminos a la vez desde un mismo origen.

- Divide un problema en pasos que no dependen entre sí.
- Ejecuta nodos en paralelo en lugar de en secuencia.
- Usa un nodo final aggregator para condensar respuestas.

### ¿En qué se diferencia de chaining y routing?
- En chaining: un nodo tras otro, paso a paso.
- En routing: el grafo decide entre un camino u otro, no ambos.
- En paralelización: se ejecutan varios nodos al mismo tiempo y luego se unen los resultados.

### ¿Cómo definir nodos, edges y el rol del aggregator?
Para obligar la ejecución en paralelo, se elimina el edge que conecta de forma opcional un nodo con otro y se especifica explícitamente que, desde un nodo origen, se debe ir a dos destinos. Por ejemplo: desde el nodo 1 se va al nodo 2 y al nodo 3 a la vez. Ambos son obligatorios.

- Declara que desde el nodo origen se dispara al nodo 2 y al nodo 3 en paralelo.
- Haz que los nodos 2 y 3 apunten al aggregator.
- El aggregator condensa todo y emite el end.

En la visualización del grafo, los caminos obligatorios aparecen con línea sólida, mientras que los condicionales suelen verse como líneas punteadas. Esto señala que el flujo sí o sí pasará por esos nodos paralelos.

```python
from langgraph.graph import StateGraph, START, END

def node_1(state):
    return state

def node_2(state):
    # Proceso independiente
    return {"result": "Resultado de node_2"}

def node_3(state):
    # Proceso independiente
    return {"result": "Resultado de node_3"}

def aggregator(state):
    # Condensar resultados
    return {"final": f"Combinado: {state}"}

builder = StateGraph(dict)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
builder.add_node("aggregator", aggregator)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_1", "node_3")
builder.add_edge("node_2", "aggregator")
builder.add_edge("node_3", "aggregator")
builder.add_edge("aggregator", END)

agent = builder.compile()
```

### ¿Por qué es crítico el aggregator?
Porque, si los nodos en paralelo finalizaran con end por su cuenta, el agente podría intentar responder al usuario dos veces a la vez. El aggregator espera a que todos los nodos terminen, recopila sus salidas y produce una única respuesta final.

### ¿Cómo se refleja en el grafo ASCII la obligatoriedad?
- Línea sólida: camino obligatorio hacia el siguiente nodo.
- Línea punteada: camino condicional que depende de decisiones previas.
- Paralelización: múltiples líneas sólidas desde un mismo origen a varios nodos.

### ¿Cuándo iniciar varios nodos desde start y qué cuidar?
También es posible enviar varios nodos en paralelo directamente desde start. Por ejemplo: start dispara el nodo 1, el nodo 2 y el nodo 3 al mismo tiempo. Luego, todos convergen en el aggregator y de ahí se pasa al end.

- Desde start puedes lanzar múltiples nodos a la vez.
- Todos deben converger en un único aggregator.
- La salida final debe ser una sola: el end.
Para que funcione bien, los nodos paralelos deben ser independientes: ninguno debe esperar datos de otro. El aggregator resume y decide la respuesta final tras recibir todo.

### Lecturas recomendadas
- [Workflows and agents - Docs by LangChain](https://python.langchain.com/docs/langgraph/)

### Comentarios
¿Listo para aplicar paralelización? Comparte en comentarios qué escenarios independientes se te ocurren que puedan correr en paralelo y cómo condensarías sus resultados con un aggregator.