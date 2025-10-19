# Herramientas específicas para el nodo conversation (open source)
from langchain_core.tools import tool
from duckduckgo_search import DDGS

@tool
def web_search(query: str) -> str:
    """Busca información en la web usando DuckDuckGo.
    
    Args:
        query: La consulta de búsqueda
        
    Returns:
        Resultados de búsqueda relevantes
    """
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=3)
        if not results:
            return "No se encontraron resultados."
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"{i}. {result['title']}\n"
                f"   {result['body']}\n"
                f"   URL: {result['href']}"
            )
        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"Error al buscar: {str(e)}"

tools = [web_search]