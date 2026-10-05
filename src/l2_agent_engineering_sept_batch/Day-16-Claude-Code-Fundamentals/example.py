"""Session 16: a tiny LangGraph file learners can safely edit."""

from langgraph.graph import END, START, StateGraph


def label_ticket(state):
    text = state["ticket"].lower()
    if "vpn" in text:
        label = "network"
    else:
        label = "general"
    return {"label": label}


graph_builder = StateGraph(dict)
graph_builder.add_node("label_ticket", label_ticket)
graph_builder.add_edge(START, "label_ticket")
graph_builder.add_edge("label_ticket", END)
graph = graph_builder.compile()

result = graph.invoke({"ticket": "VPN is disconnected"})
print("Ticket label:", result["label"])

# Try this: ask Claude Code to add a "password" label.
