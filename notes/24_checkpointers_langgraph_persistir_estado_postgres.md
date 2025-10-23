# Checkpointers de LangGraph para Persistir Estado en Postgres

## Curso para Crear Agentes de AI con LangGraph - Clase 24

### Resumen
Evita que tu agente olvide cada interacción: con los checkpointers de LangGraph puedes guardar y derivar el estado de la conversación en una base de datos Postgres usando Docker, y controlar la concurrencia con un thread ID bien definido. Aquí aprenderás a instalar la librería, levantar Postgres y aplicar políticas de threads para que tu endpoint recuerde a cada usuario.

### ¿Qué resuelve un checkpointer de LangGraph y por qué importa?
Un agente sin memoria no avanza ni recuerda el nombre del usuario. Durante el debugging en LangGraph Studio hay memoria temporal, pero en un endpoint real el estado no se guarda. Un checkpointer crea un snapshot o screenshot del diálogo, lo asocia a un thread ID y lo persiste en una base de datos para restaurar: mensajes, memoria compartida y el nodo en el que quedó la ejecución.

- El agente no recuerda por defecto: sin estado persistente, cada pregunta empieza de cero.
- Checkpointer: guarda snapshots por thread para saber hacia dónde continuar o devolver la conversación.
- Base de datos: necesaria para recuperar el estado al consultar por thread ID.
- Concurrencia: cada usuario mantiene su propio estado sin interferir con otros.

### ¿Cómo funciona el guardado del estado por thread ID?
El thread ID define a quién pertenece la conversación y cuál estado cargar. Se pasa en la invocación del agente: “lo vamos a pasar a nivel de invoke, entonces siempre lo vamos a pasar aquí”. Cambias de conversación cambiando el ID; retomas un chat reutilizando el mismo ID.

### ¿Qué bases de datos e integraciones se mencionan?
- Oficialmente mantenidos por el equipo: Postgres y uno para SQL Lite. Recomendado usar Postgres por fiabilidad.
- Integraciones de la comunidad: Django, Dynamo, Firestore, entre otras, no mantenidas directamente por el equipo.

### ¿Cómo instalar la librería y levantar Postgres con Docker?
Primero instala la librería del checkpointer y prepara una base de datos Postgres con Docker. Luego conecta la librería a la base de datos para que persista los estados.

```bash
# Instalar la librería del checkpointer
uv add langgraph-checkpoint-postgres

# Levantar Postgres con Docker en modo detach
docker compose up -d

# Verificar servicios activos
docker compose ps
```

### ¿Cómo pasar el thread ID al agente?
Configura el agente para recibir el thread ID en cada invoke. Es el identificador que decide qué estado cargar, de quién es la conversación y dónde retomar. Cambia el ID para empezar un hilo nuevo o reutilízalo para continuar el mismo.

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres import PostgresSaver

# Configurar checkpointer
checkpointer = PostgresSaver.from_conn_string("postgresql://user:pass@localhost:5432/db")

# Agregar al agente
agent = builder.compile(checkpointer=checkpointer)

# Invocar con thread ID
response = agent.invoke({"messages": [HumanMessage(content="Hola")]}, config={"configurable": {"thread_id": "user_123"}})
```

### ¿Qué políticas de thread ID mejoran memoria y concurrencia?
Definir políticas de threads es clave para equilibrar recuerdo, rendimiento y costos. Elige la lógica que mejor se adapte a tu caso de uso.

- Relación uno a uno: usuario → un solo thread. Recuerda conversaciones aunque pase mucho tiempo. Puede degradar el contexto si el historial crece demasiado.
- Caducidad por tiempo: si el hilo supera 24 h, 48 h o una semana, se crea un nuevo thread. Mantiene al usuario enlazado, pero reinicia historial y estado de memoria compartida.
- Finalización por objetivo: cuando se resuelve la solicitud del usuario, se marca como finalizado y el siguiente mensaje abre un hilo desde cero, como en un call center.
- Concurrencia por usuario: el thread ID permite que “Juanito”, “Pepito” y “Fulanito” mantengan estados separados, cada uno con sus propios checkpoints.

### Lecturas recomendadas
- [langgraph-checkpoint-postgres · PyPI](https://pypi.org/project/langgraph-checkpoint-postgres/)

### Comentarios
¿Tú qué política aplicarías para tu agente y por qué? Comparte tu enfoque en los comentarios.
