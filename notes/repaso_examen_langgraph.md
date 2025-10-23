# 📚 Guía de Repaso - Examen LangGraph y LangChain

**Resultado: 11/15 (7.33)** - Necesitas 9.0 para aprobar

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
**Tu respuesta:** Faltaba importar `HumanMessage` desde `launching.core`

**PROBLEMA:** Esta respuesta fue marcada incorrecta. Revisa:
- ¿Era desde otro módulo? (langchain.core, langchain.schema, etc.)
- ¿El problema era otro tipo de import?
- ¿Era un problema de configuración en vez de import?
- Verificar el namespace correcto del import

**ESTUDIO:** Revisar el debugging del primer intento con FastAPI

### 5. **Thread_id y Error invalid value** ⚠️
**Tu respuesta:** `make_graph` no recibió el checkpointer para ese thread_id

**POSIBLES CAUSAS DEL ERROR:**
- Thread_id podría estar corrupto o mal formateado
- Conflicto entre diferentes versiones de checkpointer
- Estado inconsistente en la base de datos
- Problema de sincronización entre threads

**ESTUDIO:** Revisar el segmento de debugging sobre thread_id

### 7. **Prompt Chaining - Malas Prácticas** ⚠️
**Tu respuesta:** Mejor usar patrón evaluator para refinar iterativamente

**REVISA EN LA CLASE (minuto 05:04):**
- ¿El problema es la falta de iteración?
- ¿Es sobre acoplamiento entre prompts?
- ¿Complejidad innecesaria para tareas simples?
- ¿Problema de mantenibilidad?

**ESTUDIO:** Ver específicamente minuto 05:04 sobre malas prácticas

### 12. **Jinja2 vs String Format** ⚠️
**Tu respuesta:** Jinja2 mejora compatibilidad con modelos no-LangChain

**OTRAS VENTAJAS POSIBLES:**
- Control de flujo más potente (if/for)
- Mejor manejo de variables complejas
- Sintaxis más limpia y legible
- Reutilización de templates

**ESTUDIO:** Buscar ventajas específicas de Jinja2 mencionadas en clase

---

## 🎯 ESTRATEGIA PARA EL REINTENTO

### Prioridades de Estudio:
1. **ALTA:** Preguntas 2, 5, 7, 12 (las 4 incorrectas)
2. **MEDIA:** Repasar conceptos de debugging y arquitectura
3. **BAJA:** Revisar rápidamente las 11 correctas

### Checklist Pre-Examen:
- [ ] Revisar minuto 05:04 sobre malas prácticas (pregunta 7)
- [ ] Verificar el namespace correcto de HumanMessage (pregunta 2)
- [ ] Entender casos de error con thread_id (pregunta 5)
- [ ] Comparar Jinja2 vs string format detalladamente (pregunta 12)
- [ ] Hacer esquema de arquitectura cognitiva
- [ ] Repasar patrones: ReAct, Evaluator, Prompt Chaining

### Tips para el Examen:
- Lee las opciones antes de responder
- Busca palabras clave como "fundamental", "principal", "más probable"
- Si mencionan tiempo específico (05:04), es información precisa de la clase
- Diferencia entre lo que es "mejor práctica" vs "funcionalmente posible"

---

## 📝 NOTAS RÁPIDAS

**Arquitectura:**
```
LangChain (herramientas) 
    ↓
LangGraph (orquestación)
    ↓
Nodos (modifican) + Edges (enrutan)
```

**Jerarquía de Mensajes:**
- SystemMessage: Configuración
- HumanMessage: Usuario
- AIMessage: Respuesta del modelo

**Debugging Common:**
- ImportError → pyproject.toml
- Invalid thread_id → checkpointer issue
- Tool no usada → razonamiento del modelo

¡Éxito en tu próximo intento! 💪