# 🧠 Clase 12: Prompts Dinámicos con LangChain y Templates Condicionales

> Curso: **Crear Agentes de AI con LangGraph**  
> Objetivo: Aprender a gestionar prompts de forma eficaz, hacerlos dinámicos y limpios con LangChain, PromptTemplate y un motor de plantillas tipo Jinja2, para mejorar los resultados en agentes orquestados con LangGraph.

---

## 🎯 Resumen general

Una buena ingeniería de prompting marca la diferencia en agentes con LangGraph. Aunque uses los modelos más potentes y un orquestador de grafos, un prompt mediocre produce resultados mediocres. En esta clase, aprenderás a gestionar prompts de forma eficaz, hacerlos dinámicos y limpios con LangChain, PromptTemplate y un motor de plantillas tipo Jinja2, sin depender de técnicas específicas.

---

## 🤔 ¿Por qué el prompting es vital en agentes con LangGraph?

Un prompt guía al language model hacia el objetivo. No es opcional: es crítico. Técnicas como zero shot, few shot y chain of thought pueden mejorar los resultados según el modelo y la tarea, pero el foco está en cómo gestionarlos a nivel de ingeniería para agentes orquestados con LangGraph.

Los ejemplos con una sola línea son prácticos para enseñar orquestación, pero no son buenos prompts. Un buen prompt define roles, formato y atributos con claridad. Cada carácter cuenta: espacios extra y saltos de línea innecesarios añaden tokens y ruido.

Habilidades clave: ingeniería de prompt, orquestación de agentes, manejo de estado, dinamización de variables, control de formato.

---

## ⚙️ Técnicas de prompting y su impacto

### Zero Shot
Útil cuando no hay ejemplos, pero puede ser inconsistente.

### Few Shot
Añade ejemplos y guía estilo y formato.

### Chain of Thought
Favorece la explicación paso a paso; suele funcionar mejor en XML que en Markdown.

### Rol del estado en prompts dinámicos
Con un gestor de estado como LangGraph, puedes derivar tono, contexto o parámetros y inyectarlos dinámicamente. Si algo es fijo, va en el template; si cambia, se modela como variable.

---

## 🛠️ Crear prompts efectivos con PromptTemplate de LangChain

Usa PromptTemplate para declarar variables sin obligarte a resolverlas al definir el string. Evita concatenaciones con f-strings temprano; inyecta datos al formatear.

### Ejemplo base de template

```python
from langchain.prompts import PromptTemplate

template = """\
Instrucciones en Markdown:
- Sigue el rol indicado.
- Respeta el formato solicitado.
Fecha actual: {fecha_actual}
Texto del anuncio: {texto_anuncio}
"""

prompt_tmpl = PromptTemplate(template=template)

# Al formatear, envías las variables dinámicas
prompt_final = prompt_tmpl.format(
    fecha_actual="2024-05-01",
    texto_anuncio="Lanza tu producto con 20% de descuento."
)
print(prompt_final)
```

El backslash inicial evita que el primer salto de línea se convierta en tokens. Si faltan variables, el template lanza un error: te obliga a completar lo necesario.

### Evitar errores al inyectar variables
Define variables en el template y envíalas en .format cuando estén disponibles. Si aún no existen en memoria, no bloquees la definición del template.

### Usar partial variables por defecto
Puedes declarar valores por defecto con partial variables para que el template funcione aunque no envíes todo.

```python
from datetime import date

prompt_tmpl = PromptTemplate(
    template=template,
    partial_variables={
        "fecha_actual": lambda: date.today().isoformat()
    }
)

# Solo envías lo que cambia en tiempo de ejecución
prompt_final = prompt_tmpl.format(
    texto_anuncio="Actualiza tu sitio con nuevas funcionalidades."
)
print(prompt_final)
```

Útil para campos como "fecha actual" que pueden autocompletarse. Mantiene el prompt coherente y reduce errores en orquestación.

---

## 🔧 Templates condicionales con Jinja2 para prompts limpios

Cuando necesitas variaciones pequeñas (por ejemplo, saludar por nombre si está disponible), un motor de plantillas tipo Jinja2 permite bloques condicionales en el propio template. Así evitas mantener dos prompts casi iguales.

### Template con condicional y limpieza de espacios

```python
from langchain.prompts import PromptTemplate

rag_template = """\
Eres un asistente superútil que responde al mensaje del usuario.
{% if name -%}
El cliente se llama {{ name }}.
{%- endif %}
Mensaje del usuario: {{ user_message }}
"""

prompt_tmpl = PromptTemplate(
    template=rag_template,
    input_variables=["user_message", "name"],
    template_format="jinja2"  # Motor condicional mencionado
)

# Si no hay name, puedes usar partial para neutralizarlo
prompt_tmpl = PromptTemplate(
    template=rag_template,
    input_variables=["user_message"],
    partial_variables={"name": None},
    template_format="jinja2"
)

print(prompt_tmpl.format(user_message="¿Cómo puedo optimizar mi sitio web?"))
```

El bloque {% if name -%} … {%- endif %} condicionalmente incluye la sección. Los guiones “-” en los tags recortan saltos de línea y evitan huecos. Ideal para asistentes de RAG donde el campo "customer name" podría faltar.

### Activar el motor de templates condicional
Instala la dependencia del motor Jinja2 y reinicia tu entorno si es necesario. Declara template_format="jinja2" al crear el PromptTemplate.

### Limpiar saltos de línea innecesarios
Usa guiones en los tags del condicional para recortar espacios y saltos. Mantén un solo salto cuando separes indicaciones distintas.

---

## 📚 Recursos recomendados

- [Introduction — Jinja Documentation (3.1.x)](https://jinja.palletsprojects.com/en/3.1.x/intro/)
- Curso de Prompt Engineering

---

## ✅ Checklist de esta clase

- [ ] Entender por qué el prompting es vital en agentes con LangGraph.
- [ ] Aplicar técnicas como zero shot, few shot y chain of thought.
- [ ] Crear prompts efectivos con PromptTemplate de LangChain.
- [ ] Usar partial variables para valores por defecto.
- [ ] Implementar templates condicionales con Jinja2.
- [ ] Limpiar saltos de línea innecesarios en prompts.

**Siguiente clase → Clase 13: [Tema siguiente, si se conoce]**

---

## 💬 Preguntas y comentarios

Te leo en los comentarios: ¿qué estrategias usas para dinamizar prompts y mantenerlos limpios en producción?