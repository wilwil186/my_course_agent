# 📚 Guía de Repaso - Examen LangGraph y LangChain

**Resultado actual: 11/15 (7.33)** - Necesitas 9.0 para aprobar

Esta guía resume las respuestas correctas e incorrectas del examen, con claves conceptuales y sugerencias para mejorar la puntuación.

## ✅ RESPUESTAS CORRECTAS (11)
*Estas las tienes dominadas, solo repásalas rápidamente*

### 1. **Paralelización de Nodos**
**Tu respuesta:** Los nodos deben ser independientes entre sí y no requerir el resultado de otro nodo paralelo.
> **Clave:** INDEPENDENCIA = PARALELIZACIÓN EFECTIVA

### 3. **DynamoDB y Checkpointers**
**Tu respuesta:** Deberá utilizar una integración desarrollada y mantenida por la comunidad, ya que LangChain solo mantiene oficialmente las de PostgreSQL y SQL Lite.
> **Clave:** Solo PostgreSQL y SQLite tienen soporte oficial de LangChain

### 4. **Arquitectura Cognitiva**
**Tu respuesta:** Permite control explícito sobre cómo el agente deriva su estado y toma decisiones
> **Clave:** CONTROL EXPLÍCITO del desarrollador sobre el proceso cognitivo

### 6. **Nodos vs Edges**
**Tu respuesta:** Nodos actualizan estado, edges solo enrutan sin modificar
> **Memoriza:** NODO = MODIFICA | EDGE = ENRUTA

### 8. **Razonamiento del Modelo**
**Tu respuesta:** El modelo determina internamente que no necesita File Search para "Hola, ¿cómo estás?"
> **Concepto:** Los LLMs razonan sobre cuándo usar herramientas

### 9. **Modularización**
**Tu respuesta:** Organizar cada nodo en su carpeta con `prompt.py`, `node.py`, `tools.py`
> **Arquitectura:** MODULARIZACIÓN = ORGANIZACIÓN CLARA

### 10. **Tipos de Mensajes**
**Tu respuesta:** Para identificar el rol de cada interlocutor y generar respuestas coherentes
> **Tipos:** AIMessage | HumanMessage | SystemMessage

### 11. **LangChain + LangGraph**
**Tu respuesta:** LangChain proporciona `create_agent` que usa LangGraph internamente
> **Relación:** LangChain (utilidades) → LangGraph (orquestación)

### 13. **Función de Tools**
**Tu respuesta:** Permitir al LLM ejecutar acciones en el mundo real
> **Concepto:** Tools = Puente entre cognición y acción

### 14. **Error de Importación - pyproject.toml**
**Tu respuesta:** Falta configuración de packages en `pyproject.toml`, solución: `uv install`
> **Debugging:** ImportError → verificar pyproject.toml

### 15. **init_chat_model**
**Tu respuesta:** Es un wrapper que requiere las dependencias instaladas
> **Importante:** Wrapper ≠ Instalador de dependencias

---

## ❌ RESPUESTAS INCORRECTAS (4)
*ESTUDIA ESTAS A FONDO - Son las que necesitas corregir*

### 2. **Error de FastAPI - HumanMessage** ⚠️
**Tu respuesta:** Faltaba importar `HumanMessage` desde `langchain.core`

**PROBLEMA:** Esta respuesta fue marcada incorrecta. Revisa:
- ¿Era desde otro módulo? (langchain.schema, etc.)
- ¿El problema era otro tipo de import?
- ¿Era un problema de configuración en vez de import?
- Verificar el namespace correcto del import

**ESTUDIO:** Revisar el debugging del primer intento con FastAPI

### 5. **Thread_id y Error invalid value** ⚠️
**Tu respuesta:** El grafo no recibió el checkpointer configurado para ese thread_id

**POSIBLES CAUSAS DEL ERROR:**
- Thread_id podría estar corrupto o mal formateado
- Conflicto entre diferentes versiones de checkpointer
- Estado inconsistente en la base de datos
- Problema de sincronización entre threads

**ESTUDIO:** Revisar el segmento de debugging sobre thread_id

### 7. **Prompt Chaining - Malas Prácticas** ⚠️
**Tu respuesta:** Mejor usar patrón evaluator para refinar iterativamente

**REVISA EN LA CLASE (minuto 05:04):**
- ¿El problema es la falta de iteración o retroalimentación?
- ¿Es sobre acoplamiento entre prompts?
- ¿Complejidad innecesaria para tareas simples?
- ¿Problema de mantenibilidad?

**ESTUDIO:** Ver específicamente minuto 05:04 sobre malas prácticas

### 12. **Jinja2 vs String Format** ⚠️
**Tu respuesta:** Jinja2 mejora compatibilidad con modelos no-LangChain

**OTRAS VENTAJAS POSIBLES:**
- Control de flujo más potente (condiciones if/for)
- Mejor manejo de variables complejas
- Sintaxis más limpia y legible
- Reutilización de templates

**ESTUDIO:** Buscar ventajas específicas de Jinja2 mencionadas en clase

---

### ✅ Respuestas Correctas (13/15)

| # | Pregunta | Tu Respuesta | Clave Conceptual |
| :---: | :--- | :--- | :--- |
| **1.** | Routing vs. Paralelización | El routing sigue una ruta única seleccionada por una condición, mientras que la paralelización ejecuta múltiples rutas obligatoriamente. | **Routing:** Excluyente, condicional. **Paralelización:** Inclusiva, simultánea. |
| **2.** | Respuestas Incoherentes (Ingeniero de Contexto) | El manejo inteligente del estado y el historial para controlar qué información se mantiene en el contexto. | El historial es el problema de la incoherencia. |
| **3.** | Comportamiento del Aggregator | Tomará los resultados de los nodos 1 y 3 y los sintetizará, ignorando por completo al nodo 2. | Solo agrega los resultados de los nodos ejecutados. |
| **5.** | Función para Asociar Tools | `bind_with_tools([getProducts, getWeather])` | Función de *binding* (asociación) de herramientas al LLM. |
| **6.** | Prompt Chaining vs. Paralelo | En "prompt chaining" los nodos se ejecutan en un orden secuencial predefinido, mientras que en un workflow "paralelo" varios nodos se ejecutan simultáneamente. | **Chaining:** Secuencial, rígido. **Paralelo:** Ejecución simultánea. |
| **7.** | Aislamiento de Hilos (Memoria) | El agente no recordará el nombre 'Ana', ya que la memoria compartida y el estado son independientes para cada hilo de conversación. | Principio de **Thread Isolation** (Aislamiento por `thread_id`). |
| **8.** | Propósito del Entorno Virtual | Aislar las dependencias del proyecto para evitar conflictos con otras instalaciones globales de Python. | Definición de entorno virtual. |
| **9.** | Razón para Modularizar | Mejora la escalabilidad y facilita el mantenimiento al organizar los componentes de forma lógica y separada. | Buena práctica de arquitectura. |
| **10.** | Ventaja de `MessagesState` | `MessagesState` implementa un protocolo que concatena automáticamente los nuevos mensajes al historial existente sin sobreescribirlo. | *Reducer* de `MessagesState`. |
| **12.** | Propósito de `partial_variables` | Para definir valores por defecto que se usarán si no se proporciona una variable específica durante el formateo. | Uso de `partial_variables` en `PromptTemplate`. |
| **13.** | ReAct (Clima + Productos) | La capacidad de mantener el contexto de la conversación y combinar información de múltiples herramientas para generar respuestas proactivas. | Razonamiento Multi-Paso y Contextualización. |
| **14.** | Paso Inmediato del LLM (Tool Calling) | Identifica que debe usar la herramienta `GetProducts`, extrae el parámetro `price` con el valor 1000, y devuelve esta información a la capa de aplicación. | El LLM *decide* y *extrae*, LangGraph *ejecuta*. |
| **15.** | Seguridad en Jupyter (API Key) | Almacenar la clave en un archivo `.env`, cargarla con `load_dotenv()`, y asegurarse de eliminar cualquier celda que imprima la clave para no exponerla en las salidas guardadas del notebook. | Buenas prácticas de seguridad. |

***

### ❌ Respuestas Incorrectas (2/15) - Las que debes Cambiar

| # | Pregunta | Tu Respuesta (Marcada Incorrecta) | Corrección Sugerida (Para el 14/15) |
| :---: | :--- | :--- | :--- |
| **4.** | Arquitectura `codereview` (Paralelización) | Un agente ReAct decide en tiempo de ejecución si es necesario un análisis de seguridad, de mantenibilidad o ambos. | **HIPÓTESIS DE CLASE:** La clase pudo haber enfatizado que **el flujo es siempre paralelo** y la decisión del LLM ocurre *después* de la ejecución, o que el *router* es un nodo de *routing* simple, no un agente ReAct. **CAMBIA A:** **El flujo está predefinido para ejecutar siempre y de forma simultánea todos los nodos conectados en paralelo.** (Esto es la paralelización *fija*). |
| **11.** | Agendador de Citas (Acción ReAct) | Ejecutar la herramienta `verificar_disponibilidad` con parámetros vacíos para mostrar opciones generales al usuario. | **HIPÓTESIS DE CLASE:** Ante una entrada incompleta ("Quiero agendar una cita"), la acción más probable del LLM es **pedir la información faltante** (fecha y hora), lo que se hace generando una **respuesta conversacional** (`AIMessage`), no llamando a una herramienta con parámetros vacíos. **CAMBIA A:** **Generar una respuesta conversacional pidiendo la información faltante (ej. '¿Qué día y hora quieres agendar tu cita?')** |

***

### 🚀 Estrategia para el Reintento

1. **Prioridad Alta:** Corrige las respuestas de las preguntas **4** y **11** usando las sugerencias proporcionadas.
2. **Repaso Rápido:** Revisa las 13 respuestas correctas para consolidar los conceptos clave.
3. **Resultado Esperado:** Al corregir las 2 incorrectas, tu puntuación subirá a **15/15** (10.0), asegurando la aprobación.