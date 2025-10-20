# Implementación de Agente ReAct para Booking de Citas Médicas

## Curso para Crear Agentes de AI con LangGraph - Clase 16

### Resumen
Un agente ReAct bien diseñado acelera el booking de citas médicas con precisión. Aquí verás cómo estructurar un nodo, definir sus tools, preparar un prompt con reglas claras y probarlo en standalone con LangGraph Studio. El enfoque combina razonamiento del language model con salidas de APIs formateadas en texto plano para una experiencia fluida.

### ¿Cómo se arma un agente ReAct con tools y prompt?
La base es un nodo tipo ReAct: un agente, sus tools y un system prompt. Se crea con `create_react_agent`, pasando el modelo, el arreglo de tools y el prompt. El modelo se inyecta directo: no hace falta un init especial. El prompt guía pasos, reglas y variables como `today` para interpretar expresiones temporales relativas.

### ¿Qué estructura de archivos usa el nodo booking?
Estructura mínima ordenada por responsabilidad: un node, su prompt y sus tools.

```
booking/
  __init__.py
  node.py
  prompt.py
  tools.py
```

- Un nodo por responsabilidad: extractor, conversation y booking.
- Reutiliza tools existentes cuando convenga.
- Mantén ejemplos de ReAct separados para no afectar el booking real.

### ¿Cómo se carga el prompt con reglas y today?
El prompt define el rol: asistente que agenda citas médicas. Incluye `today` como variable calculada si no se envía. Añade pasos y reglas para reducir errores del agente.

```python
system_prompt = """
Eres un asistente que agenda citas médicas.
today: {today}
pasos:
1) obtener información del paciente.
2) obtener fecha y hora deseadas.
3) obtener información del doctor.
4) check de availability.
5) enviar sugerencias.
6) hacer booking.
reglas:
- usa book appointment solo si ya verificaste availability.
- no agendar a más de 30 días.
"""
```

- El prompt sigue siendo fundamental, incluso con patrón ReAct.
- Los pasos guían el razonamiento y el orden de llamadas a tools.
- Reglas explícitas: primero check de availability, luego book appointment.

### ¿Cómo se integran tools existentes como getweather y getproducts?
Se importan, se agrupan en un array y se pasan al agente. Sirven para validar la arquitectura ReAct antes del booking real.

```python
from tools import getweather, getproducts

tools = [getweather, getproducts]
agent = create_react_agent(model=model, tools=tools, prompt=system_prompt)
```

- El agente formatea la salida de las tools y genera la respuesta final.
- Ejemplo práctico: listó productos y categorizó por tipo de prenda de forma autónoma.
- También combinó clima con catálogo y sugirió productos acordes a la temperatura.

### ¿Cómo se prueban el nodo y el agente en standalone?
El nodo booking se puede ejecutar en standalone: funciona como mini-nodo de LangGraph y como agente individual. Así se valida el flujo antes de integrarlo con extractor y conversation. En LangGraph Studio se inspeccionan llamadas a tools, state y mensajes del chat.

- Respuesta inicial: saluda, confirma nombre del paciente y pide fecha, hora y doctor.
- Entiende expresiones relativas: mañana, tarde, etc., gracias a `today`.
- Secuencia observada: primero usa `get_appointment_availability`, luego hace `booking_appointment` y confirma.

### ¿Qué habilidades técnicas se aplican en la implementación?
- Diseño de nodos con patrón ReAct: agente + tools + prompt.
- Prompting con pasos, reglas y variables como `today`.
- Reutilización e incorporación de tools externas.
- Mocking de APIs para acelerar pruebas.
- Control de errores en tools: devolver texto claro al modelo.
- Formateo en texto plano: respuestas legibles para el language model.
- Pruebas en standalone antes de integrar con routing y chain.

### ¿Qué herramientas de booking se definieron y qué parámetros aceptan?
Dos tools con foco en disponibilidad y reserva. Por ahora hacen mocking, listas para conectarse a tu API o calendario.

```python
def booking_appointment(fecha: str, tiempo: str, doctor: str, paciente: str) -> str:
    # lógica real: validar, reservar y manejar errores
    return (
        f"Cita confirmada: paciente {paciente}, doctor {doctor}, "
        f"fecha {fecha}, hora {tiempo}."
    )

def get_appointment_availability(fecha: str, tiempo: str, doctor: str) -> str:
    # lógica real: consultar agenda y formatear 'slots' útiles
    return (
        f"Disponibilidad para {doctor} en {fecha} {tiempo}: 14:00, 15:00, 16:00. "
        "Indica tu hora preferida."
    )
```

- `booking_appointment`: requiere fecha, tiempo, doctor y paciente.
- `get_appointment_availability`: requiere fecha, tiempo y doctor.
- Devuelven texto plano: fácil de interpretar y reformatear por el agente.

### ¿Cómo diseñar las tools de booking y el flujo de decisión?
El flujo se guía por el prompt template: primero recopilar datos, luego check de availability, sugerir horarios y finalmente reservar. Añade reglas como no agendar más de treinta días.

- Diseña salidas en texto claro: el modelo debe poder decidir con esa información.
- Si falla una tool: devuelve un mensaje de error en texto para que el agente lo comunique.
- Integra después con routing para derivar entre extractor, conversation y booking.

### Lecturas recomendadas
- [Tools - Docs by LangChain](https://python.langchain.com/docs/modules/tools/)
- [Agents - Docs by LangChain](https://python.langchain.com/docs/modules/agents/)

### Comentarios
**Nicolas Molina (teacher)**: Usando la versión del pre-release hubo un pequeño cambio creando el agent en vez de poner prompt debes poner `system_prompt` entonces queda así:

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[...],
    system_prompt="You are a helpful assistant",
)
```

¿Te gustaría comentar cómo conectar estas tools a tu API o calendario y qué validaciones agregarías?