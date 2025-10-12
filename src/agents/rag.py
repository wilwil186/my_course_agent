# src/agents/rag.py
# -*- coding: utf-8 -*-
"""
RAG minimal y robusto para LangGraph API.

Arregla el bug:
AttributeError: 'dict' object has no attribute 'replace'
causado porque el retriever recibía un dict en lugar de un string.

Puntos clave del fix:
- El retriever SOLO recibe la cadena de la pregunta (itemgetter("question")).
- Wrapper defensivo por si invoke recibe un dict u otro tipo.
- Mantiene la interfaz async_answer(question: str) usada por el resto del proyecto.
"""

from __future__ import annotations

import os
import asyncio
from typing import Any, Dict, Union
from operator import itemgetter

# LangChain core
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# Vector store + embeddings
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

# LLM (ajusta si usas otro proveedor)
# Si usas OpenAI oficial, asegúrate de tener OPENAI_API_KEY en el entorno.
from langchain_openai import ChatOpenAI


# ----------------------------
# Configuración
# ----------------------------

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "data/faiss_index")  # cambia a tu ruta
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "4"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# ----------------------------
# Utilidades
# ----------------------------

def _get_embeddings() -> HuggingFaceEmbeddings:
    # Usa el mismo modelo que empleaste al indexar.
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def _load_vectorstore() -> FAISS:
    embeddings = _get_embeddings()
    # allow_dangerous_deserialization=True es habitual al cargar FAISS local
    return FAISS.load_local(
        FAISS_INDEX_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )


def _get_retriever():
    vs = _load_vectorstore()
    return vs.as_retriever(search_type="similarity", k=RETRIEVER_K)


def _get_llm():
    # Ajusta aquí si usas otro proveedor (Ollama, Azure, etc.)
    # Este constructor requiere OPENAI_API_KEY en el entorno.
    return ChatOpenAI(model=OPENAI_MODEL, temperature=0)


def _get_prompt() -> ChatPromptTemplate:
    system = (
        "Eres un asistente que responde de forma concisa y cita hechos "
        "solo desde el CONTEXTO si aplica. Si la respuesta no está en el "
        "contexto, di que no tienes suficiente información."
    )
    user = (
        "PREGUNTA: {question}\n\n"
        "CONTEXTO:\n{context}\n\n"
        "RESPONDE:"
    )
    return ChatPromptTemplate.from_messages(
        [("system", system), ("user", user)]
    )


def _extract_question(x: Union[str, Dict[str, Any]]) -> str:
    """
    Wrapper defensivo: acepta dict o str y devuelve la pregunta como str.
    Evita que el retriever reciba un dict (causa del AttributeError).
    """
    if isinstance(x, dict):
        # Lo común en tu código: {"question": "..."}
        if "question" in x:
            return str(x["question"])
        # Si viene con otra clave, intenta una heurística simple:
        for k in ("query", "input", "prompt"):
            if k in x:
                return str(x[k])
        # Último recurso: repr
        return str(x)
    return str(x)


# ----------------------------
# Construcción del RAG chain (LCEL)
# ----------------------------

# Componentes
_retriever = _get_retriever()
_llm = _get_llm()
_prompt = _get_prompt()
_parser = StrOutputParser()

# Runnable que garantiza string para el retriever/prompt
_to_question = RunnableLambda(_extract_question)

# Mapa de entrada -> {context, question}
# CLAVE DEL FIX: el retriever recibe itemgetter("question") pasando por _to_question.
RAG_CHAIN = (
    {
        "context": itemgetter("question") | _to_question | _retriever,
        "question": itemgetter("question") | _to_question,
    }
    | _prompt
    | _llm
    | _parser
)


# ----------------------------
# API pública
# ----------------------------

def answer(question: str) -> str:
    """
    Versión síncrona por si se necesita en otros sitios.
    """
    return RAG_CHAIN.invoke({"question": question})


async def async_answer(question: str) -> str:
    """
    Interfaz usada por LangGraph API en tu proyecto (según el stacktrace).
    Mantiene la misma firma, pero ahora el retriever recibe correctamente un string.
    """
    return await asyncio.to_thread(RAG_CHAIN.invoke, {"question": question})


# ----------------------------
# Modo script (opcional)
# ----------------------------

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "¿Qué hay en el índice?"
    print(answer(q))
