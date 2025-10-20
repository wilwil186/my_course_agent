from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import START, END, StateGraph
from typing import Sequence, TypedDict
from typing_extensions import Annotated
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
import requests

# Define tools
@tool
def getProducts() -> str:
    """Get a list of available products."""
    # Mock or real API call to get products
    try:
        response = requests.get("https://fakeapi.platzi.com/en/rest/products")
        products = response.json()
        return f"Productos disponibles: {[p['title'] for p in products[:5]]}"  # Limit for brevity
    except:
        return "Error al obtener productos."

@tool
def getWeather(city: str) -> str:
    """Get the current weather for a given city."""
    # Get lat/long from geocoding API
    try:
        geo_response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}")
        geo_data = geo_response.json()
        if geo_data.get("results"):
            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            # Get weather
            weather_response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true")
            weather_data = weather_response.json()
            current = weather_data.get("current_weather", {})
            return f"El clima en {city}: Temperatura {current.get('temperature', 'N/A')}°C, Viento {current.get('windspeed', 'N/A')} km/h."
        else:
            return f"No se encontró ubicación para {city}."
    except:
        return "Error al obtener el clima."

# Tools list
tools = [getProducts, getWeather]

# State
class State(TypedDict, total=False):
    messages: Annotated[Sequence, add_messages]

# Model
model = ChatOllama(model="qwen2.5:7b")

# Standard ReAct prompt
system_prompt = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

You are a sales assistant capable of finding products and providing weather information for a city.

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""

prompt = PromptTemplate.from_template(system_prompt)
agent = create_react_agent(model, tools, prompt)

# Node
def react_node(state: State) -> dict:
    messages = state.get("messages", [])
    response = agent.invoke({"input": messages[-1].content if messages else ""})
    return {"messages": [AIMessage(content=response.get("output", "No response."))]}

# Graph
builder = StateGraph(State)
builder.add_node("react", react_node)
builder.add_edge(START, "react")
builder.add_edge("react", END)

app = builder.compile()

# Helper for CLI/tests
def ask(text: str, thread_id: str = "react-demo") -> str:
    result = app.invoke(
        {"messages": [HumanMessage(content=text)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    last = result["messages"][-1]
    return getattr(last, "content", str(last))

__all__ = ["app", "ask", "State"]