# Exposición de Agentes con FastAPI y Endpoints REST

## Curso para Crear Agentes de AI con LangGraph - Clase 23

### Resumen
Conecta tu agente inteligente al mundo con FastAPI y un endpoint claro, escalable y listo para producción. Aquí verás cómo levantar un servidor básico, crear un POST tipado para chat, invocar el agente con Human message y habilitar streaming response para una mejor UX, todo con pasos prácticos y probados en Postman.

### ¿Cómo exponer tu agente con FastAPI y un endpoint API?
Publicar el agente vía una recipe API permite que cualquier app web o móvil se conecte a tu servicio. El flujo es directo: instalar dependencias, crear un servidor básico, validar con un Hello, world! y luego añadir el endpoint que conecta con el agente.

### ¿Qué instala y cómo corre el servidor?
Instala el paquete y prepara el entorno.
Crea el archivo main.py dentro de tu carpeta API.
Corre el servidor en modo desarrollo y verifica la URL.

```bash
uv add fastapi standard
uv run fastapi dev src/api/main.py
```

Ejemplo mínimo con dos GET (uno con parámetro):

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "hello world"}

@app.get("/hello/{name}")
def hello_name(name: str):
    return {"hello": name}
```

Verifica el “hello world”.
Revisa la documentación automática en /docs con tus endpoints.

### ¿Cómo validar que la API responde?
Abre la URL que imprime la consola al iniciar el servidor.
Confirma el JSON esperado en el GET raíz.
Entra a /docs para probar endpoints con la UI interactiva.

### ¿Cómo crear un endpoint post para chat con tipado?
Para recibir un mensaje y un ID de chat, usa un POST con cuerpo tipado. Esto facilita validaciones y escalabilidad.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    message: str

@app.post("/chat/{chat_id}")
def chat(chat_id: int, item: Message):
    return {"chat_id": chat_id, "message": item.message}
```

### ¿Cómo probarlo con Postman?
Crea un request tipo POST a /chat/12.
Envía el JSON: { "message": "hola, ¿cómo estás?" }.
Verifica que responde el chat_id y el mensaje.

### ¿Cómo conectar el agente, manejar asincronía y streaming?
La clave es invocar el agente con el mensaje del usuario y retornar solo el contenido útil. Puedes cargar variables de entorno al iniciar main.py y elegir entre invocación síncrona o asíncrona, según tu necesidad de rendimiento.

```python
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

app = FastAPI()

class Message(BaseModel):
    message: str

@app.post("/chat/{chat_id}")
def chat(chat_id: int, item: Message):
    # response = agent.invoke([HumanMessage(content=item.message)])
    # return {"text": response.last_message.text}
    return {"text": "Hola, estoy bien. Gracias, ¿en qué puedo ayudarte?"}
```

Notas prácticas:
- Síncrono vs. asíncrono: puedes usar agent.invoke o agent.ainvoke si tu flujo es async.
- Estado por defecto: el agente recibe un estado inicial y el Human message en un array.
- Variables de entorno: cárgalas antes de invocar al agente para evitar errores de conexión a keys.

### ¿Cómo mejorar la UX con streaming response?
Usa el método agent.stream para enviar “pedacitos” a medida que se generan.
Implementa un endpoint adicional, por ejemplo, /chat-stream, y consúmelo en tu UI.
En web o móvil funciona bien; WhatsApp no acepta streaming.

```python
# for chunk in agent.stream([HumanMessage(content=item.message)]):
#     yield chunk  # la interfaz va pintando cada parte
```

Habilidades y conceptos trabajados:
- Exposición del agente mediante recipe API y endpoint público.
- Creación de servidor básico con FastAPI y verificación en /docs.
- Endpoints GET y POST con parámetros de ruta e input tipado.
- Uso de BaseModel para el modelo Message y cuerpo JSON.
- Pruebas con Postman para requests POST y validación de respuesta.
- Manejo de variables de entorno antes de llamar al agente.
- Invocación con Human message y retorno del last message en texto plano.
- Elección entre síncrono y asíncrono para rendimiento.
- Habilitación de streaming response para mejorar la UX.

### Lecturas recomendadas
- [Run a Server Manually - FastAPI](https://fastapi.tiangolo.com/tutorial/run/)

### Comentarios
¿Te gustaría que se muestre un ejemplo con tu propia ruta y cuerpo JSON? Cuéntame tu caso y lo adaptamos juntos.
