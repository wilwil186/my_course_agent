# Clase 9 — Prompt Chaining: Orquestación de Agentes en Secuencia

**Objetivo:** Aprender a dividir tareas complejas en pasos simples y especializados, usando **LangGraph** para crear flujos de trabajo claros y fáciles de mantener. Esto se basa en lo que vimos en clases anteriores, como el estado compartido (Clase 4) y la integración con herramientas externas (Clase 8).

---

## 🧠 ¿Por qué usar Prompt Chaining?
Imagina que quieres cocinar una comida complicada. Si intentas hacer todo al mismo tiempo (cortar, cocinar, servir), es un caos. Mejor seguir un plan: primero prepara los ingredientes, luego cocina, y al final sirve. Eso es exactamente lo que hace el **Prompt Chaining**.

- **Problema con un solo prompt:** Cuando pides algo muy complejo a un modelo de IA (como analizar un texto largo, traducirlo y resumirlo todo junto), puede confundirse, cometer errores o ser difícil de arreglar si algo sale mal.
- **Solución con Prompt Chaining:** Divide la tarea en pasos pequeños, cada uno manejado por un "nodo" especializado. Cada nodo hace solo una cosa bien, y pasa el resultado al siguiente.
- **Beneficios simples:** Más fácil de entender, probar y mejorar. Como armar un rompecabezas paso a paso en lugar de todo de golpe.

En resumen, transforma tareas grandes en un proceso ordenado y predecible.

---

## 🔑 Conceptos Básicos
Aquí van las ideas principales, explicadas de forma sencilla.

- **Prompt Chaining:** Es como una cadena de pasos donde cada "nodo" (un pequeño programa o función) hace una tarea específica y pasa la información al siguiente. Ejemplo: Paso 1: Traducir texto. Paso 2: Analizar el sentimiento. Paso 3: Crear un resumen.
- **Flujo típico:** Empieza con la entrada (lo que le das al sistema), pasa por varios nodos, y termina con el resultado final.
- **Especialización:** Cada nodo es un experto en una cosa, como un traductor o un resumidor. Esto hace que cada parte sea más precisa.
- **Estado compartido:** Como vimos en Clase 4, la información viaja entre nodos a través de un "estado" común, como una caja donde cada nodo agrega o cambia cosas.
- **Control claro:** Tú decides cómo se conectan los nodos (en código), no el modelo de IA. Esto es diferente a los agentes autónomos, donde la IA decide más.
- **Enfoque simple:** Cada nodo solo piensa en su tarea, lo que reduce errores y hace todo más eficiente.

Esto te permite construir sistemas complejos de manera modular, como agregar piezas a un Lego.

---

## 🏭 Tipos de Patrones para Organizar los Pasos
Dependiendo de lo que necesites, puedes organizar los nodos de diferentes formas. Aquí te explico cada uno con ejemplos fáciles.

### 1. 🔗 Patrón Secuencial (Uno tras Otro)
**Cómo funciona:** Los nodos van en línea recta, uno después del otro.

**Ejemplo fácil:**
- Entrada: Un texto largo en inglés.
- Nodo 1: Lo traduce al español.
- Nodo 2: Analiza si el sentimiento es positivo o negativo.
- Nodo 3: Crea un resumen corto.
- Salida: Un resumen en español con el análisis del sentimiento.

**¿Cuándo usarlo?** Cuando cada paso necesita el resultado del anterior, como una receta de cocina.

### 2. ⚖️ Patrón Paralelo (Varios al Mismo Tiempo)
**Cómo funciona:** Varios nodos trabajan al mismo tiempo y luego se combinan.

**Ejemplo fácil:**
- Entrada: Una reseña de un producto.
- Nodo A: Analiza lo técnico (calidad, durabilidad).
- Nodo B: Analiza la facilidad de uso.
- Nodo C: Analiza el precio.
- Luego, un nodo combina todo en un informe completo.

**Ventajas:** Es más rápido porque se hace en paralelo, y obtienes diferentes puntos de vista.

### 3. 🧾 Patrón Condicional (Decide Según la Situación)
**Cómo funciona:** Un nodo decide cuál es el siguiente paso basado en condiciones.

**Ejemplo fácil:**
- Entrada: Una consulta de un cliente.
- Nodo clasificador: Mira si es sobre "soporte técnico", "facturación" o "general".
- Luego, envía a un nodo específico: Si es técnico, va a soporte; si es facturación, a finanzas.

**¿Cuándo usarlo?** Cuando el proceso cambia según el tipo de entrada, como un menú de opciones.

### 4. 🤖 Patrón Planificador (Elige lo Necesario)
**Cómo funciona:** Un nodo "jefe" decide qué pasos ejecutar, sin hacer todo siempre.

**Ejemplo fácil:**
- Pregunta: "¿Cómo afecta el cambio climático a la agricultura?"
- Planificador: Decide que necesita buscar en web, analizar artículos y sintetizar, pero no generar imágenes.
- Ejecuta solo esos nodos.

**Ventajas:** Ahorra tiempo y dinero al no hacer pasos innecesarios.

### 5. 🔍 Patrón Evaluador (Mejora Hasta que Esté Bien)
**Cómo funciona:** Crea algo, lo revisa, y si no está bien, lo mejora repetidamente.

**Ejemplo fácil:**
- Nodo generador: Crea un artículo.
- Nodo evaluador: Revisa si es claro, tiene buen tono y longitud adecuada.
- Si no cumple, da feedback y vuelve a generar hasta que esté perfecto.

**¿Cuándo usarlo?** Cuando necesitas calidad alta, como en escritura profesional.

### 6. 🦀 Patrón Agente (La IA Decide)
**Cómo funciona:** La IA elige qué herramientas usar y en qué orden, con libertad.

**Características:** Piensa y actúa paso a paso, adaptándose al contexto.

**¿Cuándo usarlo?** Para tareas abiertas donde no hay un plan fijo, como investigar un tema nuevo.

> **Nota:** Este patrón lo veremos más en clases futuras sobre agentes autónomos.

---

## ⚖️ ¿Cuándo Usar Chaining o Chain of Thought?
Una decisión importante: ¿Hacer todo en un solo prompt con razonamiento interno, o dividir en múltiples nodos?

### Usa Chain of Thought (Un Solo Prompt)
**Mejor para:**
- Tareas simples que el modelo puede manejar solo.
- Cuando quieres ahorrar costos (solo una llamada a la IA).
- Ejemplo: "Analiza este texto, encuentra el sentimiento y resume" – todo en un prompt claro.

### Usa Chaining (Múltiples Nodos)
**Mejor para:**
- Pasos que necesitan mucho enfoque o integración con otras herramientas (como APIs o imágenes).
- Cuando el proyecto crecerá y necesitarás agregar más pasos.
- Ejemplo: Extraer datos de un PDF, generar un tweet y crear una imagen – necesita diferentes tecnologías.

**Costo:** Chaining cuesta más porque cada nodo es una llamada separada, pero vale la pena por la claridad.

---

## ⚙️ Cómo Implementarlo en LangGraph
Usando lo que aprendimos en Clase 4 sobre grafos y estado.

### Ejemplo Básico: Construcción Manual
Aquí un código simple para un flujo secuencial.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

# Define el estado (como una caja de datos compartida)
class State(TypedDict):
    input: str  # Lo que entra
    result: str  # Lo que se acumula

# Nodo 1: Procesa la entrada
def nodo_1(state: State) -> State:
    return {"result": f"Procesado por nodo 1: {state['input']}"}

# Nodo 2: Agrega más
def nodo_2(state: State) -> State:
    return {"result": f"{state['result']} + nodo 2"}

# Nodo 3: Termina
def nodo_3(state: State) -> State:
    return {"result": f"{state['result']} + nodo 3"}

# Construye el grafo
graph = StateGraph(State)
graph.add_node("nodo_1", nodo_1)
graph.add_node("nodo_2", nodo_2)
graph.add_node("nodo_3", nodo_3)

# Conecta los nodos en orden
graph.set_entry_point("nodo_1")
graph.add_edge("nodo_1", "nodo_2")
graph.add_edge("nodo_2", "nodo_3")
graph.add_edge("nodo_3", END)

# Compila y listo para usar
app = graph.compile()
```

### Atajo Rápido
Para flujos lineales, usa `add_sequence` para simplificar.

---

## 💼 Ejemplos Prácticos
Veamos casos reales para entender mejor.

### Caso 1: Pipeline Extractor + Conversation
Arquitectura: Inicio → Extractor → Conversation → Fin

- **Extractor:** Prepara datos, como sacar texto de un PDF (usa herramientas de Clase 8).
- **Conversation:** Habla con el usuario, usando los datos preparados.

Beneficios: Separa la preparación de la charla, fácil de expandir y probar.

### Caso 2: Pipeline de Social Media
Crea un post completo (texto + imagen) desde un PDF.

- Nodo 1: Genera un tweet corto del texto largo.
- Nodo 2: Crea una imagen basada en el tweet (usando modelos como DALL·E).
- Nodo 3: Combina todo en un post listo.

¿Por qué chaining? Porque un solo modelo no puede generar imágenes; necesitas diferentes herramientas.

---

## 🔀 Workflows vs Agents: ¿Cuál Elegir?
- **Workflows (Control Tú):** Tú defines los pasos exactamente. Bueno para procesos estrictos como en salud o finanzas.
- **Agents (La IA Decide):** La IA elige qué hacer. Bueno para tareas creativas o abiertas.

Puedes combinar: Un workflow con un nodo agente para partes flexibles.

---

## ✅ Consejos Prácticos
- Usa herramientas como LangGraph Studio para ver y probar tu flujo.
- No compliques: Solo divide si es necesario (pregúntate si un modelo razonador puede hacerlo solo).
- Diseña para crecer: Empieza simple, pero deja espacio para agregar nodos después.

---

## 💭 Reflexión Final
Pregúntate:
1. ¿Puedes hacer esto en un solo prompt?
2. ¿Necesitas integrar varias herramientas?
3. ¿Vale la pena el costo extra por claridad?
4. ¿Tu diseño permite cambios futuros?

Elige según tu proyecto: equilibrio entre simplicidad, costo y mantenibilidad.

---

## 📚 Recursos
- Documentación de LangGraph.
- Tutoriales y mejores prácticas.

---

## 🤔 Preguntas para Pensar
- ¿Qué partes de tu proyecto mejorarías con chaining?
- ¿Dónde usarías chain of thought en lugar de nodos?
- ¿Cómo equilibras costo y claridad en tu sistema?