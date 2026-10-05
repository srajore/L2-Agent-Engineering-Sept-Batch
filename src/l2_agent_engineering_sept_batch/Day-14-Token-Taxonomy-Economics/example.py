"""Session 14: estimate the size of each part of a model request."""

from langgraph.graph import END, START, StateGraph


def count_words(text):
    return len(text.split())


def measure(state):
    counts = {
        "instruction": count_words(state["instruction"]),
        "question": count_words(state["question"]),
        "context": count_words(state["context"]),
    }
    return {"counts": counts, "total": sum(counts.values())}


graph_builder = StateGraph(dict)
graph_builder.add_node("measure", measure)
graph_builder.add_edge(START, "measure")
graph_builder.add_edge("measure", END)
graph = graph_builder.compile()

result = graph.invoke(
    {
        "instruction": "Answer using the context.",
        "question": "How do I reset my password?",
        "context": "Open the reset page.",
    }
)
print("Word estimate by part:", result["counts"])
print("Total word estimate:", result["total"])
