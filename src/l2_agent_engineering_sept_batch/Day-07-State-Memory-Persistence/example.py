"""Session 7: remember values between calls with a thread ID."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from typing import TypedDict


# This small state definition lets LangGraph save each value separately.
class MemoryState(TypedDict, total=False):
    name: str
    saved_name: str
    question: str


def remember_name(state):
    if state.get("name"):
        return {"saved_name": state["name"]}
    return {}


graph_builder = StateGraph(MemoryState)
graph_builder.add_node("remember", remember_name)
graph_builder.add_edge(START, "remember")
graph_builder.add_edge("remember", END)
graph = graph_builder.compile(checkpointer=InMemorySaver())

# The same thread ID continues the same conversation.
settings = {"configurable": {"thread_id": "student-1"}}
graph.invoke({"name": "Asha"}, config=settings)
result = graph.invoke({"question": "What is my name?"}, config=settings)

print("Remembered name:", result["saved_name"])
