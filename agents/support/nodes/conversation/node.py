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