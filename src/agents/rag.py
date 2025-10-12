# src/agents/rag.py
from __future__ import annotations

import os
import asyncio
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_core.tools import tool, Tool

# =====================================================
# Configuración base
# =====================================================
load_dotenv()

LLM_MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMB_MODEL_NAME = os.getenv("EMB_MODEL_NAME", "intfloat/multilingual-e5-small")

# Rutas
HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[2]
PDF_PATH = REPO_ROOT / "PDF" / "9587014499.PDF"
INDEX_DIR = REPO_ROOT / ".rag_index" / "faiss-e5-small"

# Chunking / Retrieval
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
TOP_K = int(os.getenv("TOP_K", "4"))

# Locks de inicialización
_VECSTORE_LOCK = asyncio.Lock()
_EMB_LOCK = asyncio.Lock()

# Caches globales
_VS: FAISS | None = None
_EMB: HuggingFaceEmbeddings | None = None


# =====================================================
# Construcción de componentes
# =====================================================
def _build_embeddings() -> HuggingFaceEmbeddings:
    """Crea los embeddings con HuggingFace en CPU (evita conflictos con Ollama GPU)."""
    return HuggingFaceEmbeddings(
        model_name=EMB_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


async def _get_embeddings() -> HuggingFaceEmbeddings:
    """Devuelve un singleton de embeddings (thread-safe)."""
    global _EMB
    if _EMB is not None:
        return _EMB
    async with _EMB_LOCK:
        if _EMB is not None:
            return _EMB
        _EMB = await asyncio.to_thread(_build_embeddings)
        return _EMB


def _make_llm() -> ChatOllama:
    """Inicializa el modelo LLM de Ollama."""
    return ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.2)


@lru_cache(maxsize=1)
def _prompt_template():
    """Prompt de sistema preconfigurado (cacheado)."""
    system = (
        "Eres un asistente que responde EXCLUSIVAMENTE con el contexto proporcionado. "
        "Si la respuesta no está en el contexto, dilo claramente. Responde en español."
    )
    return ChatPromptTemplate.from_messages([
        ("system", system),
        ("human",
         "Pregunta: {question}\n\n"
         "Contexto (fragmentos del PDF):\n{context}\n\n"
         "Responde de forma directa y cita brevemente la(s) página(s) si aplica.")
    ])


# =====================================================
# Indexación y retrieval
# =====================================================
async def _ensure_index() -> FAISS:
    """Carga o construye el índice FAISS a partir del PDF."""
    global _VS
    if _VS is not None:
        return _VS

    async with _VECSTORE_LOCK:
        if _VS is not None:
            return _VS

        emb = await _get_embeddings()
        await asyncio.to_thread(INDEX_DIR.mkdir, parents=True, exist_ok=True)

        faiss_exists = (INDEX_DIR / "index.faiss").exists() and (INDEX_DIR / "index.pkl").exists()
        if faiss_exists:
            def _load():
                return FAISS.load_local(INDEX_DIR, emb, allow_dangerous_deserialization=True)
            _VS = await asyncio.to_thread(_load)
            return _VS

        def _build_from_pdf():
            loader = PyPDFLoader(str(PDF_PATH))
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["\n\n", "\n", ".", " ", ""],
            )
            chunks = splitter.split_documents(docs)
            vs = FAISS.from_documents(chunks, emb)
            vs.save_local(INDEX_DIR)
            return vs

        _VS = await asyncio.to_thread(_build_from_pdf)
        return _VS


def _format_docs(docs: List[Document]) -> str:
    """Formatea los documentos recuperados para pasarlos al prompt."""
    out = []
    for i, d in enumerate(docs, 1):
        meta = d.metadata or {}
        page = meta.get("page", "?")
        out.append(f"[{i}] (pág. {page}) {d.page_content.strip()}")
    return "\n\n".join(out)


# =====================================================
# Cadena RAG
# =====================================================
async def _make_chain():
    vs = await _ensure_index()
    retriever = vs.as_retriever(search_kwargs={"k": TOP_K})
    prompt = _prompt_template()
    llm = _make_llm()

    chain = (
        {
            "context": retriever | _format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


# =====================================================
# API principal
# =====================================================
async def async_answer(question: str) -> str:
    """Responde de forma asíncrona; apto para servidores ASGI (LangGraph API)."""
    chain = await _make_chain()
    return await asyncio.to_thread(chain.invoke, {"question": question})


def answer(question: str) -> str:
    """Wrapper sincrónico (para compatibilidad con langgraph.json)."""
    return asyncio.run(async_answer(question))


# =====================================================
# Integración con herramientas LangGraph
# =====================================================
@tool("rag_search", return_direct=False)
async def rag_search(question: str) -> str:
    """Herramienta (async) para integrar en agentes LangGraph."""
    return await async_answer(question)


def get_rag_tool() -> Tool:
    """Devuelve el Tool para incluir en el agente."""
    return rag_search


# =====================================================
# Ejecución directa
# =====================================================
if __name__ == "__main__":
    print("RAG listo. PDF:", PDF_PATH)
    print(asyncio.run(async_answer("¿Cuál es el tema principal del documento?")))
