# Implementación de Tools en ReAct Agents con LangChain Core

## Curso para Crear Agentes de AI con LangGraph - Clase 14 de 26

### Resumen
Los grandes modelos de lenguaje pueden pensar, pero para actuar necesitan tools bien definidas. En esta clase, se explica paso a paso cómo integrar tools en un ReAct Agent, distinguir qué corre en la capa de aplicación y qué puede ejecutar el modelo, y cómo convertir un prompt en acciones reales como consultar una API o agendar una cita.

### ¿Cómo fluyen las tools desde el prompt hasta la capa de aplicación?
La interacción inicia con el request del usuario y pasa por tu aplicación, que actúa como wrapper del large language model. Con tools, el modelo no ejecuta la acción ni devuelve el resultado directo: primero identifica la herramienta y extrae parámetros, de forma parecida al structured output.

### ¿Qué retorna el modelo con tools y structured output?
- Devuelve un formato con el function identifier y los parámetros requeridos.
- Si faltan datos, pide al usuario lo que falta hasta estar “listo”.
- Cuando está listo, cambia de respuesta conversacional a respuesta tool con el nombre de la función y sus argumentos.

### ¿Dónde se ejecuta la tool: modelo o capa de aplicación?
- En general, las tools declaradas como funciones se ejecutan en tu capa de aplicación.
- Algunas tools son propias del modelo, como FileSearch de OpenAI, que corre con su infraestructura.
- Tras ejecutar la función en tu sistema, devuelves el resultado al modelo y este lo interpreta y responde al usuario. Ese es el ciclo completo de una tool.

### ¿Cómo definir una tool con LangChain Core y parámetros?
Se construye una función decorada como tool en LangChain Core. Así, el modelo puede mapear qué hace, cuándo usarla y con qué argumentos.

### ¿Qué incluir en la descripción y argumentos de la tool?
- Nombre claro, por ejemplo: GetProducts.
- Descripción orientada a uso: qué obtiene y para qué sirve.
- Argumentos tipados: por ejemplo, precio como entero para filtrar resultados.
- Contexto adicional: explica qué espera cada argumento, como harías en un prompt.

### ¿Cómo devolver resultados en texto para el modelo?
Aunque podrías responder con arrays, el modelo entiende mejor texto formateado. Mapea y concatena los elementos (por ejemplo, producto y precio) para ofrecer una lista legible. Llama a la tool pasando un diccionario con los argumentos; si no hay argumentos, envía un diccionario vacío.

### ¿Cómo conectar la tool a una API y evitar alucinaciones?
Para información en tiempo real (clima, productos, etc.), no basta el conocimiento del modelo. Necesitas una tool que consulte una API y te devuelva datos actualizados. Así evitas respuestas vagas o alucinaciones.

### ¿Qué ejemplo práctico se implementa con GetProducts?
- Se parte de fake data para simular productos y luego se sustituye por una API de productos de Platzi.
- Se corrige el endpoint y se confirman los campos: title y price.
- La función devuelve los productos en texto con su precio, lista para que el LLM responda con claridad.
- También se menciona el caso del agendador de citas: el modelo identifica la tool con parámetros como nombre del paciente, doctor y fecha; tu app llama a la API de agendamiento y regresa el resultado al modelo para que lo comunique.

### ¿Qué modelos se mencionan para razonar y responder rápido?
- Un modelo de razonamiento: “Cloud Opus 4.1”, más lento pero con mejor análisis.
- Alternativa con equilibrio entre rapidez y razonamiento: “Gemini 2.5”.
- Además, se contrasta ampliar conocimiento con un “rack” vectorial frente a usar tools: puedes vectorizar productos y hacer retrieval, o conectarte a una API según el caso.

### Ideas clave para poner en práctica
- **ReAct Agent y tools**: La tool define la acción, el modelo decide cuándo usarla.
- **Function identifier y parámetros**: Formato no conversacional que guía la ejecución.
- **Capa de aplicación**: Ahí se hacen las llamadas reales a servicios y bases de datos.
- **Respuesta en texto**: Formatea la salida para que el modelo continúe la conversación.
- **Evitar alucinaciones**: Conecta APIs para clima, Wikipedia o tus propios sistemas.

### Lecturas recomendadas
- [Introduction to function calling](https://platform.openai.com/docs/guides/function-calling)
- [Generative AI on Vertex AI - Google Cloud](https://cloud.google.com/vertex-ai/docs/generative-ai/function-calling)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [OpenAI Models Comparison](https://platform.openai.com/docs/models/compare)
- [Reasoning Best Practices](https://platform.openai.com/docs/guides/reasoning-best-practice)
- [Gemini Models - Google AI](https://ai.google.dev/models/gemini)
- [Claude Models Overview](https://docs.anthropic.com/en/docs/models-overview)

### Comentarios destacados
- **Pablo Torres Pérez**: Algo interesante, es que los docstrings también se pueden usar como la descripción de la tool. Ejemplo de implementación con `@tool` en LangChain.
- **Nicolas Molina**: Sí, eso también es muy útil, usar los mismos comentarios del método como insumo para documentar la tool.
