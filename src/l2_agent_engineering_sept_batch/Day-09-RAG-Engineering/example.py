"""Session 9: retrieve local text and give it to Ollama."""

import sys

import ollama
from langgraph.graph import END, START, StateGraph

sys.stdout.reconfigure(encoding="utf-8")  # the model may answer with punctuation Command Prompt cannot print


MODEL = "gpt-oss:120b-cloud"
ARTICLES = {
    "password": "Reset a password at portal.example/reset.",
    "vpn": "For VPN issues, reconnect and enter your company password.",
}


def retrieve(state):
    question = state["question"].lower()
    context = "No matching article found."
    for keyword, article in ARTICLES.items():
        if keyword in question:
            context = article
    return {"question": state["question"], "context": context}


def answer(state):
    prompt = f"Use only this context: {state['context']}\nQuestion: {state['question']}"
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return {"answer": response["message"]["content"]}


graph_builder = StateGraph(dict)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("answer", answer)
graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "answer")
graph_builder.add_edge("answer", END)
graph = graph_builder.compile()

result = graph.invoke({"question": "How do I reset my password?"})
print(result["answer"])
