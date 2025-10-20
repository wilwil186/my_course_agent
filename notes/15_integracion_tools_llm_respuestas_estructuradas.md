# Integración de Tools con LLM y Manejo de Respuestas Estructuradas

## Curso para Crear Agentes de AI con LangGraph - Clase 15

### Resumen
Conecta tus tools a un large language model y conviértelas en respuestas claras para el usuario. Aquí verás cómo el modelo detecta funciones como getProducts y una tool de clima basada en Geocoding y Open-Meteo, por qué no las ejecuta, y cómo cerrar el ciclo con resultados formateados en el idioma de la conversación. Además, aprenderás a usar `bind_with_tools`, orientar con un system prompt y apoyarte en el patrón React para la iteración.

### ¿Cómo responde el modelo cuando agregas tools?
Cuando enlazas tools, el modelo cambia su comportamiento. No ejecuta funciones: identifica cuál llamar y con qué argumentos. Devuelve texto más un objeto de tool calls que indica la función objetivo y los parámetros extraídos del contexto y del historial.

- No hay respuesta final en la primera pasada. El modelo suele decir cosas como “Voy a consultar los productos disponibles de nuestra tienda.”.
- Tú ejecutas la función con los argumentos que el modelo sugirió.
- Le devuelves el resultado como string en la siguiente llamada.
- El modelo reformatea y entrega la respuesta al usuario en el tono e idioma del chat.

### ¿Qué es un tool call y qué información entrega?
Un tool call es la instrucción estructurada del modelo: nombre de la función a invocar y argumentos listos para ejecutar. Llega junto al texto, pero ese texto no es el resultado útil. Sirve como señal para que tu sistema llame a la tool correcta.

### ¿Cómo cerrar el ciclo de ejecución y reformulación?
- Ejecuta la función indicada con los argumentos propuestos.
- Pasa el resultado como string en el “botón de la respuesta”.
- El LLM usa ese dato para reformular y entregar el contenido final al usuario.
- La iteración puede automatizarse con el patrón React.

### ¿Qué pasa si no hay tool que ejecutar?
Si el mensaje no requiere tools (por ejemplo, un “hola”), el modelo responde de forma conversacional. Los tool calls solo aparecen cuando detecta que debe llamar una función.

### ¿Cómo construir la tool del clima con APIs?
Se crea una tool que recibe una ciudad, consulta una API de Geocoding para obtener latitud y longitud, y luego llama a Open-Meteo para el clima actual. El flujo: ciudad → Geocoding (latitud, longitud) → clima (temperatura, velocidad del viento) → salida como string.

- La ciudad se envía a Geocoding. Se procesa la respuesta como JSON.
- Con la latitud y longitud, se llama a Open-Meteo para el clima.
- Se formatea la respuesta en un string listo para el LLM.
- Ejemplo usado: “Bogotá” devolviendo temperatura y viento.

### ¿Cómo se agregan las tools al modelo?
- Se crea una derivación del large language model original y se enlazan las tools con `bind_with_tools`: getProducts y getWeather.
- Luego se invoca con los mensajes actuales.
- El modelo detecta cuándo usar cada tool.
- Envía el tool call con argumentos listos.
- Tu sistema ejecuta y devuelve el resultado para que el LLM lo formatee.

### ¿Qué incluir en el system prompt para guiar al asistente?
Defínelo como asistente de ventas capaz de encontrar productos y dar el clima de una ciudad. Enumera sus tools y la finalidad de cada una.

- Indica qué hace getProducts.
- Indica qué hace getWeather.
- Mantén el objetivo y el tono deseado.

### ¿Cómo infiere argumentos desde la conversación?
El modelo puede inferir argumentos a partir del historial. Si el usuario menciona “la capital de Colombia”, el modelo puede deducir “Bogotá” y preparar el argumento de “city” para la tool del clima. En escenarios como agendamiento de citas, puede convertir “mañana” o “en tres días” al formato exacto que le pidas para tu API.

### ¿Cómo definir formatos de entrada para fechas y ciudades?
- Especifica el formato esperado en el prompt (por ejemplo, estructura de fecha o clave “city”).
- El LLM extrae del contexto y ajusta al formato antes de sugerir el tool call.
- Tú solo ejecutas con parámetros ya listos.

### Habilidades clave para mejores resultados
- Diseño de prompts y uso de system prompt claro.
- Definición de tools: getProducts, getWeather.
- Manejo de tool calls y argumentos.
- Consumo de APIs: Geocoding y Open-Meteo con latitud y longitud.
- Procesamiento de JSON y respuesta como string.
- Iteración con patrón React para cerrar el ciclo.

### Lecturas recomendadas
- [Geocoding API](https://geocoding-api.open-meteo.com/v1/search?name=bogota)
- [Open-Meteo Forecast API](https://api.open-meteo.com/v1/forecast?latitude=-17.39)
- [Platzi Fake Store API](https://fakeapi.platzi.com/)

¿Te gustaría ver ejemplos adicionales de prompts o del encadenamiento con `bind_with_tools` y patrón React? Comparte tus dudas o casos de uso en los comentarios.


Clase anterior

Ver clases
Siguiente clase

Play

Regresa 15 segundos

Adelanta 15 segundos
Current Time 
0:00
/
Duration 
10:56

Mute
2x
Playback Rate

Subtitles

Picture-in-Picture

Fullscreen
¿Tienes preguntas sobre la clase? Obtén respuesta inmediata

Preguntar
Lecturas recomendadas
https://geocoding-api.open-meteo.com/v1/search?name=bogota

https://api.open-meteo.com/v1/forecast?latitude=-17.39

Platzi Fake Store API | Platzi Fake Store API

Resumen

Conecta tus tools a un large language model y conviértelas en respuestas claras para el usuario. Aquí verás cómo el modelo detecta funciones como getProducts y una tool de clima basada en Geocoding y OpenAI OpenMethod, por qué no las ejecuta, y cómo cerrar el ciclo con resultados formateados en el idioma de la conversación. Además, aprenderás a usar bind_with_tools, orientar con un system prompt y apoyarte en el patrón React para la iteración.

¿Cómo responde el modelo cuando agregas tools?
Cuando enlazas tools, el modelo cambia su comportamiento. No ejecuta funciones: identifica cuál llamar y con qué argumentos. Devuelve texto más un objeto de tool calls que indica la función objetivo y los parámetros extraídos del contexto y del historial.

No hay respuesta final en la primera pasada. El modelo suele decir cosas como “Voy a consultar los productos disponibles de nuestra tienda.”.
Tú ejecutas la función con los argumentos que el modelo sugirió.
Le devuelves el resultado como string en la siguiente llamada.
El modelo reformatea y entrega la respuesta al usuario en el tono e idioma del chat.
¿Qué es un tool call y qué información entrega?
Un tool call es la instrucción estructurada del modelo: nombre de la función a invocar y argumentos listos para ejecutar. Llega junto al texto, pero ese texto no es el resultado útil. Sirve como señal para que tu sistema llame a la tool correcta.

¿Cómo cerrar el ciclo de ejecución y reformulación?
Ejecuta la función indicada con los argumentos propuestos.
Pasa el resultado como string en el “botón de la respuesta”.
El LLM usa ese dato para reformular y entregar el contenido final al usuario.
La iteración puede automatizarse con el patrón React.
¿Qué pasa si no hay tool que ejecutar?
Si el mensaje no requiere tools (por ejemplo, un “hola”), el modelo responde de forma conversacional. Los tool calls solo aparecen cuando detecta que debe llamar una función.

¿Cómo construir la tool del clima con APIs?
Se crea una tool que recibe una ciudad, consulta una API de Geocoding para obtener latitud y longitud, y luego llama a OpenAI OpenMethod para el clima actual. El flujo: ciudad → Geocoding (latitud, longitud) → clima (temperatura, velocidad del viento) → salida como string.

La ciudad se envía a Geocoding. Se procesa la respuesta como JSON.
Con la latitud y longitud, se llama a OpenAI OpenMethod para el clima.
Se formatea la respuesta en un string listo para el LLM.
Ejemplo usado: “Bogotá” devolviendo temperatura y viento.
¿Cómo se agregan las tools al modelo?
Se crea una derivación del large language model original y se enlazan las tools con bind_with_tools: getProducts y getWeather. Luego se invoca con los mensajes actuales.

El modelo detecta cuándo usar cada tool.
Envía el tool call con argumentos listos.
Tu sistema ejecuta y devuelve el resultado para que el LLM lo formatee.
¿Qué incluir en el system prompt para guiar al asistente?
Defínelo como asistente de ventas capaz de encontrar productos y dar el clima de una ciudad. Enumera sus tools y la finalidad de cada una.

Indica qué hace getProducts.
Indica qué hace getWeather.
Mantén el objetivo y el tono deseado.
¿Cómo infiere argumentos desde la conversación?
El modelo puede inferir argumentos a partir del historial. Si el usuario menciona “la capital de Colombia”, el modelo puede deducir “Bogotá” y preparar el argumento de “city” para la tool del clima. En escenarios como agendamiento de citas, puede convertir “mañana” o “en tres días” al formato exacto que le pidas para tu API.

¿Cómo definir formatos de entrada para fechas y ciudades?
Especifica el formato esperado en el prompt (por ejemplo, estructura de fecha o clave “city”).
El LLM extrae del contexto y ajusta al formato antes de sugerir el tool call.
Tú solo ejecutas con parámetros ya listos.
¿Qué habilidades y keywords activan mejores resultados?
Diseño de prompts y uso de system prompt claro.
Definición de tools: getProducts, getWeather.
Manejo de tool calls y argumentos.
Consumo de APIs: Geocoding y OpenAI OpenMethod con latitud y longitud.
Procesamiento de JSON y respuesta como string.
Iteración con patrón React para cerrar el ciclo.
¿Te gustaría ver ejemplos adicionales de prompts o del encadenamiento con bind_with_tools y patrón React? Comparte tus dudas o casos de uso en los comentarios.


Escribe tu comentario o pregunta

Más votados
Nuevos
Favoritos
Aún no hay aportes en esta clase
Escribe tu pregunta o comentario y sé la primera persona en participar en esta clase.

