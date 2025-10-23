# Configuración de Checkpointer Dinámico con FastAPI y Postgres

## Curso para Crear Agentes de AI con LangGraph - Clase 25

### Resumen
Conecta tu agente a una base de datos y preserva el historial sin dolores de cabeza. Aquí verás cómo construir un grafo con checkpointer dinámico, inicializarlo con FastAPI y Postgres, inyectar dependencias, y evitar que el contexto se corrompa al guardar solo lo esencial. Además, se señalan errores reales y cómo depurarlos con LangGraph Studio.

### ¿Cómo crear un checkpointer dinámico con FastAPI y Postgres?
Para que el agente recuerde y comparta estado, la configuración debe ser dinámica. La clave es recibir el checkpointer desde la app web y no “quemarlo” en el build del agente.

### ¿Cómo definir la función makegraph con configuración dinámica?
Define una función que construya el grafo y reciba un config con el checkpointer.
Envía el checkpointer al construir el agente.

```python
# makegraph.py
from typing import TypedDict, Optional

class GraphConfig(TypedDict, total=False):
    checkpointer: object  # instancia del checkpointer

def makegraph(config: GraphConfig):
    checkpointer = config.get("checkpointer", None)
    # construir el agente/ grafo usando el checkpointer dinámico
    agent = build_agent(checkpointer=checkpointer)  # función de construcción existente
    return agent
```

Ventaja: permite seguir usando LangGraph Studio para debug (si no pasas checkpointer, usarán uno propio) y, a la vez, integrarlo bien con FastAPI.

### ¿Cómo inicializar la conexión en el lifespan de FastAPI?
Crea una instancia global para el checkpointer de Postgres.
Inicializa antes de levantar la app con lifespan y ejecuta el setup para las tablas del estado.
Evita credenciales “quemadas”; usa variables de ambiente. Si las “quemas”, es inseguro.

```python
# db.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer_global = None  # instancia global

@asynccontextmanager
async def lifespan(app: FastAPI):
    global checkpointer_global
    # ejemplo: lee de env en la práctica (aquí simplificado)
    dsn = "postgresql+psycopg://user:password@localhost:5432/db"
    checkpointer_global = PostgresSaver.from_conn_string(dsn)
    await checkpointer_global.setup()  # crea tablas para estado del grafo
    yield
    # opcional: cerrar conexiones

def get_checkpointer():
    if not checkpointer_global:
        raise RuntimeError("checkpointer no inicializado")
    return checkpointer_global
```

### ¿Cómo invocar el grafo desde el endpoint con dependencia?
Inyecta el checkpointer como dependencia.
Construye el grafo con makegraph y pásale la instancia.

```python
# api.py
from fastapi import FastAPI, Depends
from db import lifespan, get_checkpointer
from makegraph import makegraph

app = FastAPI(lifespan=lifespan)

@app.post("/chat")
async def chat_endpoint(payload: dict, checkpointer=Depends(get_checkpointer)):
    agent = makegraph({"checkpointer": checkpointer})
    state = {"messages": [payload.get("message")]}  # además de otros campos de estado
    result = await agent.invoke(state)
    return result
```

Tip: si usas el endpoint de stream, inyecta también la dependencia del checkpointer.

### ¿Cómo mantener limpio el estado y el historial del grafo?
El estado es memoria compartida. Si guardas metadatos “ruidosos”, el prompt y el routing se degradan. La solución: persistir solo el texto útil.

```python
# al producir la respuesta en el nodo de conversation
raw_ai_message = await conversation_node(...)  # respuesta del modelo
clean_text = raw_ai_message.content if hasattr(raw_ai_message, "content") else str(raw_ai_message)

# guardar solo clean_text en historial/DB
save_message({
    "role": "ai",
    "content": clean_text,
})
```

Beneficio: el language model recibe contexto claro. Evitas errores en system history y routing.

### ¿Cómo usar thread ID, CRUD y memoria compartida de forma segura?
Cada conversación usa un thread ID. Si cambias el thread ID, inicias otra memoria desde cero.
Guarda entrada y salida: add_message del usuario y también de la AI con su chat ID.
Puedes reconstruir el estado desde la base: cargas historial y lo inyectas como state junto a campos como customer_name.
Si un thread quedó “sucio”, crea uno nuevo y continúa con historial limpio.

Buenas prácticas:
- Persistir mensajes con CRUD simple.
- Asociar por chat ID.
- Evitar metadata innecesaria en el historial.

### ¿Cómo depurar errores frecuentes con LangGraph Studio y el API?
La depuración combina impresión rápida, revisión del historial y ajuste del routing. Estos fueron fallos típicos y su enfoque.

- ¿Qué hacer ante internal server error e invalid request?
  - Verifica que ya no invocas al agente directo: usa makegraph con checkpointer en el endpoint.
  - Imprime el último message para validar formato de entrada. Aunque no es lo ideal, un print veloz ayuda a aislar el problema.
  - Revisa si el error proviene del extractor y no del nodo de conversación. Ajusta esa etapa primero.
- ¿Cómo revisar system history y routing con LangGraph Studio?
  - Usa LangGraph Studio para ejecutar la función constructora del grafo y ver el system history.
  - Imprime el historial y valida que no contenga metadatos no deseados.
  - Si el primer thread se creó sin checkpointer, puede haber historial viejo. Crea un thread nuevo y prueba.

### ¿Cómo optimizar el flujo con booking e intent route?
El booking (creative rig agent) comparte estado completo y suele manejar mejor el historial limpio.
Si el rack de OpenAI solo toma el último mensaje, ajusta el prompt o define un custom rack según el caso.
Guía con intent route hacia el agente correcto cuando el usuario pida acciones como citas médicas.

Señales de mejora:
- Evitar búsquedas a file search para preguntas simples.
- Inyectar prompt con datos del usuario si corresponde.
- Limpiar también la salida del agente de booking si añade metadata.

### Comentarios
¿Te gustaría que compartamos un ejemplo más detallado de la limpieza del historial o de la inyección de estado con campos personalizados como customer_name?
