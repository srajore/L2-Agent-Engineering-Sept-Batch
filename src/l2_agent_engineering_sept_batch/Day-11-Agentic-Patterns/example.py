"""Session 11: router pattern rebuilt as an agent.

Problem: an IT helpdesk gets free-text requests and must send each one to
one of two specialists -- network or account. A workflow would route with a
plain if/else rule (see Day-04-Routing-Control-Flow/example.py for exactly
that technique). Here the model reads the request and its own output picks
the specialist, and LangGraph routes to a different node depending on that
output -- that is this course's own definition of the agent boundary
(CLAUDE.md: "the agent boundary is specifically ... where the model's
output selects the next node").
"""

import ollama
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    request: str
    route: str
    answer: str


def router(state: State):
    prompt = (
        "Choose the specialist for this IT request.\n"
        "Return only NETWORK for a VPN or connectivity problem.\n"
        "Return only ACCOUNT for anything else.\n\n"
        f"Request: {state['request']}"
    )
    response = ollama.chat(
        model="gpt-oss:120b-cloud",
        messages=[{"role": "user", "content": prompt}],
    )
    route = response["message"]["content"].strip().upper()

    if route not in ("NETWORK", "ACCOUNT"):
        route = "ACCOUNT"
    return {"route": route.lower()}


def select_specialist(state: State):
    return state["route"]


def network_specialist(state: State):
    return {"answer": "Network specialist: reconnect the VPN."}


def account_specialist(state: State):
    return {"answer": "Account specialist: check your access."}


graph_builder = StateGraph(State)
graph_builder.add_node("router", router)
graph_builder.add_node("network", network_specialist)
graph_builder.add_node("account", account_specialist)

graph_builder.add_edge(START, "router")
graph_builder.add_conditional_edges("router", select_specialist)
graph_builder.add_edge("network", END)
graph_builder.add_edge("account", END)
graph = graph_builder.compile()

# result = graph.invoke({"request": "My VPN is disconnected"})
result = graph.invoke({"request": "My forgot my password and cannot log in"})
print(result["answer"])
