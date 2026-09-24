"""Session 11: planner-executor rebuilt as an agent.

Problem: a workflow version of this file would pick a plan with an if/elif
rule and then validate it before running anything. Here the model is the
planner itself: it must choose exactly one next action from a fixed,
allowed list, and its own output is what LangGraph routes on -- so this is
an agent, not a workflow. The bounded/validated part of the original
pattern still matters: an out-of-list answer from the model is corrected to
a safe default instead of being executed, so the model never gets to invent
an action nobody approved.
"""

import ollama
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

ALLOWED_ACTIONS = ["reset_password", "restart_vpn_client", "escalate_to_human"]


class State(TypedDict):
    request: str
    action: str
    result: str


def plan_next_action(state: State):
    prompt = (
        "Choose exactly one next action for this IT request from this list: "
        f"{', '.join(ALLOWED_ACTIONS)}.\n"
        "Return only the action name, nothing else.\n\n"
        f"Request: {state['request']}"
    )
    response = ollama.chat(
        model="gpt-oss:120b-cloud",
        messages=[{"role": "user", "content": prompt}],
    )
    action = response["message"]["content"].strip().lower()
    if action not in ALLOWED_ACTIONS:
        action = "escalate_to_human"
    return {"action": action}


def route_to_action(state: State):
    return state["action"]


def reset_password(state: State):
    return {"result": "executed reset_password: password reset link sent"}


def restart_vpn_client(state: State):
    return {"result": "executed restart_vpn_client: VPN client restarted"}


def escalate_to_human(state: State):
    return {"result": "executed escalate_to_human: handed to a human specialist"}



graph_builder = StateGraph(State)
graph_builder.add_node("plan", plan_next_action)
graph_builder.add_node("reset_password", reset_password)
graph_builder.add_node("restart_vpn_client", restart_vpn_client)
graph_builder.add_node("escalate_to_human", escalate_to_human)


graph_builder.add_edge(START, "plan")
graph_builder.add_conditional_edges("plan", route_to_action)
graph_builder.add_edge("reset_password", END)
graph_builder.add_edge("restart_vpn_client", END)
graph_builder.add_edge("escalate_to_human", END)
graph = graph_builder.compile()

# result = graph.invoke({"request": "I forgot my password"})

# result = graph.invoke({"request": "I am not able to connect to VPN"})

result = graph.invoke({"request": "for my genai training I want 64GB RAM"})
print(result["result"])
