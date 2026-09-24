"""Session 11: evaluator-optimizer rebuilt as an agent.

Problem: a workflow version of this file would check the draft with a
deterministic rule (does the text contain "Step" and "KB-"). Here the model
itself judges the draft, and its own PASS/FAIL verdict is what LangGraph
routes on -- the model's output selects the next node, which is this
course's own definition of an agent. The pattern still revises at most
once and stops regardless of the second result.
"""

import sys
from typing import TypedDict

import ollama
from langgraph.graph import END, START, StateGraph

sys.stdout.reconfigure(encoding="utf-8")  # the model may answer with punctuation Command Prompt cannot print


class State(TypedDict):
    request: str
    draft: str
    verdict: str
    final: str


def draft_answer(state: State):
    print("Inside draft_answer")
    prompt = f"Write a one-sentence IT support answer to this request: {state['request']}"
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[{"role": "user", "content": prompt}],
    )
    return {"draft": response["message"]["content"].strip()}


def evaluate_draft(state: State):
    prompt = (
        "Judge this draft IT support answer.\n"
        "Return only PASS if it includes a numbered step and a KB- citation.\n"
        "Return only FAIL otherwise.\n\n"
        f"Draft: {state['draft']}"
    )
    response = ollama.chat(
        model="gpt-oss:120b-cloud",
        messages=[{"role": "user", "content": prompt}],
    )
    verdict = response["message"]["content"].strip().upper()
    if verdict not in ("PASS", "FAIL"):
        verdict = "FAIL"
    return {"verdict": verdict}


def route_after_evaluate(state: State):
    return "finish" if state["verdict"] == "PASS" else "revise"


def finish(state: State):
    return {"final": state["draft"]}


def revise_draft(state: State):
    print("Inside revise_draft")
    prompt = (
        "Rewrite this answer so it includes a numbered step (like 'Step 1: ...') "
        f"and a citation like 'KB-1042'.\n\nOriginal: {state['draft']}"
    )
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[{"role": "user", "content": prompt}],
    )
    return {"final": response["message"]["content"].strip()}


graph_builder = StateGraph(State)
graph_builder.add_node("draft", draft_answer)
graph_builder.add_node("evaluate", evaluate_draft)
graph_builder.add_node("finish", finish)
graph_builder.add_node("revise", revise_draft)

graph_builder.add_edge(START, "draft")
graph_builder.add_edge("draft", "evaluate")
graph_builder.add_conditional_edges("evaluate", route_after_evaluate)
graph_builder.add_edge("finish", END)
graph_builder.add_edge("revise", END)
graph = graph_builder.compile()

result = graph.invoke({"request": "My laptop screen is broken?"})
print(result["final"])
