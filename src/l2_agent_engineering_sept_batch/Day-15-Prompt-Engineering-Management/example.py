"""Session 15: select and use a clearly versioned prompt."""

import sys

import ollama
from langgraph.graph import END, START, StateGraph

sys.stdout.reconfigure(encoding="utf-8")  # the model may answer with punctuation Command Prompt cannot print


MODEL = "gpt-oss:120b-cloud"
PROMPTS = {
    "v1": "Answer the IT request.",
    "v2": "Answer the IT request in one short sentence. Do not guess.",
}


def create_prompt(state):
    instruction = PROMPTS[state["version"]]
    return {"prompt": f"{instruction}\nRequest: {state['request']}"}


def ask_model(state):
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": state["prompt"]}],
    )
    return {"answer": response["message"]["content"]}


graph_builder = StateGraph(dict)
graph_builder.add_node("create_prompt", create_prompt)
graph_builder.add_node("ask_model", ask_model)
graph_builder.add_edge(START, "create_prompt")
graph_builder.add_edge("create_prompt", "ask_model")
graph_builder.add_edge("ask_model", END)
graph = graph_builder.compile()

result = graph.invoke({"version": "v1", "request": "The VPN is down."})
print("Prompt version: v1")
print(result["answer"])
