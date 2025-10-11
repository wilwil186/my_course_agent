# src/agents/simple.py
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    msg: str

def node(state: State) -> State:
    return {"msg": state.get("msg", "") + " ✅"}

builder = StateGraph(State)
builder.add_node("node", node)
builder.add_edge(START, "node")
builder.add_edge("node", END)
app = builder.compile()
