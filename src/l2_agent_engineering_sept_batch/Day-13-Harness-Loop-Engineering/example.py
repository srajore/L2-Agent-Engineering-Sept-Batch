"""Session 13: a loop (act/verify/retry) inside a harness (explicit attempt limit)."""

from langgraph.graph import END, START, StateGraph

MAX_ATTEMPTS = 3
PASS_THRESHOLD = 10


def act(state):
    attempt = state["attempt"] + 1
    return {"attempt": attempt, "result": attempt * 5}


def verify(state):
    return {
        "attempt": state["attempt"],
        "result": state["result"],
        "passed": state["result"] >= PASS_THRESHOLD,
    }


def enforce_limit(state):
    if state["passed"]:
        return "done"
    if state["attempt"] >= MAX_ATTEMPTS:
        return "give_up"
    return "try_again"


graph_builder = StateGraph(dict)
graph_builder.add_node("act", act)
graph_builder.add_node("verify", verify)
graph_builder.add_edge(START, "act")
graph_builder.add_edge("act", "verify")
graph_builder.add_conditional_edges(
    "verify",
    enforce_limit,
    {"try_again": "act", "done": END, "give_up": END},
)
graph = graph_builder.compile()

result = graph.invoke({"attempt": 0})
print("Attempts:", result["attempt"])
print("Final result:", result["result"])
if result["passed"]:
    print("Stopped because: verification passed")
else:
    print(f"Stopped because: harness hit its {MAX_ATTEMPTS}-attempt limit")
