"""Session 12: build a small, clearly labelled model context."""

import sys
from typing import TypedDict

import ollama
from langgraph.graph import END, START, StateGraph

sys.stdout.reconfigure(encoding="utf-8")  # the model may answer with punctuation Command Prompt cannot print


MODEL = "gpt-oss:120b-cloud"


class State(TypedDict):
    user: str
    fact: str
    context: str
    answer: str


def build_context(state: State):
    context = f"USER: {state['user']}\nFACT: {state['fact']}"
    return {"context": context}


def ask_model(state: State):
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": state["context"]}],
    )
    return {
        "context": state["context"],
        "answer": response["message"]["content"],
    }


graph_builder = StateGraph(State)
graph_builder.add_node("build_context", build_context)
graph_builder.add_node("ask_model", ask_model)

graph_builder.add_edge(START, "build_context")
graph_builder.add_edge("build_context", "ask_model")
graph_builder.add_edge("ask_model", END)

graph = graph_builder.compile()

result = graph.invoke({"user": "How do I reset my password?", "fact": "Use /reset."})
print("Context sent to the model:\n", result["context"])
print("\nAnswer:\n", result["answer"])
