# Day 11 — Agentic Patterns

## What You'll Learn Today

- Compare a fixed pipeline against a routed pattern and explain when each one fits.
- Build a router where the model's own output picks the specialist node — and see why that, specifically, is what makes it an agent.
- Understand how a planner-executor pattern bounds a plan before anything runs, even when the model is the one choosing the action.
- Understand how an evaluator-optimizer pattern drafts, checks, and revises at most once, with the model acting as the judge.
- Learn to compare patterns by their state, their model calls, their stop rule, and their main failure risk.
- Make a small change to `example.py`, predict the effect, and explain what happened in your own words.

## Why This Matters

Before you pick a pattern name, you first need to look at the actual task and its constraints — the pattern comes after the problem, not before. If different teams need different kinds of help, a router that classifies the request once and sends it to one specialist branch makes sense. If the task is "draft something, then check it against clear criteria," an evaluator-optimizer loop fits better than a straight pipeline. You already know several of these shapes from earlier sessions — a pipeline, a branch, a bounded loop, an approval gate, a retrieval step — so today is mostly about naming them clearly and knowing which one to reach for.

Today's examples all call the model, and in every one of them the model's own output is what LangGraph routes on — that specific detail is what makes each of these an agent rather than a workflow. It is worth holding onto the contrast: a workflow can call a model too (Day 2 does exactly that) and still stay a workflow, because the path through the graph is fixed regardless of what the model says. The four files here are deliberately built so the path is *not* fixed — the model's answer decides which node runs next.

## Key Concepts

**Fixed Pipeline.** When the sequence of steps never changes and no dynamic choice is needed, a straight line of steps is usually the simplest and best design — don't reach for something fancier just because it feels more "agentic." `pattern-1-fixed-pipeline.py` shows what happens the moment you give that pipeline a real decision: it stops being a fixed pipeline and becomes a router-shaped agent instead.

**Router Pattern.** A router classifies the incoming request once, writes that decision into the state, and sends the request down exactly one specialist branch. Because the route is written into state, you can always trace which branch a request took and why. Here, the classification is the model's own judgment call, not a keyword rule — so the main risk is a wrong classification from the model, not a wrong classification from a hardcoded rule; larger systems add fallback branches and labeled tests for the router itself either way.

**Planner-Executor.** This pattern separates deciding what to do from actually doing it: the planner creates a bounded plan, the plan is validated, and only then does the executor perform the allowed steps. Planning is not the same as execution authority. In `pattern-3-planner-executor.py`, the model is the planner — it must pick exactly one action from a fixed, allowed list, and anything outside that list is corrected to a safe default rather than run. That is the bounded, validated part of the pattern: the model never gets execution authority over anything it wasn't explicitly permitted to choose.

**Evaluator-Optimizer.** This pattern drafts an answer, checks it against clear pass/fail criteria, revises once if it fails, and then stops regardless of the second result. In `pattern-4-evaluator-optimizer.py` the check itself is a model call — the model acts as the judge and its PASS/FAIL verdict is what selects the next node. A first draft that already passes goes straight to the end; there is no reason to revise something that's already acceptable.

**Verification, Reflection, and Multi-Agent (know the difference).** A verifier checks independent evidence — facts, schemas, tests, citations — and is a stronger guarantee than a model simply feeling confident about its own answer. Reflection is different: it's a model critiquing its own draft and suggesting changes, which can improve style but never proves the draft is actually true. Multi-agent systems add specialist roles and handoffs coordinated by an orchestrator, but every extra agent you add is also an extra way for coordination to fail — so more agents is not automatically better. This session doesn't build a multi-agent system; it's an overview to know by name.

## Code Walkthrough — `Day-11-Agentic-Patterns/example.py`

```python
"""Session 11: router pattern rebuilt as an agent.

Problem: an IT helpdesk gets free-text requests and must send each one to
one of two specialists -- network or account. A workflow would route with a
plain if/else rule (see Day-04-Routing-Control-Flow/example.py for exactly
that technique). Here the model reads the request and its own output picks
the specialist, and LangGraph routes to a different node depending on that
output -- that is this course's own definition of the agent boundary
(CLAUDE.md: "the agent boundary is specifically ... where the model's
output selects the next node").
"""

import ollama
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    request: str
    route: str
    answer: str


def router(state: State):
    prompt = (
        "Choose the specialist for this IT request.\n"
        "Return only NETWORK for a VPN or connectivity problem.\n"
        "Return only ACCOUNT for anything else.\n\n"
        f"Request: {state['request']}"
    )
    response = ollama.chat(
        model="gpt-oss:120b-cloud",
        messages=[{"role": "user", "content": prompt}],
    )
    route = response["message"]["content"].strip().upper()
    if route not in ("NETWORK", "ACCOUNT"):
        route = "ACCOUNT"
    return {"route": route.lower()}


def select_specialist(state: State):
    return state["route"]


def network_specialist(state: State):
    return {"answer": "Network specialist: reconnect the VPN."}


def account_specialist(state: State):
    return {"answer": "Account specialist: check your access."}


graph_builder = StateGraph(State)
graph_builder.add_node("router", router)
graph_builder.add_node("network", network_specialist)
graph_builder.add_node("account", account_specialist)
graph_builder.add_edge(START, "router")
graph_builder.add_conditional_edges("router", select_specialist)
graph_builder.add_edge("network", END)
graph_builder.add_edge("account", END)
graph = graph_builder.compile()

result = graph.invoke({"request": "My VPN is disconnected"})
print(result["answer"])
```

1. `State` is a `TypedDict` naming every field the graph can hold: `request`, `route`, `answer`. Passing it to `StateGraph(State)` (instead of a plain `dict`) tells LangGraph to merge each node's returned keys into state one field at a time, instead of replacing the whole state with whatever a node returns.
2. `router(state)` builds a prompt asking the model to pick `NETWORK` or `ACCOUNT`, calls `ollama.chat(...)`, and reads the model's reply. An unexpected reply falls back to `ACCOUNT` so the route is never something outside the two permitted values. It writes this choice into state as `route`.
3. `select_specialist(state)` simply reads back the `route` value from state — this is the function LangGraph uses to decide which node runs next. Because `route` came from the model's own output, the model is the thing actually choosing the next node — this is the agent boundary, not the `ollama.chat` call by itself.
4. `network_specialist` and `account_specialist` are the two possible next nodes. Each one just returns a canned `answer` string.
5. The graph wires it together: `START` always goes to `router`, then `add_conditional_edges` uses `select_specialist` to send execution to either `network` or `account`, and both of those lead to `END`.
6. `graph.invoke({"request": "My VPN is disconnected"})` runs the graph with a sample request, and the script prints whichever `answer` the chosen specialist produced. Because the model call is live, re-running the file can occasionally pick a different route for a borderline request — that variability is itself worth noticing.

**The other three patterns**, each in its own file in this folder, follow the same rule — the model's output is what LangGraph routes on:

- `pattern-1-fixed-pipeline.py` — a ticket gets a genuine two-way choice (close with a standard reply, or escalate); the model decides, and `add_conditional_edges` routes to a different node depending on that decision.
- `pattern-3-planner-executor.py` — the model is the planner: it must choose exactly one next action from a fixed, allowed list, and LangGraph routes straight to that action's node.
- `pattern-4-evaluator-optimizer.py` — the model judges the draft (`PASS`/`FAIL`) and that verdict is what routes to `finish` or `revise`.

## Hands-On Lab (~30 minutes)

**Goal:** send a request to one specialist node, chosen by the model.

**Graph to draw:** `START -> router -> network or account -> END`

Sign in to Ollama once per machine, then open only `example.py` in `Day-11-Agentic-Patterns\`. Set up and run it from the repository root in Windows Command Prompt:

```cmd
cd L2-Agent-Engineering
uv sync
ollama signin
uv run python Day-11-Agentic-Patterns\example.py
```

**Code walkthrough steps:** read the short description at the top of the file, find each node function, find `StateGraph` and where nodes get registered, then follow the edges from `START` to `END`. Try to predict the printed result before you actually run the file.

**Small change to try:** change the `request` text in the `graph.invoke(...)` call and observe which specialist the model selects. Try a borderline request (something that mentions both a password and a VPN) and see which way the model breaks the tie.

**Control question:** the router selects one permitted specialist, and the model's own output is what makes that selection — nothing in the graph hardcodes the route.

## Assignment

**Goal:** make one small change to `example.py` and explain how the result changes.

**Steps:**
1. Read the sample input near the bottom of `example.py`.
2. Predict the current output without running the file.
3. Run it: `uv run python Day-11-Agentic-Patterns\example.py` (from the repository root).
4. Change only one input value or one short input sentence.
5. Predict the new route or output.
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:** keep the example in one Python file. Use LangGraph directly. Don't add a test folder or helper package. Don't replace `uv` commands with another package manager. Use the Windows Command Prompt commands shown above. Use the exact `ollama.chat(model="gpt-oss:120b-cloud", messages=[...])` call already in the file — don't switch to `ChatOllama` or another wrapper.

## Before You Move to Day 12

- [ ] The file runs without errors (and you've run `ollama signin` at least once on this machine).
- [ ] You can name the state, the nodes, and the edges in this graph.
- [ ] You can explain who (or what) controls the next step — and confirm it **is** the model's own output here, unlike Days 1–5.
- [ ] You made one small change, predicted the effect first, then ran it and confirmed (or corrected) your prediction.
- [ ] You can write, in plain words, what you changed, what happened, and why.
