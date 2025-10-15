# Clase 11 — Organización de Código en LangGraph para Sistemas Complejos de AI

**Objetivo:** Aprender a estructurar proyectos de agentes de IA con LangGraph de forma modular y escalable, separando responsabilidades en carpetas y archivos claros. Esto facilita el mantenimiento, la escalabilidad y la colaboración en sistemas con múltiples nodos, prompts y herramientas, usando herramientas open source como Ollama.

---

## 🧠 ¿Por Qué Organizar el Código para Escalar en LangGraph?
Cuando un proyecto crece con múltiples nodos, prompts, RAGs y herramientas, mantener todo en un solo archivo se vuelve caótico. Una estructura modular mejora:

- **Mantenibilidad:** Localizar y editar un nodo es rápido y aislado.
- **Escalabilidad:** Agregar nodos o herramientas no rompe el código existente.
- **Claridad:** Cada componente (estado, grafo, nodos, prompts, herramientas) tiene su lugar.
- **Visibilidad:** El flujo del agente es fácil de entender y depurar.

Esta organización transforma agentes simples en sistemas complejos y profesionales, listos para producción.

---

## 🔑 Conceptos Básicos
Ideas clave para estructurar proyectos de agentes.

- **Agente como Carpeta:** Cada agente (ej. "support") se convierte en una carpeta con subcarpetas para nodos.
- **Separación de Responsabilidades:** Estado, grafo, nodos, prompts y herramientas en archivos dedicados.
- **Imports Claros:** Rutas explícitas como `from agents.support.state import State`.
- **Herramientas Open Source:** Usa Ollama para LLMs locales, evitando APIs propietarias.

---

## ✅ Requisitos
- Proyecto con LangGraph instalado (como en clases anteriores).
- uv para gestión de dependencias.
- Ollama corriendo para modelos locales.

---

## 🗂️ Estructura Sugerida del Proyecto
Convierte un agente monolítico en una estructura modular.

### Estructura de Carpetas para un Agente "Support"
```
agents/
  support/
    __init__.py              # Hace que 'support' sea un paquete
    state.py                 # Definición del estado compartido
    agent.py                 # Construcción del grafo del agente
    nodes/
      __init__.py            # Paquete para nodos
      extractor/
        __init__.py          # Paquete para extractor
        node.py              # Lógica del nodo extractor
        prompt.py            # System prompt para extractor
      conversation/
        __init__.py          # Paquete para conversation
        node.py              # Lógica del nodo conversation
        prompt.py            # System prompt para conversation
        tools.py             # Herramientas específicas del nodo
```

- **Estado Centralizado:** `state.py` define el TypedDict compartido.
- **Grafo en `agent.py`:** Importa estado y nodos, construye el StateGraph.
- **Nodos Modulares:** Cada nodo en su carpeta con lógica, prompt y herramientas.
- **Imports Limpios:** Usa rutas absolutas como `from agents.support.state import State`.

---

## ⚙️ Ejemplo Práctico: Refactorizar un Agente Simple
Supongamos un agente básico con extractor y conversation. Lo refactorizamos a la estructura modular.

### Paso 1: Definir el Estado (`state.py`)
```python
from typing import TypedDict, Sequence
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]  # Historial acumulado
    question: str  # Pregunta del usuario
    context: str  # Contexto de RAG
    contact_info: Optional[ContactInfo]  # Datos extraídos (de clase anterior)
```

- **Explicación:** El estado es compartido entre nodos. Usa `add_messages` para acumular mensajes automáticamente.

### Paso 2: Prompt por Nodo (`nodes/extractor/prompt.py`)
```python
# System prompt específico para el nodo extractor
SYSTEM_PROMPT = (
    "Eres un asistente que extrae información de contacto de conversaciones. "
    "Si no encuentras un dato, no lo inventes. Usa null para campos no presentes."
)
```

- **Ventajas:** Prompts aislados por nodo, fáciles de editar y reutilizar.

### Paso 3: Nodo Extractor (`nodes/extractor/node.py`)
```python
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from ..state import State  # Import relativo al estado
from .prompt import SYSTEM_PROMPT

llm = ChatOllama(model="qwen2.5:7b-instruct", temperature=0)

def extract_info(state: State) -> dict:
    """Nodo: Extrae información estructurada del historial."""
    messages = list(state.get("messages", []))
    if not messages:
        return {}
    
    full_messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm.invoke(full_messages)
    # Asume uso de with_structured_output como en clase anterior
    return {"contact_info": response}  # Adaptar según implementación
```

- **Explicación:** Cada nodo tiene su propio LLM y lógica. Usa imports relativos para claridad.

### Paso 4: Herramientas por Nodo (`nodes/conversation/tools.py`)
```python
# Herramientas específicas para el nodo conversation (open source)
from langchain_community.tools import DuckDuckGoSearchRun

tools = [DuckDuckGoSearchRun()]  # Ejemplo: búsqueda web gratuita
```

- **Ventajas:** Herramientas agrupadas por nodo, inyectadas solo donde se necesitan.

### Paso 5: Nodo Conversation (`nodes/conversation/node.py`)
```python
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from ..state import State
from .prompt import SYSTEM_PROMPT
from .tools import tools

llm = ChatOllama(model="llama3.1:8b", temperature=0.3)
llm_with_tools = llm.bind_tools(tools)

def conversation(state: State) -> dict:
    """Nodo: Responde usando contexto y herramientas."""
    question = state.get("question", "")
    context = state.get("context", "")
    
    if context:
        full_prompt = f"Contexto: {context}\nPregunta: {question}"
    else:
        full_prompt = question
    
    messages = [HumanMessage(content=full_prompt)]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}
```

- **Explicación:** Integra herramientas y prompts de forma modular.

### Paso 6: Construir el Agente (`agent.py`)
```python
from langgraph.graph import StateGraph, START, END
from .state import State
from .nodes.extractor.node import extract_info
from .nodes.conversation.node import conversation

builder = StateGraph(State)
builder.add_node("extract", extract_info)
builder.add_node("converse", conversation)

builder.add_edge(START, "extract")
builder.add_edge("extract", "converse")
builder.add_edge("converse", END)

app = builder.compile()
```

- **Explicación:** El grafo importa nodos modulares y define el flujo.

---

## 📏 Buenas Prácticas para Organización
Consejos para mantener y escalar el proyecto.

- **Un Agente, Una Carpeta:** Cada agente en su directorio para navegación fácil.
- **Estado Centralizado:** Un solo `state.py` con el TypedDict compartido.
- **Nodos Autocontenidos:** Cada nodo con su lógica, prompt y herramientas.
- **LLM por Nodo:** Declara el modelo en cada nodo para flexibilidad (usa Ollama para open source).
- **Prompts Declarativos:** Un archivo `prompt.py` por nodo con el system prompt.
- **Herramientas Agrupadas:** Exporta arrays de herramientas por nodo.
- **Imports Explícitos:** Usa rutas claras para evitar errores.
- **Refactor Incremental:** Mueve estado primero, luego nodos, prompts y herramientas.
- **Pruebas Continuas:** Usa LangGraph Studio para validar el flujo después de cambios.

---

## 🧪 Ejercicios Prácticos
Practica refactorizando un agente simple.

1. **Crear Carpeta para Agente:** Toma un agente de clases anteriores y conviértelo en carpeta con estado y nodos.
2. **Agregar Prompt por Nodo:** Separa el system prompt en archivos dedicados.
3. **Integrar Herramientas:** Agrega herramientas open source (ej. búsqueda web) a un nodo específico.

Estos ejercicios preparan para proyectos reales escalables.

---

## ✅ Checklist
- [ ] Proyecto estructurado con carpetas por agente y nodos.
- [ ] Estado definido en `state.py` y compartido.
- [ ] Nodos modulares con prompts y herramientas separados.
- [ ] Grafo construido en `agent.py` con imports claros.
- [ ] Probado en LangGraph Studio (flujo funciona después de refactor).

Si todo está marcado, tu proyecto está organizado para escalar.

---

## 📚 Recursos Open Source
- [LangGraph Application Structure Docs](https://python.langchain.com/docs/langgraph/application-structure/)
- [Ollama para Modelos Locales](https://ollama.ai/)
- [LangChain Community Tools](https://python.langchain.com/docs/integrations/tools/)

---

## 🤔 Preguntas para Reflexionar
- ¿Qué nodo modularizarías primero en tu proyecto y por qué?
- ¿Cómo mejorarías esta estructura para agentes con múltiples herramientas?
- ¿Qué beneficios ves en usar modelos locales como Ollama para esta organización?

**Siguiente clase →** Patrones avanzados de agentes con memoria y herramientas externas.

