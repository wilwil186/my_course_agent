from typing import TypedDict, Sequence, Optional
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    """Esquema para extraer información estructurada de conversaciones."""
    name: Optional[str] = Field(description="Nombre de la persona, si se menciona.")
    email: Optional[str] = Field(description="Email, si se proporciona.")
    phone: Optional[str] = Field(description="Teléfono, si se da.")
    tone: Optional[str] = Field(description="Tono: positivo, negativo o neutral, si inferible.")
    age: Optional[int] = Field(description="Edad, si se menciona como número.")

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]  # Historial acumulado
    question: str  # Pregunta del usuario
    context: str  # Contexto de RAG
    contact_info: Optional[ContactInfo]  # Datos extraídos
    customer_name: Optional[str]  # Nombre del cliente