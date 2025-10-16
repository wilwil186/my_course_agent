from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.support.state import State  # Import absoluto
from src.agents.support.nodes.extractor.prompt import SYSTEM_PROMPT

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