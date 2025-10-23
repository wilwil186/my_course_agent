# Routing Inteligente con LLM para Derivar Conversaciones Automáticamente

## Curso para Crear Agentes de AI con LangGraph - Clase 18

### Resumen
Construye un agente que decide por sí mismo a qué nodo enviar cada turno. Con el patrón de routing en LangGraph y un structured output guiado por un language model open source como Ollama, el flujo se deriva de forma fiable a conversation o booking. Verás cómo integrar un subgrafo React node, usar memoria compartida y depurar errores comunes sin añadir complejidad innecesaria.

### ¿Cómo implementar routing con structured output en LangGraph?
Para que el agente tome decisiones autónomas, se añade un router entre el extractor y los nodos finales. El router llama al LLM con un prompt breve y devuelve un esquema tipado que indica el siguiente paso: conversation o booking. Así, cada mensaje se encamina al nodo correcto.

### ¿Qué nodos y flujo define el grafo?
- Inicio, extractor y memoria compartida. El extractor guarda datos útiles del historial en el estado común.
- Intent route. Un nodo de enrutamiento que decide el destino con structured output.
- Conversation node. Maneja preguntas generales con respuesta directa o con RAG cuando aplica.
- Booking node. Agente con patrón React, representado como subgrafo con agent, tools y finalizar.
- End. Ambos caminos convergen al cierre del flujo.

### ¿Cómo se construye el intent route con un LLM?
Se define un esquema tipado para el paso siguiente con Pydantic: conversation o booking.
Se pasa al LLM el historial completo más un system prompt que explica cuándo ir a cada nodo.
Se establece un valor por defecto: si no hay decisión clara, ir a conversation.
Los nombres deben coincidir exactamente con los nodos del grafo: errores de nombre impiden el ruteo correcto.

```python
from typing import Literal
from pydantic import BaseModel
from langchain_ollama import OllamaLLM

class IntentDecision(BaseModel):
    step: Literal["conversation", "booking"] | None = None

SYSTEM_PROMPT = (
    "Eres un asistente que enruta al paso adecuado: 'conversation' para preguntas generales, "
    "'booking' si el usuario habla de citas o appointments."
)

def intent_route(messages, llm: OllamaLLM):
    decision = llm.with_structured_output(schema=IntentDecision)(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages  # historial completo
        ]
    )
    if decision is not None and decision.step is not None:
        return decision.step
    return "conversation"  # por defecto
```

### ¿Cómo organizar el proyecto en nodes y routes?
- Carpeta nodes: define nodos como conversation, extractor y el booking node con patrón React.
- Carpeta routes: separa la lógica de enrutamiento. Incluye init.py, route.py y prompt.py para mantener el prompt del router y posibles tools.
Ventajas: modularidad, claridad y posibilidad de evolucionar el router sin tocar los nodos.

### ¿Qué errores típicos se encontraron y cómo se corrigen?
Durante la integración surgieron fallos útiles para afinar el flujo. Identificarlos rápido evita diagnósticos erróneos del prompt o del modelo.

- Nombre del módulo mal escrito. Se intentó importar booking en lugar de booking node. Síntoma: “no puede importar ese módulo”. Solución: corregir el nombre exacto del nodo y evitar “refresh” innecesarios si la configuración de setapp-tools ya descubre módulos automáticamente.
- Condición lógica invertida. El chequeo usaba is none en vez de is not none, forzando el desvío a conversation aunque el LLM devolviera booking. Solución: validar que el esquema no sea nulo y devolver schema.step; si no existe, usar el valor por defecto conversation.
- Ajustes de prompt en el router. El clasificador debía contemplar variaciones como appointments, no solo “medical appointments”. Solución: afinar el lenguaje del system prompt con términos más generales.
- Falta de visibilidad al debug. No había impresiones del step devuelto. Solución: imprimir el esquema y usar un sistema de monitoring como LangSmith para inspeccionar decisiones y mejorar el prompt.

### ¿Cómo validar el agente con pruebas y buenas prácticas?
Probar con mensajes representativos confirma que el router toma decisiones correctas y que la memoria compartida da contexto a todos los nodos.

- Mensaje casual: “Hola, ¿cómo estás?”. Debe ir a conversation y responder con cortesía.
- Petición de cita: “Quiero una cita para mañana a las tres PM con el doctor Pérez”. Debe ir a booking; el extractor aporta nombre, fecha, hora y médico, y el agente React pregunta por datos faltantes si aplica.
- Disponibilidad y confirmación: el flujo de booking valida horarios y devuelve alternativas cuando no hay cupo, manteniendo la conversación en el historial compartido.
- Pregunta técnica general: “cómo mejorar el rendimiento de un website”. Debe ir a conversation y activar el RAG con la fuente disponible; conviene ajustar el prompt para respuestas concisas.

Buenas prácticas observadas:
- Usar el historial completo en el router para mayor precisión; si el costo crece, evaluar un resumen previo o basarse solo en el último mensaje.
- Incluir few-shot en el system prompt del router para desambiguar intenciones cercanas.
- Escoger un modelo adecuado: para clasificar, un LLM no razonador puede bastar; para booking con React, uno con mejor razonamiento mejora la calidad.
- Mantener consistencia de nombres de nodos y tipados en el structured output.

### Lecturas recomendadas
- [Workflows and agents - Docs by LangChain](https://python.langchain.com/docs/langgraph/)

### Comentarios
¿Te gustaría que preparemos ejemplos de few-shot para tu dominio o revisemos el prompt de tu router? Comparte tus dudas y casos en los comentarios.