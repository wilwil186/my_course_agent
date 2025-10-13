# src/agents/rag.py
import os
import asyncio
from typing import List, Optional, Dict, Any, Sequence, TypedDict
from typing_extensions import Annotated

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ChatOllama: usa el paquete disponible
try:
    from langchain_ollama import ChatOllama  # paquete nuevo
except Exception:
    from langchain_community.chat_models import ChatOllama  # fallback

from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages

# -----------------------------------------------------------------------------
# Estado tipado para el grafo RAG
# -----------------------------------------------------------------------------
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    question: str
    context: str

# -------------------------
# Config
# -------------------------
FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "data/faiss_index")
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "index")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

# -------------------------
# Utils
# -------------------------
def _format_docs(docs: List[Document]) -> str:
    return "\n\n".join(d.page_content for d in docs) if docs else ""

def _load_embeddings_sync():
    """Carga embeddings de forma síncrona con configuración para evitar errores de CUDA"""
    # Forzar CPU para evitar problemas con meta tensors
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},  # Forzar CPU
        encode_kwargs={'normalize_embeddings': True}
    )

async def _load_embeddings():
    """Carga embeddings de forma asíncrona"""
    return await asyncio.to_thread(_load_embeddings_sync)

def _load_retriever_sync(embeddings):
    """Carga el retriever de forma síncrona"""
    idx_path = os.path.join(FAISS_INDEX_DIR)
    faiss_file = os.path.join(idx_path, f"{FAISS_INDEX_NAME}.faiss")
    pkl_file = os.path.join(idx_path, f"{FAISS_INDEX_NAME}.pkl")

    if os.path.exists(faiss_file) and os.path.exists(pkl_file):
        vs = FAISS.load_local(
            idx_path,
            embeddings,
            index_name=FAISS_INDEX_NAME,
            allow_dangerous_deserialization=True,
        )
        return vs.as_retriever(search_kwargs={"k": 4})
    return None

async def _load_retriever_if_available():
    """Carga el retriever sólo si el índice existe."""
    embeddings = await _load_embeddings()
    return await asyncio.to_thread(_load_retriever_sync, embeddings)

def _get_llm():
    """Obtiene el LLM - esta inicialización es liviana"""
    return ChatOllama(
        model=MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=TEMPERATURE,
    )

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Eres un asistente RAG. Usa únicamente el contexto cuando esté presente. "
                "Si la respuesta no está en el contexto, dilo explícitamente.\n\n"
                "Contexto:\n{context}"
            ),
        ),
        ("human", "{question}"),
    ]
)

# Cache para el retriever y embeddings
_retriever_cache = None
_embeddings_cache = None

def _prepare_inputs(inputs: Any) -> Dict[str, str]:
    """Prepara los inputs asegurando que siempre sean strings"""
    if isinstance(inputs, dict):
        question = inputs.get("question", "")
        # Asegurar que question es string
        if not isinstance(question, str):
            question = str(question)
        return {"question": question}
    else:
        # Si no es dict, convertirlo a string
        return {"question": str(inputs)}

def _retrieve_context(question: str, retriever) -> str:
    """Ejecuta la recuperación de documentos"""
    if not retriever or not question:
        return ""
    
    try:
        # Usar invoke en lugar del método deprecated
        docs = retriever.invoke(question)
        return _format_docs(docs)
    except Exception as e:
        print(f"Error en recuperación: {e}")
        return ""

def _build_chain_sync(retriever):
    """Construye la cadena de forma síncrona"""
    llm = _get_llm()

    def _prepare_with_retriever(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara inputs incluyendo el retriever"""
        prepared = _prepare_inputs(inputs)
        return {
            "question": prepared["question"],
            "retriever": retriever
        }

    def _retrieve_and_format(inputs: Dict[str, Any]) -> Dict[str, str]:
        """Ejecuta la recuperación y formatea los documentos"""
        question = inputs["question"]
        retriever_obj = inputs.get("retriever")
        
        context = _retrieve_context(question, retriever_obj)
        
        return {
            "question": question,
            "context": context
        }

    # Si no hay retriever, usar cadena simple sin RAG
    if not retriever:
        def _simple_chain(inputs: Dict[str, Any]) -> Dict[str, str]:
            prepared = _prepare_inputs(inputs)
            return {
                "question": prepared["question"],
                "context": ""
            }
        return (
            RunnableLambda(_simple_chain) 
            | PROMPT 
            | llm 
            | StrOutputParser()
        )
    else:
        # Cadena completa con RAG
        return (
            RunnableLambda(_prepare_with_retriever)
            | RunnableLambda(_retrieve_and_format)
            | PROMPT
            | llm
            | StrOutputParser()
        )

async def _build_chain():
    """Construye la cadena de forma asíncrona"""
    global _retriever_cache
    
    # Cargar retriever una sola vez y cachearlo
    if _retriever_cache is None:
        _retriever_cache = await _load_retriever_if_available()
    
    retriever = _retriever_cache
    
    # Construir la cadena síncrona en un thread
    return await asyncio.to_thread(_build_chain_sync, retriever)

# Cache para la cadena
_chain_cache = None

# -----------------------------------------------------------------------------
# Nodos para el grafo RAG
# -----------------------------------------------------------------------------
def retrieve_context(state: State) -> dict:
    """Nodo para recuperar contexto basado en la pregunta"""
    global _retriever_cache
    
    # Inicializar retriever si no está cargado
    if _retriever_cache is None:
        import asyncio
        try:
            _retriever_cache = asyncio.run(_load_retriever_if_available())
        except RuntimeError:
            # Si ya hay un event loop corriendo, usar to_thread
            loop = asyncio.get_event_loop()
            if loop.is_running():
                embeddings = _load_embeddings_sync()
                _retriever_cache = _load_retriever_sync(embeddings)
            else:
                _retriever_cache = asyncio.run(_load_retriever_if_available())
    
    question = state.get("question", "")
    retriever = _retriever_cache
    
    context = _retrieve_context(question, retriever)
    
    return {"context": context}

def generate_response(state: State) -> dict:
    """Nodo para generar la respuesta usando el LLM"""
    question = state.get("question", "")
    context = state.get("context", "")
    
    # Construir el prompt con contexto
    if context:
        full_prompt = f"Contexto:\n{context}\n\nPregunta: {question}"
    else:
        full_prompt = f"Pregunta: {question}"
    
    # Crear mensajes para el LLM
    messages = [HumanMessage(content=full_prompt)]
    
    # Obtener respuesta del LLM
    llm = _get_llm()
    ai_response = llm.invoke(messages)
    
    return {"messages": [ai_response]}

# -----------------------------------------------------------------------------
# Construir el grafo RAG
# -----------------------------------------------------------------------------
builder = StateGraph(State)
builder.add_node("retrieve", retrieve_context)
builder.add_node("generate", generate_response)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

# Compilar el grafo
app = builder.compile()

# -------------------------
# Punto de entrada (usado por langgraph.json)
# -------------------------
async def async_answer(question: str) -> str:
    """
    Entrada asíncrona simple para LangGraph API.
    """
    global _chain_cache
    
    try:
        # Construir la cadena una sola vez
        if _chain_cache is None:
            _chain_cache = await _build_chain()
        
        chain = _chain_cache
        
        # Asegurar que la pregunta es string
        if not isinstance(question, str):
            question = str(question)
        
        # Ejecutar la cadena
        result = await asyncio.to_thread(
            chain.invoke, 
            {"question": question}
        )
        
        return result
        
    except Exception as e:
        # Manejo de errores robusto
        error_msg = f"Error procesando la pregunta: {str(e)}"
        print(error_msg)
        return f"Lo siento, ocurrió un error al procesar tu pregunta. {error_msg}"

# Función opcional para limpiar la cache si es necesario
async def clear_cache():
    """Limpia la cache del retriever y la cadena"""
    global _retriever_cache, _chain_cache, _embeddings_cache
    _retriever_cache = None
    _chain_cache = None
    _embeddings_cache = None

# Función para verificar si el índice existe
async def check_index_exists() -> bool:
    """Verifica si el índice FAISS existe"""
    idx_path = os.path.join(FAISS_INDEX_DIR)
    faiss_file = os.path.join(idx_path, f"{FAISS_INDEX_NAME}.faiss")
    pkl_file = os.path.join(idx_path, f"{FAISS_INDEX_NAME}.pkl")
    return os.path.exists(faiss_file) and os.path.exists(pkl_file)