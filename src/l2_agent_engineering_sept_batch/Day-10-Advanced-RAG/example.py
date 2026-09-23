"""Session 10: rewrite a question before retrieving context."""

from langgraph.graph import END, START, StateGraph


ARTICLES = {
    "password": "Use the self-service password reset page.",
    "vpn": "Reconnect the VPN client before contacting support.",
}


def rewrite_question(state):
    clearer = state["question"].lower().replace("login code", "password")
    return {"clearer_question": clearer}


def retrieve(state):
    context = "No match"
    for keyword, article in ARTICLES.items():
        if keyword in state["clearer_question"]:
            context = article
    return {"context": context}


def show_result(state):
    return {"answer": f"Retrieved: {state['context']}"}


graph_builder = StateGraph(dict)
graph_builder.add_node("rewrite", rewrite_question)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("show", show_result)
graph_builder.add_edge(START, "rewrite")
graph_builder.add_edge("rewrite", "retrieve")
graph_builder.add_edge("retrieve", "show")
graph_builder.add_edge("show", END)
graph = graph_builder.compile()

result = graph.invoke({"question": "I forgot my login code"})
print(result["answer"])
