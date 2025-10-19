from langchain_core.prompts import PromptTemplate

# System prompt específico para el nodo conversation
template = """\
Eres un asistente útil y conciso para atender a {name}.

{% if context %}
Contexto disponible: {context}
Usa este contexto para responder preguntas de manera precisa.
{% endif %}

Responde de manera clara y profesional. Si no tienes información suficiente, indícalo amablemente.
"""

prompt_template = PromptTemplate.from_template(template, template_format="jinja2")