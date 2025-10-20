from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import START, END, StateGraph
from typing import Sequence, TypedDict
from typing_extensions import Annotated
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from datetime import datetime

# Define tools for booking
@tool
def booking_appointment(fecha: str, tiempo: str, doctor: str, paciente: str) -> str:
    """Book an appointment for a patient with a doctor at a specific date and time."""
    # Mock logic for booking
    return (
        f"Cita confirmada: paciente {paciente}, doctor {doctor}, "
        f"fecha {fecha}, hora {tiempo}."
    )

@tool
def get_appointment_availability(fecha: str, tiempo: str, doctor: str) -> str:
    """Get available time slots for a doctor on a specific date."""
    # Mock logic for availability
    return (
        f"Disponibilidad para {doctor} en {fecha} {tiempo}: 14:00, 15:00, 16:00. "
        "Indica tu hora preferida."
    )

# Tools list
tools = [booking_appointment, get_appointment_availability]

# Get today's date
today = datetime.now().strftime("%Y-%m-%d")

# State
class State(TypedDict, total=False):
    messages: Annotated[Sequence, add_messages]

# Model
model = ChatOllama(model="llama3.1:70b")

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

Today: {today}
Additional rules: Do not book appointments more than 30 days in advance.

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""

prompt = PromptTemplate.from_template(system_prompt)
agent = create_react_agent(model, tools, prompt)

# Node
def booking_node(state: State) -> dict:
    messages = state.get("messages", [])
    response = agent.invoke({"input": messages[-1].content if messages else "", "today": today})
    return {"messages": [AIMessage(content=response.get("output", "No response."))]}

# Graph
builder = StateGraph(State)
builder.add_node("booking", booking_node)
builder.add_edge(START, "booking")
builder.add_edge("booking", END)

app = builder.compile()

# Helper for CLI/tests
def ask(text: str, thread_id: str = "booking-demo") -> str:
    result = app.invoke(
        {"messages": [HumanMessage(content=text)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    last = result["messages"][-1]
    return getattr(last, "content", str(last))

__all__ = ["app", "ask", "State"]