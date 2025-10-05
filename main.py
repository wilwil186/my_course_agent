# pip install -U langchain-community python-dotenv

# >>> Igual que en el curso:
# from langchain.agents import create_agent   # (ya no existe)
# En su lugar, dejamos un "shim" para que el código luzca igual.

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List, Dict, Any
import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage

load_dotenv()

# ------------------------------
# Config: modelo local (Ollama)
# ------------------------------
MODEL = os.getenv("MODEL", "qwen2.5:7b-instruct")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ------------------------------
# Tool de ejemplo (idéntica)
# ------------------------------
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


# ----------------------------------------------------
# Pequeño "shim" para imitar create_agent del curso
# ----------------------------------------------------
@dataclass
class _MiniAgent:
    llm: ChatOllama
    tools: List[Callable[..., str]]
    prompt: str

    def _maybe_call_tool(self, text: str) -> str | None:
        """
        Router ultra simple: si detecta 'weather' o 'clima',
        intenta extraer la ciudad y llama la tool get_weather.
        """
        low = text.lower()
        if "weather" in low or "clima" in low:
            city = "San Francisco"
            # extracción super básica para demo
            for token in [" in ", " de ", " en ", " para "]:
                if token in low:
                    city = text.split(token, 1)[1].strip().strip(".?!")
                    break
            # Buscar tool compatible por nombre
            for f in self.tools:
                if f.__name__ == "get_weather":
                    return f(city)
        return None

    def invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Imitamos la firma del curso:
        agent.invoke({"messages": [{"role":"user","content":"..."}]})
        """
        msgs = payload.get("messages", [])
        if isinstance(msgs, str):
            user_text = msgs
        else:
            user_text = msgs[-1]["content"] if msgs else "Hello!"

        # 1) Intento de tool
        tool_answer = self._maybe_call_tool(user_text)
        if tool_answer is not None:
            return {"output": tool_answer}

        # 2) Llamada al LLM local (Ollama)
        sys_prefix = f"{self.prompt}\n\n" if self.prompt else ""
        result = self.llm.invoke([HumanMessage(content=sys_prefix + user_text)])
        return {"output": result.content}


def create_agent(model: str, tools: List[Callable[...,]()]()_
