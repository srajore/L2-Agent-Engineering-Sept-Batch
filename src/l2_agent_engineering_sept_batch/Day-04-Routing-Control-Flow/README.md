# Day 4 — Routing and Control Flow

## What You'll Learn Today

- Why a single fixed path through a graph isn't always enough, and when you need branching instead.
- How to read and write a conditional edge that sends state down one of several routes.
- How to split "decide" (an assessment node) from "select" (a router function) so routing logic is explicit and easy to trace.
- Why this session's routing rules are all developer-written, and why model-driven routing waits until Session 6.

## Why This Matters

Session 3 gave you one straight path through a graph, but real requests don't all deserve the same treatment — for example, a password-related request and a general request need different replies. Burying that decision-making inside one large function makes it hard to inspect or test, so today you pull it out into an explicit routing step instead. The core idea is simple — one node decides which route applies, and a conditional edge sends execution to the matching node — and once you can do that reliably with fixed rules, you have exactly the foundation Session 6 needs when a model, rather than a rule, starts making a bounded choice.

## Key Concepts

**Why one path isn't enough.** A fixed graph is ideal when the next step is genuinely unconditional, but many real workflows need different lanes — different requests deserve different handling. The fix is to make that branching explicit in the graph itself, rather than hiding it inside a large function where it's hard to see or test.

**Separating assessment from routing.** It helps to split "decide" from "select": one node writes a route decision into state, and a separate router function reads that decision and returns the destination label LangGraph should send it to. In `example.py`, `choose_route` is the assessment node — it checks whether the word "password" appears in the (lowercased) request and writes `route` as either `"account"` or `"general"` — and `next_node` is the router function, which just reads `state["route"]` back out and returns it. Every label the router can return needs a matching node registered in the graph: here that's exactly two, `account` and `general`.

**Two routes, one router.** This session's example is a simple two-way router: a password-related request takes the `account` path and gets "Open the password reset page," and anything else takes the `general` path and gets "A support engineer will review the request." Both routes are registered as real nodes and both converge on `END`, so the two full paths through the graph are `START -> choose_route -> account -> END` and `START -> choose_route -> general -> END`.

**Not built in this file.** Real routing graphs often need more than two lanes — an approval route for high-impact requests, a bounded retry loop (an `attempts` counter in state, routed back to assessment until a maximum is hit), a `trace` list recording every node visited, or several branches converging on a shared summary node. None of that is in `example.py` — it stays intentionally small, with one assessment node and two destinations, so the conditional-edge pattern itself is easy to trace by hand. Keep these richer ideas in mind as directions a routing graph can grow in, not as something this file demonstrates.

## Code Walkthrough — `Day-04-Routing-Control-Flow/example.py`

```python
"""Session 4: Send a request to one of two graph paths."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    request: str
    route: str
    answer: str


def choose_route(state: State):
    if "password" in state["request"].lower():
        return {"route": "account"}

    return {"route": "general"}


def next_node(state: State):
    return state["route"]


def account_help(state: State):
    return {"answer": "Open the password reset page."}


def general_help(state: State):
    return {"answer": "A support engineer will review the request."}


# StateGraph now knows the structure of our State
graph_builder = StateGraph(State)

graph_builder.add_node("choose_route", choose_route)
graph_builder.add_node("account", account_help)
graph_builder.add_node("general", general_help)

graph_builder.add_edge(START, "choose_route")

graph_builder.add_conditional_edges(
    "choose_route",
    next_node
)

graph_builder.add_edge("account", END)
graph_builder.add_edge("general", END)

graph = graph_builder.compile()


result = graph.invoke({
    "request": "I forgot my password"
})

print(result["answer"])
```

1. `State(TypedDict)` declares the shape of the graph's state up front: a `request` string that comes in, a `route` string that records the routing decision, and an `answer` string that holds the final reply. Each node function is type-hinted `state: State`, and `StateGraph(State)` tells LangGraph to use that typed shape instead of a plain `dict`.
2. `choose_route` is the assessment node. It checks whether "password" appears in the (lowercased) request, and returns a `route` value of either `"account"` or `"general"`.
3. `next_node` is the router function. It simply reads `state["route"]` and returns it — that returned string is the name of the node LangGraph should go to next.
4. `account_help` and `general_help` are the two destination nodes. Each returns a canned `answer` for its lane.
5. `graph_builder.add_conditional_edges("choose_route", next_node)` is the key new piece compared to earlier sessions: instead of one fixed `add_edge`, this line tells LangGraph to call `next_node` after `choose_route` runs, and follow whichever route name it returns.
6. The two possible full paths are `START -> choose_route -> account -> END` and `START -> choose_route -> general -> END`. The sample request contains "password," so it takes the `account` path and prints "Open the password reset page."

## Hands-On Lab (~30 minutes)

**Graph to draw:** `START -> choose_route -> account or general -> END`

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-04-Routing-Control-Flow\example.py
```

**Walkthrough steps:**

1. Read the short description at the top of the file.
2. Find each node function (`choose_route`, `next_node`, `account_help`, `general_help`).
3. Find `StateGraph` and the node registrations.
4. Follow the edges from `START` to `END`, paying attention to `add_conditional_edges`.
5. Predict the printed result before you run the file.

**Small change to try:** Try one request that mentions a password, and one that mentions a VPN instead, and compare which route each one takes.

**Control question:** Who chooses the route here? Developer-written code chooses from a fixed, known set of routes — there is no model involved yet.

## Assignment

**Goal:** Make one small change to `example.py` and explain how the result changes.

**Steps:**

1. Read the sample input near the bottom of `example.py`.
2. Predict the current output without running the file.
3. Run the example from the repository root:
   ```cmd
   uv run python Day-04-Routing-Control-Flow\example.py
   ```
4. Change only one input value or one short input sentence.
5. Predict the new route or output.
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:**

- Keep the example in one Python file.
- Use LangGraph directly.
- Do not add a test folder or helper package.
- Do not replace `uv` commands with another package manager.
- Use the Windows Command Prompt commands shown above.
- Do not add an Ollama call — this session's example is intentionally deterministic.

## Before You Move to Day 5

- The file runs successfully on your machine.
- You can name the state, all four nodes, and the edges, including the conditional edge.
- You can explain who controls the next step (developer-written rules pick from fixed routes).
- You tried both a password request and a general request and saw each one take a different path.
- Your three-sentence explanation matches what you actually observed.
