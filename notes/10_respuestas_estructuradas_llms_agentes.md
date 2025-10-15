# Clase 10 — Respuestas Estructuradas en LLMs para Agentes

**Objetivo:** Aprender a controlar las respuestas de los LLMs usando salidas estructuradas (structured output) con Pydantic y LangChain, enfocándonos en herramientas open source como Ollama. Esto permite extraer datos confiables de conversaciones para usar en agentes con LangGraph, mejorando precisión y control.

---

## 🧠 ¿Por Qué Estructurar Respuestas de LLMs?
Controlar cómo responde un modelo de lenguaje es esencial para agentes que toman decisiones seguras. Pasar de respuestas libres a estructuradas transforma texto impredecible en datos útiles, como nombres, emails o sentimientos, que puedes evaluar y usar en código.

- **Problema con respuestas libres:** Dependiendo del tono, longitud o temperatura, las respuestas varían mucho, lo que complica su uso en agentes.
- **Solución con structured output:** Fuerza al modelo a devolver un objeto JSON con un esquema claro (usando Pydantic), facilitando operaciones en el grafo del agente.
- **Beneficios:**
  - **Evaluación programática:** Extrae variables como nombre, email o tono para decisiones automáticas.
  - **Decisiones en agentes:** Un nodo puede ramificar basado en datos consistentes.
  - **Más que chat:** El modelo actúa como extractor confiable, no solo conversador.

Esto reduce impredecibilidad y costos al evitar respuestas ambiguas.

---

## 🔑 Conceptos Básicos
Ideas clave para implementar structured output de forma efectiva.

- **Structured Output:** Técnica para que el LLM devuelva datos en un formato predefinido (ej. JSON con campos específicos), usando esquemas como Pydantic.
- **Pydantic:** Librería Python para definir modelos de datos con validación automática. Traduce clases a esquemas JSON para el LLM.
- **Integración con LangChain:** Usa `with_structured_output()` en modelos como ChatOllama para forzar respuestas estructuradas.
- **Ventajas sobre JSON mode antiguo:** Más robusto y nativo en modelos modernos, sin depender de modos obsoletos.

---

## ✅ Requisitos
- Python ≥ 3.11
- uv instalado
- Ollama corriendo (para modelos locales open source)
- Dependencias: `uv add langchain langchain-ollama pydantic`

---

## ⚙️ Implementación Básica con Ollama
Crea un extractor que use structured output para extraer información de una conversación.

### Definir el Esquema con Pydantic
```python
from pydantic import BaseModel, Field
from typing import Optional

class ContactInfo(BaseModel):
    name: Optional[str] = Field(description="Nombre de la persona, si se menciona explícitamente.")
    email: Optional[str] = Field(description="Email, si se proporciona.")
    phone: Optional[str] = Field(description="Teléfono, si se da.")
    tone: Optional[str] = Field(description="Tono de la conversación: positivo, negativo o neutral.")
    age: Optional[int] = Field(description="Edad, si se menciona como número entero.")
```

- **Explicación:** Cada campo tiene una descripción clara para guiar al LLM. Usa `Optional` para campos que pueden no estar presentes.

### Configurar el LLM con Structured Output
```python
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()
MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

llm = ChatOllama(model=MODEL, base_url=BASE_URL)
llm_structured = llm.with_structured_output(ContactInfo)
```

- **Ventajas open source:** Usa Ollama para modelos locales, sin costos ni datos externos.

### Usar el Extractor en Código
```python
from langchain_core.messages import HumanMessage, SystemMessage

# Mensajes de ejemplo
messages = [
    SystemMessage(content="Extrae información de contacto de la conversación siguiente el esquema."),
    HumanMessage(content="Hola, me llamo Juan, tengo 25 años y mi email es juan@example.com. Estoy emocionado por este curso.")
]

# Invocar el LLM estructurado
response = llm_structured.invoke(messages)
print(response)  # ContactInfo(name='Juan', email='juan@example.com', tone='positivo', age=25)
```

- **Cómo funciona:** El LLM recibe el esquema y devuelve un objeto Pydantic validado. Puedes acceder a campos directamente: `response.name`.

---

## 🛠️ Integración en un Agente con LangGraph
Agrega un nodo extractor a tu grafo para extraer datos y usarlos en otros nodos.

### Estado con Datos Extraídos
```python
from typing import TypedDict, Sequence
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class State(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    contact_info: Optional[ContactInfo]  # Datos extraídos
```

### Nodo Extractor
```python
def extract_info(state: State) -> dict:
    """Nodo: Extrae información estructurada del historial."""
    messages = list(state.get("messages", []))
    if not messages:
        return {}
    
    # Agregar system prompt para extracción
    system_msg = SystemMessage(content="Extrae información de contacto de la conversación. Si no encuentras un dato, no lo inventes.")
    full_messages = [system_msg] + messages
    
    # Invocar LLM estructurado
    response = llm_structured.invoke(full_messages)
    return {"contact_info": response}
```

### Nodo que Usa los Datos
```python
def respond_with_info(state: State) -> dict:
    """Nodo: Responde usando datos extraídos."""
    contact = state.get("contact_info")
    name = contact.name if contact else "usuario"
    
    user_msg = next((m for m in reversed(state.get("messages", [])) if isinstance(m, HumanMessage)), None)
    if user_msg:
        response = f"Hola {name}, gracias por tu mensaje: '{user_msg.content}'. ¿En qué más te ayudo?"
        return {"messages": [AIMessage(content=response)]}
    return {}
```

### Construir el Grafo
```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)
builder.add_node("extract", extract_info)
builder.add_node("respond", respond_with_info)

builder.add_edge(START, "extract")
builder.add_edge("extract", "respond")
builder.add_edge("respond", END)

app = builder.compile()
```

- **Flujo:** START → extract (extrae datos) → respond (usa datos en respuesta) → END.
- **Beneficios:** Datos consistentes fluyen entre nodos, mejorando personalización.

---

## 📏 Buenas Prácticas
Consejos para evitar errores comunes en structured output.

- **Evita alucinaciones:** En el system prompt, agrega "Si no encuentras el dato en la conversación, devuelve null o vacío. No inventes."
- **Maneja validaciones:** Usa tipos flexibles (Optional) para campos no obligatorios. Prueba con datos reales.
- **Optimiza costos:** Ejecuta el extractor solo cuando sea necesario (ej. si falta info o historial largo).
- **Pruebas:** Usa ejemplos variados para validar el esquema. Ajusta descripciones si el modelo falla.
- **Open source focus:** Siempre usa Ollama o modelos Hugging Face para mantener privacidad y cero costos.

---

## 🧪 Ejercicios Prácticos
Practica con estos ejercicios para reforzar conceptos.

1. **Esquema personalizado:** Crea un esquema para extraer "producto" y "precio" de mensajes de compra. Integra en un nodo de agente.
2. **Manejo de errores:** Modifica el extractor para manejar casos donde el LLM devuelve datos inválidos (usa try/except con Pydantic).
3. **Extracción condicional:** Agrega lógica para extraer solo si el historial tiene >5 mensajes.

Estos ejercicios preparan para agentes más robustos.

---

## ✅ Checklist
- [ ] Esquema Pydantic definido con campos claros y descripciones.
- [ ] LLM configurado con `with_structured_output()`.
- [ ] Nodo extractor integrado en grafo LangGraph.
- [ ] Probado con mensajes reales (respuestas válidas y consistentes).
- [ ] Errores comunes mitigados (alucinaciones, validaciones).

Si todo está marcado, dominas structured output en agentes open source.

---

## 📚 Recursos Open Source
- [LangChain Structured Output Docs](https://python.langchain.com/docs/how_to/structured_output/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Ollama para Modelos Locales](https://ollama.ai/)

---

## 🤔 Preguntas para Reflexionar
- ¿Cómo mejorarías el esquema para evitar alucinaciones en tus agentes?
- ¿Dónde aplicarías structured output en proyectos reales?
- ¿Qué otros datos estructurados extraerías de conversaciones?

**Siguiente clase →** Más patrones avanzados de agentes con herramientas y memoria.

