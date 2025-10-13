# 🔌 Clase 6: Integración de **OpenAI** y **Anthropic** con LangChain (agnóstico y fácil de cambiar)

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Conectar modelos de distintos proveedores sin reescribir el flujo. Mantener una **API homogénea** (con `invoke`), enviar **historial** (`System/Human/AI`) y alternar proveedor con una sola variable.

---

## 🧠 Arquitectura en una frase
Esta integración crea agentes agnósticos a proveedores, fáciles de cambiar y escalar.

- **LangGraph**: Orquesta el **flujo** del agente mediante grafos (nodos para acciones como razonamiento o tools, edges para transiciones, estado compartido para datos que fluyen entre nodos).
- **LangChain**: Estandariza la **conexión a modelos** (OpenAI, Anthropic, Ollama, etc.), proporcionando una API uniforme (`invoke`) para enviar mensajes y recibir respuestas, independientemente del proveedor.
- **Tú eliges el proveedor** por entorno/variable (ej. `PROVIDER=ollama` en `.env`); el grafo y la lógica **no cambian**, permitiendo alternar entre modelos locales (open-source) y APIs cerradas sin reescribir código.
- **Beneficio clave**: Portabilidad y flexibilidad; prueba con Ollama gratis, despliega con OpenAI si necesitas más poder.

---

## ⚙️ Instalación (dependencias de producción)

Agrega estas librerías a tu proyecto para conectar con proveedores populares. Usa `uv` para gestión limpia.

```bash
# Para proveedores cerrados (APIs pagas)
uv add langchain-openai langchain-anthropic

# (Opcional) Para open-source local (Ollama)
uv add langchain-ollama
```

- **langchain-openai**: Integra modelos de OpenAI (GPT-4, etc.) con API uniforme.
- **langchain-anthropic**: Para modelos de Anthropic (Claude) con misma interfaz.
- **langchain-ollama**: Para modelos locales como Qwen o Llama vía Ollama (100% gratis y privado).
- **Por qué producción**: Estas son estables y usadas en entornos reales; instala solo las que necesites para mantener ligero.

Después de agregar, corre `uv sync` para instalar y actualizar `uv.lock`.

---

## 🔑 Variables de entorno (`.env` y `.env.example`)

Configura proveedores y modelos mediante variables de entorno para flexibilidad y seguridad.

### `.env.example` (plantilla pública, commitea esto)
```env
# Copia a .env y agrega tus claves reales

# OpenAI (API paga, requiere cuenta)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini   # Ej: gpt-4o, gpt-3.5-turbo

# Anthropic (API paga, alternativa a OpenAI)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-latest  # Ej: claude-3-opus-20240229

# Open-source local (Ollama, gratis)
PROVIDER=ollama            # Valores: "openai" | "anthropic" | "ollama"
MODEL=qwen2.5:7b-instruct  # Modelo en Ollama (ollama pull primero)
OLLAMA_BASE_URL=http://localhost:11434  # URL de Ollama (cambia si remoto)

# Hiperparámetros comunes (aplican a todos los proveedores)
TEMPERATURE=0.3  # Creatividad: 0.0=determinista, 1.0=creativo
```

### Carga en código (agrega al inicio de tus archivos)
```python
import os
from dotenv import load_dotenv
load_dotenv()  # Lee .env y pone variables en os.environ

# Ejemplo de uso
provider = os.getenv("PROVIDER", "ollama")
model = os.getenv("MODEL", "qwen2.5:7b-instruct")
```

- **Seguridad**: Nunca commitees `.env` real (agrega a `.gitignore`). Usa `.env.example` para que otros sepan qué necesitan.
- **Flexibilidad**: Cambia proveedor/modelo editando `.env` sin tocar código.
- **Hiperparámetros**: `TEMPERATURE` controla variabilidad; ajusta según necesidades (bajo para tareas precisas, alto para creativas).

> **Buenas prácticas**: nunca imprimas tus claves; usa `assert os.getenv("OPENAI_API_KEY") is not None` si quieres verificar.

---

## 🧾 Tipos de mensajes (recordatorio rápido)

LangChain usa tipos específicos para estructurar conversaciones, asegurando que el LLM entienda roles y contexto.

```python
from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage, BaseMessage
)
```

- **SystemMessage**: Instrucciones del “sistema” (estilo, reglas, contexto inicial). Ej: "Eres un asistente útil y respondes en español." Invisible al usuario, pero guía el comportamiento.
- **HumanMessage**: Entrada de usuario. Ej: "Hola, ¿cómo estás?" Representa la consulta del humano.
- **AIMessage**: Respuesta del modelo. Ej: "¡Hola! Estoy bien, ¿en qué te ayudo?" Lo que el agente "dice".
- **BaseMessage**: Tipo base para listas mixtas. Útil para tipar `list[BaseMessage]` sin especificar.

Estos tipos permiten enviar historial completo al LLM, manteniendo el contexto de la conversación.

---

## 🤝 Enfoque **agnóstico** con un pequeño inicializador

Crea un helper que selecciona proveedor y modelo basado en variables de entorno. Esto permite cambiar de proveedor (OpenAI, Anthropic, Ollama) sin modificar el resto del código, manteniendo el grafo y lógica intactos.

```python
import os
from dotenv import load_dotenv
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama  # Opcional para open-source

# Cargar .env al importar
load_dotenv()

def init_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
):
    """
    Inicializador agnóstico: elige proveedor basado en .env o parámetros.
    Devuelve un LLM listo para usar con API uniforme (invoke).
    """
    provider = (provider or os.getenv("PROVIDER", "ollama")).lower()
    temperature = temperature if temperature is not None else float(os.getenv("TEMPERATURE", "0.3"))
    
    if provider == "openai":
        return ChatOpenAI(
            model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
            # Opcional: api_key=os.getenv("OPENAI_API_KEY") si no usas default
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            model=model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
            temperature=temperature,
        )
    elif provider == "ollama":
        return ChatOllama(
            model=model or os.getenv("MODEL", "qwen2.5:7b-instruct"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=temperature,
        )
    else:
        raise ValueError(f"Proveedor no soportado: {provider}. Usa 'openai', 'anthropic' o 'ollama'.")

# Uso: llm = init_llm()  # Toma de .env
# response = llm.invoke([HumanMessage(content="Hola")])
```

- **Agnóstico**: El mismo código funciona con cualquier proveedor; cambia solo `.env`.
- **API uniforme**: Todos usan `invoke(mensajes)` y devuelven `AIMessage`.
- **Flexibilidad**: Pasa parámetros para override (ej. `init_llm(provider="openai")`).
- **Error handling**: Lanza excepción clara si proveedor inválido.

---

## 🧩 Enviar **historial** (system/human/ai) y mantenerlo en el estado

Envía el historial completo al LLM para contexto, y acumula respuestas en el estado sin perder mensajes previos.

### Definir estado con historial
```python
from typing import TypedDict, Sequence
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages

class State(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]  # Acumula automáticamente
    # Otras claves opcionales: customer_name, etc.
```

- `add_messages`: Agregador que appendea nuevos mensajes al historial existente.

### Nodo que usa historial y responde
```python
llm = init_llm()  # Inicializa con proveedor de .env

def llm_node(state: State) -> dict:
    """
    Nodo: Lee historial, agrega system prompt si falta,
    invoca LLM con contexto completo y devuelve nueva respuesta.
    """
    msgs = list(state.get("messages", []))  # Copia para no mutar

    # Asegura system prompt al inicio (si no existe)
    has_system = any(isinstance(m, SystemMessage) for m in msgs)
    if not has_system:
        msgs = [SystemMessage(content="Eres breve, claro y útil.")] + msgs

    # Invoca LLM con historial completo
    response = llm.invoke(msgs)  # Devuelve AIMessage

    # Devuelve solo lo nuevo (add_messages hará append)
    return {"messages": [response]}

# Agrega a grafo
# builder.add_node("llm", llm_node)
```

- **Por qué funciona**: El LLM recibe todo el contexto (system + historial), permitiendo respuestas coherentes.
- **Acumulación**: `add_messages` evita sobrescritura; cada invocación agrega al final.

### Grafo mínimo y prueba
```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)
builder.add_node("llm", llm_node)
builder.add_edge(START, "llm")
builder.add_edge("llm", END)
app = builder.compile()
```

Prueba en CLI:
```bash
uv run python -c "from agents.main import app; \
from langchain_core.messages import HumanMessage; \
result = app.invoke({'messages': [HumanMessage(content='Dime un tip rápido de Python')]}); \
print(result['messages'][-1].content)"
```

- Output ejemplo: "Usa list comprehensions para código conciso: [x for x in range(10)]."
- Verifica acumulación enviando múltiples mensajes en el mismo thread.

---

## 🧪 Probar **cada proveedor** en segundos

Cambia el proveedor vía variable de entorno y prueba inmediatamente. Asegúrate de tener claves/API configuradas.

### OpenAI (API paga, requiere `OPENAI_API_KEY` en `.env`)
```bash
PROVIDER=openai uv run python -c "from agents.main import app; \
from langchain_core.messages import HumanMessage; \
result = app.invoke({'messages': [HumanMessage(content='Resume esto en 1 línea: List comprehensions')]}); \
print(result['messages'][-1].content)"
```
- Output ejemplo: "List comprehensions son una forma concisa de crear listas en Python usando una expresión."
- Nota: Consume créditos; usa para pruebas rápidas.

### Anthropic (API paga, alternativa, requiere `ANTHROPIC_API_KEY`)
```bash
PROVIDER=anthropic uv run python -c "from agents.main import app; \
from langchain_core.messages import HumanMessage; \
result = app.invoke({'messages': [HumanMessage(content='Explica “decorators” en Python en 1 línea')]}); \
print(result['messages'][-1].content)"
```
- Output ejemplo: "Decorators son funciones que modifican otras funciones agregando comportamiento antes o después de su ejecución."
- Nota: Similar a OpenAI, pero con estilo propio (más "pensativo").

### Ollama (local, open-source, gratis)
```bash
PROVIDER=ollama uv run python -c "from agents.main import app; \
from langchain_core.messages import HumanMessage; \
result = app.invoke({'messages': [HumanMessage(content='¿Qué es un grafo en 1 línea?')]}); \
print(result['messages'][-1].content)"
```
- Output ejemplo: "Un grafo es una estructura de datos compuesta por nodos conectados por aristas."
- Nota: Corre localmente; descarga modelo primero con `ollama pull qwen2.5:7b-instruct`.

Cambia `PROVIDER` en `.env` para hacer permanente el cambio sin comandos largos.

---

## 🧪 Ejemplo directo (sin grafo) para validar instalación

Prueba proveedores directamente (sin LangGraph) para validar que las librerías funcionen.

### OpenAI
```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
resp = llm.invoke([HumanMessage(content="Hola, hola, ¿cómo estás?")])
print(type(resp))   # <class 'langchain_core.messages.ai.AIMessage'>
print(resp.content) # Ej: "¡Hola! Estoy bien, gracias por preguntar. ¿En qué puedo ayudarte?"
```

### Anthropic
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

llm = ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0.3)
resp = llm.invoke([HumanMessage(content="Hola, hola, ¿cómo estás?")])
print(resp.content) # Ej: "Hola, estoy bien. ¿Y tú?"
```

### Ollama
```python
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

llm = ChatOllama(model="qwen2.5:7b-instruct", base_url="http://localhost:11434", temperature=0.3)
resp = llm.invoke([HumanMessage(content="Hola, hola, ¿cómo estás?")])
print(resp.content) # Ej: "¡Hola! Estoy aquí y listo para ayudar."
```

- **Cambio fácil**: Cambiar proveedor es solo cambiar el import y modelo; la API (`invoke`) es idéntica.
- **Validación**: Si falla, verifica claves en `.env` o instalación de Ollama.
- **Uso en grafo**: Usa el inicializador `init_llm()` para integrar en nodos.

---

## 🎛️ Hiperparámetros y contexto
Ajusta estos parámetros para controlar el comportamiento del LLM.

- **temperature**: Controla creatividad/variabilidad.
  - Bajo (0.0-0.3): Respuestas deterministas y precisas (ideal para hechos o código).
  - Alto (0.7-1.0): Más creativo y diverso (bueno para brainstorming).
  - Ejemplo: `ChatOpenAI(temperature=0.1)` para respuestas consistentes.
- **top_p / top_k**: Filtros de sampling (no todos los proveedores lo soportan).
  - `top_p`: Núcleo de probabilidad (ej. 0.9 = usa tokens hasta cubrir 90% de probabilidad).
  - `top_k`: Número de tokens candidatos (ej. 50 = considera solo los 50 más probables).
- **Contexto (historial)**: Envía todo el historial o aplica estrategias.
  - Todo: Máxima coherencia, pero costos altos.
  - Ventana: Últimos N mensajes para reducir tokens.
  - Resumen: Pide al LLM resumir historial periódicamente.

Ajusta basado en tarea: precisión para soporte, creatividad para generación.

---

## 🛟 Troubleshooting

Errores comunes al integrar proveedores y soluciones paso a paso.

- **`ValueError: Proveedor no soportado`**:
  - Causa: `PROVIDER` en `.env` no es "openai", "anthropic" o "ollama".
  - Solución: Revisa `.env` y usa valores válidos; prueba con `init_llm(provider="ollama")` para override.

- **`401/403` (Unauthorized/Forbidden)**:
  - Causa: Clave API inválida o sin permisos.
  - Solución: Verifica `OPENAI_API_KEY` o `ANTHROPIC_API_KEY` en `.env` (copia correcta de dashboard). Revisa límites de cuenta/plan.

- **`429 RateLimitError`**:
  - Causa: Límite de cuota excedido (requests por minuto/hora).
  - Solución: Espera, reduce concurrencia o ajusta plan/billing. Usa Ollama para pruebas ilimitadas.

- **`Model not found`**:
  - Causa: Nombre de modelo incorrecto en `.env`.
  - Solución: Valida `OPENAI_MODEL` (ej. "gpt-4o-mini") o `ANTHROPIC_MODEL` (ej. "claude-3-5-sonnet-latest"). Lista modelos en dashboard.

- **Ollama no responde**:
  - Causa: Ollama no corriendo o URL incorrecta.
  - Solución: Inicia `ollama serve` en terminal. Verifica `OLLAMA_BASE_URL` (default: http://localhost:11434). Descarga modelo con `ollama pull`.

- **Mensajes se borran** (historial perdido):
  - Causa: No usas `add_messages` o devuelves todo el estado.
  - Solución: Define `messages` con `add_messages` en `State`; devuelve solo `{"messages": [nuevo]}`.

Prueba con ejemplos directos primero para aislar problemas de grafo.

---

## ✅ Checklist

Verifica que la integración funcione correctamente antes de avanzar.

- [ ] Dependencias instaladas: `langchain-openai` y/o `langchain-anthropic` (y `langchain-ollama` para local).
- [ ] Variables en `.env` configuradas (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `PROVIDER`, modelos, `TEMPERATURE`).
- [ ] Helper `init_llm` implementado y probado; `invoke` devuelve `AIMessage` con contenido válido.
- [ ] Grafo mínimo integrado (nodo con `llm_node`) y probado en CLI (respuestas coherentes).
- [ ] Probado en LangGraph Studio (cambia `PROVIDER` y verifica respuestas).
- [ ] Historial en estado con `add_messages` (mensajes se acumulan sin borrarse).
- [ ] Ejemplos directos funcionando para cada proveedor (sin grafo).

Si todo está marcado, puedes cambiar proveedores fácilmente.

**Siguiente clase →** Branching y tools: cómo añadir decisiones condicionales (ramas) y herramientas externas (búsqueda, cálculo, I/O) para agentes más inteligentes.
