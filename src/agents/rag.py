# src/agents/rag.py
"""
RAG (Retrieval-Augmented Generation) Agent with LangGraph.

Este script implementa un agente RAG completamente open source usando Ollama y FAISS.
Incluye chaining avanzado con múltiples nodos para preparación, carga, recuperación,
generación y formateo de respuestas. Inspirado en patrones de agentes no open source,
pero adaptado para herramientas locales y gratuitas.

Características clave:
- Estado compartido con mensajes y contexto.
- Nodos especializados para modularidad.
- Uso de embeddings locales con HuggingFace.
- Integración con Ollama para LLMs locales.
- Comentarios detallados para claridad.
"""

import os
import asyncio
from typing import List, Optional, Dict, Any, Sequence, TypedDict
from typing_extensions import Annotated

# Imports para prompts y parsing
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Imports para vector stores y embeddings (open source)
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ChatOllama: interfaz open source para modelos locales
try:
    from langchain_ollama import ChatOllama  # paquete nuevo
except Exception:
    from langchain_community.chat_models import ChatOllama  # fallback

# Imports para grafos y estado en LangGraph
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages

# -----------------------------------------------------------------------------
# Estado tipado para el grafo RAG
# Inspirado en agentes no open source, agregamos campos para extracción estructurada
# -----------------------------------------------------------------------------
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    """Esquema para extraer información estructurada de conversaciones."""
    name: Optional[str] = Field(description="Nombre de la persona, si se menciona.")
    email: Optional[str] = Field(description="Email, si se proporciona.")
    phone: Optional[str] = Field(description="Teléfono, si se da.")
    tone: Optional[str] = Field(description="Tono: positivo, negativo o neutral, si inferible.")
    age: Optional[int] = Field(description="Edad, si se menciona como número.")

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]  # Historial de mensajes acumulado (requerido para add_messages)
    question: str  # Pregunta del usuario
    context: str  # Contexto recuperado de documentos
    contact_info: Optional[ContactInfo]  # Información extraída estructurada

# -------------------------
# Configuración del agente RAG
# Variables de entorno para flexibilidad (pueden cambiarse en .env)
# -------------------------
FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "data/faiss_index")  # Directorio del índice FAISS
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "index")  # Nombre del índice
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")  # Modelo de embeddings open source

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")  # URL de Ollama
MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")  # Modelo LLM local
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))  # Creatividad del LLM (bajo para precisión)

# -------------------------
# Funciones utilitarias para RAG
# -------------------------
def _format_docs(docs: List[Document]) -> str:
    """Formatea documentos recuperados en un string para el prompt."""
    return "\n\n".join(d.page_content for d in docs) if docs else ""

def _load_embeddings_sync():
    """Carga embeddings de forma síncrona con configuración para evitar errores de CUDA.
    Usa CPU para compatibilidad y evita problemas con GPUs."""
    os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Forzar CPU
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},  # Forzar CPU
        encode_kwargs={'normalize_embeddings': True}  # Normalizar para mejor búsqueda
    )

async def _load_embeddings():
    """Carga embeddings de forma asíncrona para no bloquear el event loop."""
    return await asyncio.to_thread(_load_embeddings_sync)

def _load_retriever_sync(embeddings):
    """Carga el retriever de forma síncrona desde el índice FAISS guardado."""
    idx_path = os.path.join(FAISS_INDEX_DIR)
    faiss_file = os.path.join(idx_path, f"{FAISS_INDEX_NAME}.faiss")
    pkl_file = os.path.join(idx_path, f"{FAISS_INDEX_NAME}.pkl")

    if os.path.exists(faiss_file) and os.path.exists(pkl_file):
        vs = FAISS.load_local(
            idx_path,
            embeddings,
            index_name=FAISS_INDEX_NAME,
            allow_dangerous_deserialization=True,  # Permitir deserialización para cargar índice
        )
        return vs.as_retriever(search_kwargs={"k": 4})  # Top 4 documentos relevantes
    return None  # Si no existe índice, retorna None

async def _load_retriever_if_available():
    """Carga el retriever solo si el índice existe, de forma asíncrona."""
    embeddings = await _load_embeddings()
    return await asyncio.to_thread(_load_retriever_sync, embeddings)

def _get_llm():
    """Obtiene el LLM local con Ollama - inicialización liviana y reutilizable."""
    return ChatOllama(
        model=MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=TEMPERATURE,
    )

# Prompt para el LLM: guía el comportamiento con contexto
PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Eres un asistente RAG open source. Usa únicamente el contexto proporcionado para responder. "
                "Si la respuesta no está en el contexto, dilo explícitamente y no inventes información.\n\n"
                "Contexto:\n{context}"
            ),
        ),
        ("human", "{question}"),
    ]
)

# Caches globales para evitar recargas innecesarias (mejora rendimiento)
_retriever_cache = None
_embeddings_cache = None

def _prepare_inputs(inputs: Any) -> Dict[str, str]:
    """Prepara los inputs asegurando que siempre sean strings válidos."""
    if isinstance(inputs, dict):
        question = inputs.get("question", "")
        if not isinstance(question, str):
            question = str(question)
        return {"question": question}
    else:
        return {"question": str(inputs)}

def _retrieve_context(question: str, retriever) -> str:
    """Ejecuta la recuperación de documentos relevantes para la pregunta."""
    if not retriever or not question:
        return ""
    
    try:
        docs = retriever.invoke(question)  # Recupera top-k documentos
        return _format_docs(docs)
    except Exception as e:
        print(f"Error en recuperación: {e}")
        return ""

def _build_chain_sync(retriever):
    """Construye la cadena RAG de forma síncrona usando RunnableLambda."""
    llm = _get_llm()

    def _prepare_with_retriever(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara inputs incluyendo el retriever para la cadena."""
        prepared = _prepare_inputs(inputs)
        return {
            "question": prepared["question"],
            "retriever": retriever
        }

    def _retrieve_and_format(inputs: Dict[str, Any]) -> Dict[str, str]:
        """Ejecuta la recuperación y formatea los documentos en contexto."""
        question = inputs["question"]
        retriever_obj = inputs.get("retriever")
        context = _retrieve_context(question, retriever_obj)
        return {
            "question": question,
            "context": context
        }

    # Si no hay retriever, cadena simple sin RAG
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
        # Cadena completa con recuperación y generación
        return (
            RunnableLambda(_prepare_with_retriever)
            | RunnableLambda(_retrieve_and_format)
            | PROMPT
            | llm
            | StrOutputParser()
        )

async def _build_chain():
    """Construye la cadena de forma asíncrona, cargando retriever si es necesario."""
    global _retriever_cache
    
    if _retriever_cache is None:
        _retriever_cache = await _load_retriever_if_available()
    
    retriever = _retriever_cache
    return await asyncio.to_thread(_build_chain_sync, retriever)

# Cache para la cadena construida
_chain_cache = None

# -----------------------------------------------------------------------------
# Nodos para el grafo RAG (chaining avanzado: preparar, cargar, recuperar, generar, formatear)
# Inspirado en agentes no open source, agregamos nodos para extracción estructurada y conversación
# -----------------------------------------------------------------------------
def prepare_question(state: State) -> dict:
    """Nodo inicial: prepara la pregunta desde mensajes o input directo.
    Extrae la pregunta del último HumanMessage si no está proporcionada."""
    question = state.get("question", "")
    if not question and state.get("messages"):
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                question = msg.content
                break
    return {"question": question}

def load_retriever(state: State) -> dict:
    """Nodo: carga el retriever si no está en cache global.
    Inicializa embeddings y vector store de forma asíncrona o síncrona según el contexto."""
    global _retriever_cache
    if _retriever_cache is None:
        import asyncio
        try:
            _retriever_cache = asyncio.run(_load_retriever_if_available())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                embeddings = _load_embeddings_sync()
                _retriever_cache = _load_retriever_sync(embeddings)
            else:
                _retriever_cache = asyncio.run(_load_retriever_if_available())
    return {}  # No modifica estado, solo inicializa recursos

def retrieve_context(state: State) -> dict:
    """Nodo: recupera contexto relevante de documentos basado en la pregunta."""
    question = state.get("question", "")
    retriever = _retriever_cache
    context = _retrieve_context(question, retriever)
    return {"context": context}

def generate_response(state: State) -> dict:
    """Nodo: genera la respuesta usando el LLM con contexto recuperado."""
    question = state.get("question", "")
    context = state.get("context", "")
    
    if context:
        full_prompt = f"Contexto:\n{context}\n\nPregunta: {question}"
    else:
        full_prompt = f"Pregunta: {question}"
    
    messages = [HumanMessage(content=full_prompt)]
    llm = _get_llm()
    ai_response = llm.invoke(messages)
    return {"messages": [ai_response]}

def format_response(state: State) -> dict:
    """Nodo final: formatea la respuesta para salida limpia y consistente."""
    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        if isinstance(last_msg, AIMessage):
            content = last_msg.content
            if isinstance(content, str):
                formatted = content.strip()
            else:
                formatted = str(content)
            return {"messages": [AIMessage(content=formatted)]}
    return {}

# -----------------------------------------------------------------------------
# Construir el grafo RAG (chaining avanzado con múltiples nodos especializados)
# Flujo: preparar pregunta -> cargar recursos -> recuperar contexto -> generar respuesta -> formatear salida
# -----------------------------------------------------------------------------
builder = StateGraph(State)
builder.add_node("prepare", prepare_question)  # Prepara la pregunta
builder.add_node("load", load_retriever)  # Carga retriever si necesario
builder.add_node("retrieve", retrieve_context)  # Recupera contexto de docs
builder.add_node("generate", generate_response)  # Genera respuesta con LLM
builder.add_node("format", format_response)  # Formatea la respuesta final

# Definir flujo secuencial con edges
builder.add_edge(START, "prepare")
builder.add_edge("prepare", "load")
builder.add_edge("load", "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", "format")
builder.add_edge("format", END)

# Compilar el grafo en una aplicación ejecutable
app = builder.compile()

# -------------------------
# Funciones de entrada y utilidades (usadas por langgraph.json y pruebas)
# -------------------------
async def async_answer(question: str) -> str:
    """
    Función de entrada asíncrona para procesar preguntas con RAG.
    Construye la cadena una sola vez y la reutiliza para eficiencia.
    """
    global _chain_cache
    
    try:
        if _chain_cache is None:
            _chain_cache = await _build_chain()
        
        chain = _chain_cache
        if not isinstance(question, str):
            question = str(question)
        
        result = await asyncio.to_thread(chain.invoke, {"question": question})
        return result
        
    except Exception as e:
        error_msg = f"Error procesando la pregunta: {str(e)}"
        print(error_msg)
        return f"Lo siento, ocurrió un error al procesar tu pregunta. {error_msg}"

async def clear_cache():
    """Limpia las caches globales para recargar recursos si es necesario."""
    global _retriever_cache, _chain_cache, _embeddings_cache
    _retriever_cache = None
    _chain_cache = None
    _embeddings_cache = None

async def check_index_exists() -> bool:
    """Verifica si el índice FAISS existe en disco."""
    idx_path = os.path.join(FAISS_INDEX_DIR)
    faiss_file = os.path.join(idx_path, f"{FAISS_INDEX_NAME}.faiss")
    pkl_file = os.path.join(idx_path, f"{FAISS_INDEX_NAME}.pkl")
    return os.path.exists(faiss_file) and os.path.exists(pkl_file)