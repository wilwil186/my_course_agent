# src/agents/rag.py
import os
import asyncio
from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ChatOllama: usa el paquete disponible
try:
    from langchain_ollama import ChatOllama  # paquete nuevo
except Exception:
    from langchain_community.chat_models import ChatOllama  # fallback

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

def _load_retriever_if_available():
    """Carga el retriever sólo si el índice existe. Si no, devuelve None (no rompe el server)."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

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

def _get_llm():
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

def _build_chain():
    retriever = _load_retriever_if_available()
    llm = _get_llm()

    def _prepare(inputs):
        # Asegura que siempre trabajamos con un string (evita el error .replace sobre dict)
        q = inputs["question"] if isinstance(inputs, dict) else str(inputs)
        if retriever:
            docs = retriever.get_relevant_documents(q)
            ctx = _format_docs(docs)
        else:
            ctx = ""  # sin índice todavía: el LLM responderá sin contexto
        return {"question": q, "context": ctx}

    return RunnableLambda(_prepare) | PROMPT | llm | StrOutputParser()

# -------------------------
# Punto de entrada (usado por langgraph.json)
# -------------------------
async def async_answer(question: str) -> str:
    """
    Entrada asíncrona simple para LangGraph API.
    No realiza cargas pesadas al importar el módulo.
    """
    chain = _build_chain()
    # Ejecuta en thread para no bloquear el loop si el conector hace I/O
    return await asyncio.to_thread(chain.invoke, {"question": question})
