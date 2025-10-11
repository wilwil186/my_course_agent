# src/agents/main.py
import os
from typing import TypedDict, List
from langchain_core.messages import AnyMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_ollama import ChatOllama

# =========================
# 1️⃣ Estado del grafo
# =========================
class State(TypedDict):
    messages: List[AnyMessage]


# =========================
# 2️⃣ Definimos tools
# =========================
@tool
def add(a: int, b: int) -> int:
    """Suma dos números."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiplica dos números."""
    return a * b

tools = [add, multiply]


# =========================
# 3️⃣ Modelo Ollama (Qwen)
# =========================
llm = ChatOllama(
    model=os.getenv("MODEL", "qwen2.5:7b-instruct"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=0.2,
)

# Importantísimo: permitirle usar tools
llm = llm.bind_tools(tools)


# =========================
# 4️⃣ Nodo del agente
# =========================
def agent(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}


# =========================
# 5️⃣ Construcción del grafo
# =========================
builder = StateGraph(State)

builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")

# Condición: si el modelo pide usar una tool, ir al nodo "tools"
builder.add_conditional_edges(
    "agent",
    tools_condition,
    {"tools": "tools", "__end__": END},
)

# Cuando acaba una tool, vuelve al agente
builder.add_edge("tools", "agent")

# Compilamos el grafo
app = builder.compile()
