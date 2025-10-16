from langgraph.graph import StateGraph, START, END
from src.agents.support.state import State
from src.agents.support.nodes.extractor.node import extract_info
from src.agents.support.nodes.conversation.node import conversation

builder = StateGraph(State)
builder.add_node("extract", extract_info)
builder.add_node("converse", conversation)

builder.add_edge(START, "extract")
builder.add_edge("extract", "converse")
builder.add_edge("converse", END)

app = builder.compile()