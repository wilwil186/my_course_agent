import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, MessagesState, START, END

# 1) Cargar .env
load_dotenv()

# 2) Instanciar LLM local vía Ollama (100% open source)
#    Usa variables MODEL y OLLAMA_BASE_URL desde el .env
llm = ChatOllama(
    model=os.getenv("MODEL", "qwen2.5:7b-instruct"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)

# 3) Nodo que llama al modelo
def call_model(state: MessagesState):
    """Recibe la lista de mensajes y devuelve la respuesta del LLM."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 4) Definir el grafo de LangGraph
builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_edge(START, "model")
builder.add_edge("model", END)

# 5) Compilar el grafo
app = builder.compile()

# 6) Helper para invocar en código/CLI
def ask(text: str) -> str:
    messages: List[BaseMessage] = [
        SystemMessage(content="Eres un asistente útil que contesta de forma breve y clara."),
        HumanMessage(content=text),
    ]
    result = app.invoke({"messages": messages})
    return result["messages"][-1].content