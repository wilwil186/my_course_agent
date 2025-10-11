# src/agents/simple.py
"""
Agente simple 100% open-source con LangGraph + LangChain (Ollama).
Funciona con `uv run langgraph dev` y también permite probar con la función ask().

Requisitos en .env:
  MODEL=qwen2.5:7b-instruct
  OLLAMA_BASE_URL=http://localhost:11434
  TEMPERATURE=0.2  # opcional
"""

from __future__ import annotations

import os
from typing import Optional, Sequence, TypedDict
from typing_extensions import Annotated  # <— IMPORTANTE

from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages

# -----------------------------------------------------------------------------
# Cargar entorno
# -----------------------------------------------------------------------------
load_dotenv()
MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

# -----------------------------------------------------------------------------
# Estado tipado con agregador de mensajes
# -----------------------------------------------------------------------------
class State(TypedDict, total=False):
    # LangGraph necesita Annotated real (no string) para detectar el canal messages
    messages: Annotated[Sequence[BaseMessage], add_messages]
    customer_name: Optional[str]
    turn_count: int

# -----------------------------------------------------------------------------
# LLM local (solo OSS)
# -----------------------------------------------------------------------------
llm = ChatOllama(model=MODEL, base_url=BASE_URL, temperature=TEMPERATURE)

SYSTEM_BASE = (
    "Eres un asistente útil y conciso. "
    "Si el usuario no ha compartido su nombre, pídeselo con amabilidad. "
    "Usa el nombre si está disponible para personalizar tus respuestas."
)

# -----------------------------------------------------------------------------
# Nodos
# -----------------------------------------------------------------------------
def ensure_name(state: State) -> dict:
    """
    Extrae de forma simple un nombre si el último HumanMessage contiene 'me llamo X'.
    (Ejemplo mínimo; no es NER real.)
    """
    history = state.get("messages", [])
    last_human = next((m for m in reversed(history) if isinstance(m, HumanMessage)), None)
    if last_human:
        text = str(last_human.content).lower()
        if "me llamo" in text:
            # Toma la primera palabra después de 'me llamo'
            name = text.split("me llamo", 1)[1].strip(" .,:;!?\n\t").split()[0].title()
            if name:
                return {"customer_name": name}
    return {}

def router(state: State) -> str:
    """Si no hay nombre → 'ask_name'; si ya hay → 'reason'."""
    return "ask_name" if not state.get("customer_name") else "reason"

def ask_name(state: State) -> dict:
    """Agrega un mensaje de la IA pidiendo el nombre (no pisa historial)."""
    return {"messages": [AIMessage(content="¿Cómo te llamas?")]}

def reason(state: State) -> dict:
    """
    Llama al LLM con SystemMessage + historial. Devuelve solo lo nuevo.
    Si el historial viene vacío, inyecta un prompt mínimo para evitar errores.
    """
    name = state.get("customer_name")
    system_text = SYSTEM_BASE + (f" El usuario se llama {name}." if name else "")
    history = list(state.get("messages", []))
    if not history:
        history = [HumanMessage(content="Hola, ¿me puedes saludar?")]

    msgs = [SystemMessage(content=system_text)] + history
    ai_reply = llm.invoke(msgs)  # -> AIMessage
    turn = state.get("turn_count", 0) + 1
    return {"messages": [ai_reply], "turn_count": turn}

# -----------------------------------------------------------------------------
# Grafo
# -----------------------------------------------------------------------------
builder = StateGraph(State)
builder.add_node("ensure_name", ensure_name)
builder.add_node("ask_name", ask_name)
builder.add_node("reason", reason)

builder.add_edge(START, "ensure_name")
builder.add_conditional_edges("ensure_name", router, {
    "ask_name": "ask_name",
    "reason": "reason",
})
builder.add_edge("ask_name", END)
builder.add_edge("reason", END)

# Importante: NO usar checkpointer aquí (langgraph dev maneja persistencia)
app = builder.compile()

# -----------------------------------------------------------------------------
# Helper para CLI/tests
# -----------------------------------------------------------------------------
def ask(text: str, thread_id: str = "local-demo") -> str:
    """
    Envía un turno de conversación y devuelve el último texto de la IA.
    Con langgraph dev, la persistencia por thread la maneja el servidor.
    """
    result = app.invoke(
        {"messages": [HumanMessage(content=text)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    last = result["messages"][-1]
    return getattr(last, "content", str(last))

__all__ = ["app", "ask", "State"]
