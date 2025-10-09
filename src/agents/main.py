# main.py
# Agente ReAct con LangGraph + Ollama (Qwen) + wrapper para input vacío (Studio)

import os
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, END
from langchain_core.messages import HumanMessage


# --------- Herramienta de ejemplo ----------
@tool
def get_weather(city: str) -> str:
    """Devuelve el clima de una ciudad (demo simple)."""
    return f"El clima en {city} siempre es soleado ☀️"


# --------- LLM local (Ollama) ----------
MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
llm = ChatOllama(model=MODEL, base_url=OLLAMA_BASE_URL)

# Grafo base (prebuilt ReAct)
base_agent = create_react_agent(llm, tools=[get_weather])

# --------- Wrapper: asegura tener al menos 1 mensaje ---------
def ensure_input(state: MessagesState):
    """Si Studio llama sin mensajes, inyecta un 'Hola' por defecto."""
    if not state.get("messages"):
        return {"messages": [HumanMessage("Hola")]}
    return {}

# Construir app final exportable para LangGraph CLI/Studio
g = StateGraph(MessagesState)
g.add_node("ensure_input", ensure_input)
g.add_node("agent", base_agent)  # puedes pasar el runnable directo como nodo
g.set_entry_point("ensure_input")
g.add_edge("ensure_input", "agent")
g.add_edge("agent", END)
app = g.compile()   # <--- ESTE es el grafo que exponemos a LangGraph


# --------- Helper para uso por terminal (python main.py) ----------
def ask(question: str) -> str:
    """Invoca al grafo y devuelve solo el texto final."""
    result = app.invoke({"messages": [{"role": "user", "content": question}]})
    last = result["messages"][-1]
    content = getattr(last, "content", last)
    if isinstance(content, list):
        return "".join(p.get("text", "") for p in content if isinstance(p, dict))
    return content


if __name__ == "__main__":
    q = "¿Cuál es el clima en Bogotá?"
    print(f"\n💬 Usuario: {q}")
    print("\n🟢 Respuesta del agente:")
    print(ask(q))
