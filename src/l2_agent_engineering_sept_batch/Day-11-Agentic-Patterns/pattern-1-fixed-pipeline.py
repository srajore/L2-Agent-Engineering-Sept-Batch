"""Session 11: what a fixed pipeline looks like once it gains a real choice.

Problem: a plain fixed pipeline (receive -> reply -> close, every ticket the
same three steps in the same order) has no decision point, so adding a
model call to it would still be a workflow -- a bare model call is not what
makes something an agent. Here the ticket gets a genuine two-way choice:
close it with a standard reply, or escalate to a human. The model's own
output makes that choice and LangGraph routes to a different node depending
on it -- so this is an agent.
"""

import ollama
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    request: str
    log: list[str]
    decision: str
    answer: str


def receive_request(state: State):
    return {"log": [f"received: {state['request']}"]}


def agent_decide(state: State):
    prompt = (
        "Decide how to handle this IT ticket.\n"
        "Return only CLOSE if a standard self-service reply is enough.\n"
        "Return only ESCALATE if it needs a human specialist.\n\n"
        f"Ticket: {state['request']}"
    )
    response = ollama.chat(
        model="gpt-oss:120b-cloud",
        messages=[{"role": "user", "content": prompt}],
    )
    decision = response["message"]["content"].strip().upper()
    if decision not in ("CLOSE", "ESCALATE"):
        decision = "ESCALATE"
    return {"decision": decision.lower()}


def route_after_decision(state: State):
    return state["decision"]


def close_with_standard_reply(state: State):
    log = state["log"] + ["closed with standard reply"]
    answer = "Thanks for reaching out -- your ticket is logged and closed with our standard fix."
    return {"log": log, "answer": answer}


def escalate(state: State):
    log = state["log"] + ["escalated to a human specialist"]
    return {"log": log, "answer": "This needs a human specialist -- escalated."}


graph_builder = StateGraph(State)
graph_builder.add_node("receive", receive_request)
graph_builder.add_node("agent_decide", agent_decide)
graph_builder.add_node("close", close_with_standard_reply)
graph_builder.add_node("escalate", escalate)
graph_builder.add_edge(START, "receive")
graph_builder.add_edge("receive", "agent_decide")
graph_builder.add_conditional_edges("agent_decide", route_after_decision)
graph_builder.add_edge("close", END)
graph_builder.add_edge("escalate", END)
graph = graph_builder.compile()

result = graph.invoke({"request": "My VPN is disconnected"})
for step in result["log"]:
    print(step)
print(result["answer"])
