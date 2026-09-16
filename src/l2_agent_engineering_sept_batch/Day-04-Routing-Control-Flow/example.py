"""Session 4: Send a request to one of two graph paths."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    request: str
    route: str
    answer: str


def choose_route(state: State):
    if "password" in state["request"].lower():
        state["route"] = "account"
        return state["route"]

    return {"route": "general"}


def next_node(state: State):
    return state["route"]


def account_help(state: State):
    return {"answer": "Open the password reset page."}


def general_help(state: State):
    return {"answer": "A support engineer will review the request."}


# StateGraph now knows the structure of our State
graph_builder = StateGraph(State)

graph_builder.add_node("choose_route", choose_route)
graph_builder.add_node("account", account_help)
graph_builder.add_node("general", general_help)

graph_builder.add_edge(START, "choose_route")

graph_builder.add_conditional_edges(
    "choose_route",
    next_node
)

graph_builder.add_edge("account", END)
graph_builder.add_edge("general", END)

graph = graph_builder.compile()


result = graph.invoke({
    "request": "I account got locked"
})

print(result["answer"])