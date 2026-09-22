"""Session 8: pause a graph and ask a human for approval."""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ApprovalState(TypedDict, total=False):
    action: str
    approved: bool
    message: str


def ask_for_approval(state):
    approved = interrupt("Approve this action? (yes/no)")
    return {"approved": approved}


def finish(state):
    message = "Action completed." if state["approved"] else "Action cancelled."
    return {"message": message}


graph_builder = StateGraph(ApprovalState)
graph_builder.add_node("approval", ask_for_approval)
graph_builder.add_node("finish", finish)
graph_builder.add_edge(START, "approval")
graph_builder.add_edge("approval", "finish")
graph_builder.add_edge("finish", END)
graph = graph_builder.compile(checkpointer=InMemorySaver())

settings = {"configurable": {"thread_id": "approval-1"}}

graph.invoke({"action": "Reset the account"}, config=settings)

answer = input("Approve the account reset? (yes/no): ")
result = graph.invoke(Command(resume=answer.lower() == "yes"), config=settings)
print(result["message"])
