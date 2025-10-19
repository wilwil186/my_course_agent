# Clase 13: Patrón ReAct para Agentes que Razonan y Ejecutan Tools

**Objetivo:** Aprender a implementar el patrón ReAct (Reason and Act) en agentes con LangGraph, integrando razonamiento y ejecución de herramientas en ciclos controlados. Este patrón se basa en conceptos previos como respuestas estructuradas (Clase 10), organización modular del código (Clase 11) y prompts dinámicos (Clase 12) para crear agentes más precisos y útiles.

---

## 🧠 ¿Por Qué el Patrón ReAct Potencia Agentes con Tools?

El patrón ReAct integra razonamiento y acciones en un bucle iterativo, permitiendo al agente analizar, actuar con herramientas, observar resultados y decidir si continuar o finalizar. Construye sobre las bases establecidas en clases anteriores:

- **Respuestas Estructuradas (Clase 10):** Usa structured output con Pydantic para formatear salidas de herramientas, asegurando datos confiables que el agente puede evaluar programáticamente.
- **Organización Modular (Clase 11):** Estructura el agente en nodos separados (ej. razonamiento, ejecución de tools, observación) para mantenibilidad y escalabilidad.
- **Prompts Dinámicos (Clase 12):** Emplea PromptTemplate y Jinja2 para prompts adaptativos que guían el razonamiento y la selección de tools según el contexto.

Esto evita separar el "pensar" de la "acción", creando un ciclo virtuoso que mejora decisiones y contrasta con chains secuenciales al permitir bifurcaciones y routers en un grafo.

---

## 🔑 Conceptos Básicos

Ideas clave para implementar ReAct efectivamente.

- **Bucle Iterativo:** Une razonamiento y acciones en ciclos controlados con máximo de iteraciones para evitar loops infinitos.
- **Independencia de Proveedor:** Define tus propias tools; no depende de APIs propietarias.
- **Integración con LangGraph:** Orquesta el flujo en grafo, facilitando nodos, edges y ruteo. Combina con LangChain para utilidades como `create_agent`.
- **Modelos Razonadores:** Requiere modelos con capacidades de razonamiento (ej. GPT-4, Gemini 2.5 Pro Thinking, Claude Opus) para planificar y decidir.

---

## ✅ Requisitos

- Python ≥ 3.11
- uv instalado
- Ollama corriendo (para modelos locales open source)
- Dependencias: `uv add langchain langchain-ollama pydantic langgraph`

---

## ⚙️ Implementación Básica con Ollama

Crea un agente ReAct que razona, ejecuta tools y observa resultados.

### Definir el Estado (Basado en Clase 11)

```python
from typing import TypedDict, Sequence
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class State(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    question: str
    tool_results: Optional[list]  # Resultados de tools estructurados (Clase 10)
```

### Prompt Dinámico para Razonamiento (Basado en Clase 12)

```python
from langchain.prompts import PromptTemplate

reason_template = """\
Eres un agente que razona paso a paso antes de actuar.
Objetivo: {objetivo}
Pregunta del usuario: {question}
{% if tool_results -%}
Resultados previos de tools: {{ tool_results }}
{%- endif %}
Decide si llamar una tool o responder directamente.
"""

prompt_tmpl = PromptTemplate(
    template=reason_template,
    input_variables=["objetivo", "question"],
    partial_variables={"tool_results": None},
    template_format="jinja2"
)
```

### Nodos Modulares (Basado en Clase 11)

#### Nodo de Razonamiento

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen2.5:7b-instruct", temperature=0)

def reason_node(state: State) -> dict:
    """Nodo: Razona sobre la siguiente acción."""
    objetivo = "Resolver la consulta del usuario usando tools si es necesario."
    question = state.get("question", "")
    tool_results = state.get("tool_results", [])
    
    prompt = prompt_tmpl.format(
        objetivo=objetivo,
        question=question,
        tool_results=tool_results if tool_results else None
    )
    
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    return {"messages": [response]}
```

#### Nodo de Ejecución de Tools

```python
from langchain_community.tools import DuckDuckGoSearchRun

tools = [DuckDuckGoSearchRun()]

llm_with_tools = llm.bind_tools(tools)

def tool_node(state: State) -> dict:
    """Nodo: Ejecuta tools basadas en razonamiento."""
    messages = list(state.get("messages", []))
    response = llm_with_tools.invoke(messages)
    # Usa structured output para formatear resultados (Clase 10)
    return {"tool_results": [response], "messages": [response]}
```

#### Nodo de Observación y Decisión

```python
def observe_node(state: State) -> dict:
    """Nodo: Observa resultados y decide si continuar o finalizar."""
    # Lógica para evaluar si el objetivo se cumplió
    if "suficiente" in str(state.get("tool_results", [])):
        return {"final_response": "Objetivo cumplido."}
    return {"continue": True}
```

### Construir el Grafo

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)
builder.add_node("reason", reason_node)
builder.add_node("tool", tool_node)
builder.add_node("observe", observe_node)

builder.add_edge(START, "reason")
builder.add_conditional_edges("reason", lambda x: "tool" if "tool" in x else "observe")
builder.add_edge("tool", "observe")
builder.add_conditional_edges("observe", lambda x: END if x.get("final_response") else "reason")

app = builder.compile()
```

- **Flujo:** START → reason → (tool u observe) → (observe o reason) → END.

---

## 📏 Buenas Prácticas

Consejos para implementar ReAct efectivamente.

- **Control de Iteraciones:** Limita ciclos para evitar costos excesivos.
- **Prompts Claros:** Usa técnicas de Clase 12 para guiar razonamiento.
- **Estructura Modular:** Sigue organización de Clase 11 para escalabilidad.
- **Modelos Adecuados:** Elige modelos razonadores para mejor desempeño.
- **Pruebas:** Usa LangGraph Studio para validar flujos.

---

## 🧪 Ejercicios Prácticos

1. **Agregar Structured Output:** Integra Pydantic en tool_results para formatear datos (Clase 10).
2. **Prompt Condicional:** Usa Jinja2 para variar prompts según tool_results (Clase 12).
3. **Escalar Nodos:** Agrega más nodos siguiendo estructura de Clase 11.

---

## ✅ Checklist

- [ ] Patrón ReAct implementado con bucle iterativo.
- [ ] Integración con structured output (Clase 10).
- [ ] Código organizado modularmente (Clase 11).
- [ ] Prompts dinámicos usados (Clase 12).
- [ ] Probado en LangGraph Studio.

---

## 📚 Recursos

- [LangGraph ReAct Pattern Docs](https://python.langchain.com/docs/langgraph/)
- [Ollama para Modelos Locales](https://ollama.ai/)

---

## 🤔 Preguntas para Reflexionar

- ¿Cómo combinarías ReAct con RAG de clases anteriores?
- ¿Qué tools agregarías a un agente ReAct para tareas reales?

**Siguiente clase →** Más patrones avanzados de agentes.

