"""Session 3: learn state, nodes, edges, START, and END."""

from langgraph.graph import END, START, StateGraph


def clean_text(state):
    return {"text": state["text"].strip()}


def count_words(state):
    return {"word_count": len(state["text"].split())}


def create_message(state):
    message = f"Your requirement has {state['word_count']} words."
    return {"message": message}


graph_builder = StateGraph(dict)
graph_builder.add_node("clean", clean_text)
graph_builder.add_node("count", count_words)
graph_builder.add_node("message", create_message)
graph_builder.add_edge(START, "clean")
graph_builder.add_edge("clean", "count")
graph_builder.add_edge("count", "message")
graph_builder.add_edge("message", END)
graph = graph_builder.compile()

result = graph.invoke({"text": "  User can reset a password  "})
print(result["message"])
