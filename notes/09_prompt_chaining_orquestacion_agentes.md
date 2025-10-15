# Clase 9 — Prompt Chaining: Orquestación de Agentes en Secuencia

**Objetivo:** Aprender a descomponer tareas complejas en **nodos especializados** que trabajan en secuencia, usando **LangGraph** para crear flujos predecibles y mantenibles.

---

## 🧠 ¿Qué problema resuelve?
Cuando las tareas son complejas, un solo prompt puede fallar o volverse difícil de mantener.

- **Problema**: Intentar resolver todo en un solo prompt gigante sobrecarga al LLM, reduce precisión y dificulta el debugging.
- **Solución con Prompt Chaining**: Dividir el trabajo en **múltiples nodos especializados** que trabajan en secuencia, cada uno enfocado en una tarea específica.
- **Analogía**: Como cocinar una cena completa siguiendo un plan paso a paso (preparar ingredientes → cocinar → emplatar) en lugar de hacer todo simultáneamente.
- **Beneficio clave**: Mayor control del flujo, especialización de tareas, facilidad de debugging y arquitectura evolutiva.

El prompt chaining transforma procesos complejos en pipelines estructurados y predecibles.

---

## 🔑 Ideas clave
Conceptos fundamentales del prompt chaining y su arquitectura.

- **Prompt Chaining**: Patrón de diseño donde conectamos varios nodos de procesamiento en secuencia, cada uno especializado en una tarea específica.
- **Flujo típico**: `[Input] → [Nodo 1] → [Nodo 2] → [Nodo 3] → [Output]` donde cada nodo es un especialista.
- **Especialización**: Cada nodo tiene una responsabilidad única y bien definida (ej. traducir, analizar, resumir).
- **Estado compartido**: La información fluye entre nodos a través del estado del grafo (como vimos en Clase 4).
- **Control explícito**: El flujo está definido por el código, no por decisiones del modelo (a diferencia de agentes autónomos).
- **Razonamiento local**: Cada LLM se enfoca solo en su tarea, reduciendo carga cognitiva y mejorando precisión.

Esta arquitectura permite construir sistemas complejos de forma modular y mantenible.

---

## 🏭 Patrones de Orquestación
Diferentes arquitecturas para organizar nodos según las necesidades del problema.

### 1. 🔗 Patrón Secuencial
**Flujo:** `Nodo A → Nodo B → Nodo C` (lineal y predecible)

**Ejemplo práctico:**
```python
# Pipeline de análisis de texto
Entrada: "Texto largo en inglés"
→ Nodo 1: Traductor (inglés → español)
→ Nodo 2: Analizador de sentimiento
→ Nodo 3: Generador de resumen
Salida: "Resumen en español con análisis de sentimiento"
```

**¿Cuándo usarlo?**
- Cada paso depende del resultado del anterior
- Proceso claro y lineal sin bifurcaciones
- Transformación progresiva de datos (como un pipeline de producción)

### 2. ⚖️ Patrón Paralelo
**Flujo:** `Input → [Nodo A | Nodo B | Nodo C] → Consolidador` (ejecución simultánea)

**Ejemplo práctico:**
```python
# Análisis multi-perspectiva de un producto
Entrada: "Reseña de producto"
→ Nodo A: Análisis técnico (en paralelo)
→ Nodo B: Análisis de usabilidad (en paralelo)
→ Nodo C: Análisis de precio (en paralelo)
→ Consolidador: Combina resultados en informe completo
```

**Ventajas:**
- ⚡ **Mayor velocidad**: Ejecución simultánea reduce tiempo total
- 🎯 **Múltiples perspectivas**: Diferentes análisis del mismo input
- 🔄 **Redundancia**: Mayor confiabilidad al tener múltiples validaciones

### 3. 🧾 Patrón Condicional (Routing)
**Flujo:** Decisiones basadas en condiciones que determinan el siguiente nodo

**Ejemplo práctico:**
```python
# Clasificador de consultas de soporte
Entrada: "Consulta del cliente"
→ Clasificador (analiza tipo de consulta)
  │
  ├─ Si es "Técnico" → Nodo Soporte Técnico
  ├─ Si es "Facturación" → Nodo Finanzas
  └─ Si es "General" → Nodo Atención al Cliente
```

**¿Cuándo usarlo?**
- Diferentes tipos de input requieren procesamiento diferente
- Sistemas de clasificación y enrutamiento
- Workflows adaptativos según contexto

### 4. 🤖 Patrón Planificador (Planning)
**Flujo:** Un nodo "maestro" decide dinámicamente qué nodos ejecutar

**Ejemplo práctico:**
```python
# Sistema de investigación inteligente
Pregunta: "¿Cómo afecta el cambio climático a la agricultura?"
→ Planificador analiza y decide:
  - ✅ Necesita: Búsqueda web + Análisis de papers + Síntesis
  - ❌ No necesita: Generación de imágenes + Traducción
→ Ejecuta solo los nodos necesarios
```

**Ventajas:**
- Optimiza recursos ejecutando solo lo necesario
- Adaptable a diferentes tipos de consultas
- Reduce costos al evitar llamadas innecesarias

### 5. 🔍 Patrón Evaluador (Critic Loop)
**Flujo cíclico:** Generar → Evaluar → Mejorar → Repetir hasta cumplir criterios

**Ejemplo práctico:**
```python
# Generador de contenido con control de calidad
1. Generador: Crea artículo inicial
2. Evaluador: Revisa criterios (claridad, tono, longitud)
3. Si NO cumple: Genera feedback específico → vuelve al paso 1
4. Si SÍ cumple: Artículo aprobado → FIN
```

**¿Cuándo usarlo?**
- Necesitas garantizar calidad del output
- Iteración hasta cumplir estándares específicos
- Mejora progresiva basada en feedback

### 6. 🦀 Patrón Agente (ReAct)
**Flujo autónomo:** El LLM decide qué herramientas usar y cuándo

**Características:**
- **Razonamiento + Acción**: El agente piensa y actúa iterativamente
- **Autonomía**: Decide qué herramientas usar según el contexto
- **Menos control**: El flujo no está predefinido, el LLM tiene libertad
- **Reflexión iterativa**: Evalúa resultados y ajusta estrategia

**¿Cuándo usarlo?**
- Tareas abiertas sin flujo predefinido
- Necesitas que el agente explore soluciones
- Priorizas flexibilidad sobre control estricto

> **Nota**: Este patrón se verá en detalle en clases posteriores sobre agentes autónomos.

---

## ⚖️ Cuándo usar Chaining vs Chain of Thought
Decisión crítica: ¿Un solo prompt con razonamiento o múltiples nodos especializados?

### Usar Chain of Thought (Un Solo Prompt)
**Mejor para:**
- ✅ Tareas simples donde el modelo puede seguir todo el plan
- ✅ Instrucciones que caben cómodamente en un prompt
- ✅ Optimizar costos (una sola llamada al LLM)
- ✅ Modelos razonadores avanzados (OpenAI O1, Gemini 2.0 Flash Thinking, Claude con extended thinking)

**Ejemplo:** "Analiza este texto, identifica el sentimiento y genera un resumen" → Un solo prompt bien estructurado.

### Usar Chaining (Múltiples Nodos)
**Mejor para:**
- ✅ Pasos con alta carga cognitiva que necesitan enfoque dedicado
- ✅ Prompts muy largos que requieren división para claridad
- ✅ Integración con servicios externos (APIs, bases de datos)
- ✅ Combinar diferentes modelos (LLM + generación de imágenes + TTS)
- ✅ Arquitectura evolutiva que crecerá con el tiempo
- ✅ Debugging y mantenibilidad a largo plazo

**Ejemplo:** "Extrae datos de PDF → Genera tweet → Crea imagen para el tweet" → Requiere múltiples tecnologías.

### 💰 Consideración de Costos
- **Chaining**: Cada nodo = una llamada al modelo → Mayor costo
- **Chain of Thought**: Una sola llamada → Más económico
- **Balance**: Evalúa claridad arquitectónica vs costo según tu caso de uso

---

## ⚙️ Implementación en LangGraph
Cómo construir flujos secuenciales con LangGraph (recordando conceptos de Clase 4).

### Método 1: Construcción Manual
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    input: str
    result: str

# Definir funciones de nodos
def nodo_1(state: State) -> State:
    # Procesar y retornar estado actualizado
    return {"result": f"Procesado por nodo 1: {state['input']}"}

def nodo_2(state: State) -> State:
    return {"result": f"{state['result']} + nodo 2"}

def nodo_3(state: State) -> State:
    return {"result": f"{state['result']} + nodo 3"}

# Construir grafo
graph = StateGraph(State)
graph.add_node("nodo_1", nodo_1)
graph.add_node("nodo_2", nodo_2)
graph.add_node("nodo_3", nodo_3)

# Conectar en secuencia
graph.set_entry_point("nodo_1")
graph.add_edge("nodo_1", "nodo_2")
graph.add_edge("nodo_2", "nodo_3")
graph.add_edge("nodo_3", END)

app = graph.compile()
```

### Método 2: Atajo con `add_sequence`
```python
# Forma compacta para flujos lineales
builder.add_sequence([nodo_1, nodo_2, nodo_3])
```

> **Nota**: El nombre de la función se usa automáticamente como nombre del nodo. Útil para prototipos rápidos.

---

## 💼 Caso Práctico 1: Pipeline Extractor + Conversation
Ejemplo real de cómo estructurar un agente conversacional con preparación de datos.

### Arquitectura
```
INICIO → Extractor → Conversation → FIN
```

### Responsabilidades de cada nodo

**Nodo Extractor:**
- Prepara o extrae datos del estado inicial
- Procesa archivos o documentos si están presentes
- Enriquece el estado con información estructurada
- Ejemplo: Extraer texto de PDF antes de conversar

**Nodo Conversation:**
- Mantiene la interacción con el usuario
- Decide si necesita consultar RAG (como vimos en Clase 8)
- Usa el estado enriquecido por el extractor
- Genera respuesta final contextualizada

### Beneficios de esta arquitectura
- ✅ **Separación de responsabilidades**: Extracción vs conversación
- ✅ **Evolutiva**: Fácil agregar nodos entre extractor y conversation
- ✅ **Debugging simplificado**: Puedes inspeccionar estado después de cada nodo
- ✅ **Reutilizable**: El extractor puede usarse en otros flujos

---

## 💼 Caso Práctico 2: Pipeline de Social Media
Ejemplo que demuestra por qué el chaining es necesario para integrar múltiples tecnologías.

### Caso de Uso
Generar contenido completo para redes sociales (texto + imagen) desde un documento PDF.

### Arquitectura
```
PDF/Texto → Generador de Tweet → Generador de Imagen → Output Final
```

### Implementación paso a paso

**Nodo 1: Generador de Tweet**
- **Entrada**: Texto largo extraído del PDF
- **Proceso**: LLM resume y optimiza para Twitter (280 caracteres)
- **Salida**: Tweet optimizado guardado en estado

**Nodo 2: Generador de Imagen**
- **Entrada**: Tweet del nodo anterior
- **Proceso**: Usa modelo de imágenes (DALL·E, Stable Diffusion)
- **Prompt para imagen**: Basado en el contenido del tweet
- **Salida**: URL o archivo de imagen generada

**Nodo 3: Compositor Final**
- **Entrada**: Tweet + imagen
- **Salida**: Post completo listo para publicar

### ¿Por qué Chaining es necesario aquí?
- ❌ **Chain of Thought NO funciona**: Un LLM no puede generar imágenes
- ✅ **Requiere múltiples modelos**: LLM (texto) + modelo de difusión (imagen)
- ✅ **Tecnologías diferentes**: Cada paso usa APIs distintas
- ✅ **Dependencias claras**: La imagen depende del tweet generado

---

## 🔀 Workflows vs Agents: Diferencias Clave
Entender cuándo usar control explícito (workflows) vs autonomía (agents).

### Workflows (Control Explícito)
**Características:**
- ✅ Lógica de acción definida en el código
- ✅ Pasos, condiciones y herramientas explícitas
- ✅ Control total del flujo de ejecución
- ✅ Predecible y determinista
- ✅ RAG, APIs, function calls pre-configurados

**Ejemplo de flujo médico:**
```python
1. Preguntar nombre y apellido → esperar respuesta
2. Crear registro en BD con function call
3. Solicitar subida de fórmula médica → esperar archivo
4. Procesar PDF con extraction
5. Generar resumen médico
```

**¿Cuándo usar?**
- Procesos regulados o críticos (finanzas, salud)
- Necesitas garantizar pasos específicos
- Debugging y auditoría son prioritarios

### Agents (Autonomía del LLM)
**Características:**
- ✅ Se delega control al LLM
- ✅ El modelo decide qué herramientas usar y cuándo
- ✅ Proporciones: instrucciones generales + estado + tools
- ✅ Flexible y adaptable
- ✅ Arquitectura ReAct (Razonamiento + Acción)

**Ejemplo de agente investigador:**
```python
Objetivo: "Investiga sobre energía solar"
→ Agente decide:
  1. Buscar en web
  2. Analizar papers relevantes
  3. Consultar base de datos
  4. Sintetizar hallazgos
→ El orden y herramientas no están predefinidos
```

**¿Cuándo usar?**
- Tareas abiertas sin flujo fijo
- Necesitas exploración y creatividad
- El contexto determina las acciones necesarias

> **Nota**: Puedes combinar ambos enfoques (workflow con nodos agente para tareas específicas).

---

## ✅ Buenas Prácticas
Recomendaciones para diseñar y mantener sistemas con prompt chaining.

### 1. Visualización del Grafo
- **Usa LangGraph Studio**: Visualiza el flujo completo de tu chain
- **Valida conexiones**: Asegúrate de que todos los edges estén correctos
- **Documenta con diagramas**: Genera gráficos para tu equipo
- **Inspecciona estado**: Revisa cómo fluye la información entre nodos

### 2. Evita Over-Engineering
**⚠️ Advertencia**: No todo necesita múltiples nodos.

**Ejemplo educativo vs real:**
- ❌ "Generar broma → mejorar broma → añadir twist" → Innecesario con modelos razonadores
- ✅ "Extraer datos → Consultar API → Generar reporte" → Justificado por integración de servicios

**Pregunta clave:** ¿Un modelo razonador puede hacer esto en un solo prompt?

### 3. Arquitectura Evolutiva
- **Nodos preparatorios**: Déjalos aunque inicialmente no hagan mucho
- **Facilita bifurcaciones**: Estructura que permite agregar nodos fácilmente
- **Explícita**: Hace visible la arquitectura del sistema
- **Mantenible**: Cambios futuros son más simples

**Ejemplo:**
```python
# Hoy: Extractor → Conversation
# Mañana: Extractor → Validator → Enricher → Conversation
# La estructura inicial facilita la evolución
```

---

## 💭 Reflexión Final

Al diseñar tu pipeline con LangGraph, hazte estas preguntas:

1. **¿Los pasos pueden condensarse en un prompt con razonamiento?** → Considera Chain of Thought
2. **¿Se requiere integración de múltiples modelos/servicios?** → Usa Chaining
3. **¿La claridad arquitectónica justifica el costo adicional?** → Evalúa trade-offs
4. **¿El flujo necesitará evolucionar con más nodos?** → Diseña arquitectura evolutiva

El equilibrio entre chaining y chain of thought depende de tu caso de uso específico, restricciones de costo y necesidades de mantenibilidad.

---

## 📚 Recursos

- [LangGraph Workflows - Documentación Oficial](https://langchain-ai.github.io/langgraph/tutorials/workflows/)
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/)
- [Prompt Chaining Best Practices](https://www.promptingguide.ai/techniques/prompt_chaining)

---

## 🤔 Preguntas para Reflexionar

- ¿Qué problemas de tu proyecto actual resolverías con chaining?
- ¿Qué nodos agregarías a tu flujo para hacerlo más robusto?
- ¿Dónde tiene sentido usar chain of thought vs múltiples nodos en tu caso?
- ¿Cómo balanceas costo vs claridad arquitectónica en tu sistema?
- ¿Tu arquitectura actual permite evolucionar fácilmente?