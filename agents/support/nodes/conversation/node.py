from agents.support.state import State
from langchain.chat_models import init_chat_model
from agents.support.nodes.conversation.tools import tools
from agents.support.nodes.conversation.prompt import prompt_template
from langchain_core.messages import AIMessage

llm = init_chat_model("ollama:qwen2.5:7b-instruct", temperature=0.3)
llm = llm.bind_tools(tools)

def conversation(state: State):
    """Nodo: Responde usando contexto y herramientas."""
    new_state: State = {}
    history = state["messages"]
    last_message = history[-1]
    customer_name = state.get("customer_name", "Usuario")
    context = state.get("context", "")
    
    # Formatear el prompt con el nombre del cliente
    prompt = prompt_template.format(name=customer_name, context=context)
    
    print('*' * 100)
    print(last_message.content)
    
    # Invocar el LLM con el prompt del sistema y el mensaje del usuario
    ai_message = llm.invoke([("system", prompt), ("user", last_message.content)])
    ai_message = AIMessage(content=ai_message.content)
    
    new_state["messages"] = [ai_message]
    return new_state