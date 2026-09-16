# Day 5 — Tool Integration

## What You'll Learn Today

- What a "tool" actually is: just a normal Python function with a name, called from your graph.
- How to pass values into a tool through state, and how to store its result back into state.
- How to read a two-node workflow that calls a tool and then formats the result.
- How to trace values through state from start to finish, step by step.
- Why calling a tool from a fixed workflow does not, by itself, make a system an agent.

## Why This Matters

So far your graphs have only ever done text and arithmetic work directly inside node functions. Today introduces the idea of a "tool" — but without any of the mystery that word sometimes carries. A tool is simply a plain Python function, like `calculate_total(price, quantity)`, that your workflow calls by name. Calling it a "tool" instead of just "a function" matters because it's the same vocabulary you'll need once agents start choosing which capability to call — but for now, the developer decides exactly when the tool runs, and the model isn't involved in that decision at all. Getting comfortable with this small, fixed example — state in, tool call, state out, formatted answer out — sets up Session 6, where a model gets to choose between actions for the first time.

## Key Concepts

**A tool is just a Python function.** `calculate_total(price, quantity)` multiplies two numbers and returns the result — nothing more exotic than that. Calling it a "tool" signals that it's a named capability a workflow (and later, an agent) can call, but the function itself stays ordinary Python, testable on its own like any other function.

**How the workflow uses it.** The graph starts with a small state containing `price` and `quantity`. The first node reads both values, calls the tool, and returns just the new `total` value as a state update — the node doesn't need to copy over every existing field, only the one it changed. The second node then reads `total` from state and turns it into a friendly sentence, keeping formatting cleanly separate from calculation. This mirrors the "one responsibility per node" idea from Session 3: one node's whole job is to calculate, and the other node's whole job is to explain.

**Building and tracing the graph.** Building this graph is the same four steps as always: create a `StateGraph`, add both nodes, add the fixed edges between them, and compile. Because every edge here is fixed, `START -> use_tool -> answer -> END` is the only possible path — nothing about the input changes which nodes run, only what values move through them. Calling `graph.invoke(...)` sends the starting dictionary into `use_tool` first; you can trace this by hand: `price` 25 and `quantity` 3 go in, `calculate_total` returns 75 and it's stored as `total`, and then `create_answer` turns that into "The total price is 75."

**Still a workflow, not an agent.** Every edge in this graph is fixed before the program ever runs, so nothing here is decided at runtime — the developer chose this exact path, and calling a tool did not change that. Tool use alone does not make a system an agent; what will make Session 6 different is that a model, not a rule, gets to choose which permitted action to take next.

## Code Walkthrough — `Day-05-Tool-Integration/example.py`

```python
"""Session 5: Call a plain Python function from a graph node."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    price: float
    quantity: int
    total: float
    answer: str


# This is a normal Python function — our "tool"
def calculate_total(price, quantity):
    return price * quantity


# Graph node
def use_tool(state: State):
    total = calculate_total(
        state["price"],
        state["quantity"]
    )

    return {"total": total}


# Graph node
def create_answer(state: State):
    return {
        "answer": f"The total price is {state['total']}."
    }


# StateGraph now uses our State definition
graph_builder = StateGraph(State)

graph_builder.add_node("use_tool", use_tool)
graph_builder.add_node("answer", create_answer)

graph_builder.add_edge(START, "use_tool")
graph_builder.add_edge("use_tool", "answer")
graph_builder.add_edge("answer", END)

graph = graph_builder.compile()


result = graph.invoke({
    "price": 25,
    "quantity": 3
})

print(result["answer"])
```

1. `State(TypedDict)` declares the shape of the graph's state: `price` and `quantity` come in, `total` is written by the tool node, and `answer` is written by the formatting node. Each node function is type-hinted `state: State`, and `StateGraph(State)` uses that typed shape instead of a plain `dict`.
2. `calculate_total` is the tool — a plain function with no LangGraph code in it at all, just multiplication.
3. `use_tool` is the first node. It reads `price` and `quantity` from state, calls the tool, and returns the result as a `total` update.
4. `create_answer` is the second node. It reads `total` from state and builds the final sentence, returned as `answer`.
5. The graph is built with the usual four steps — create, add nodes, add fixed edges, compile — giving the path `START -> use_tool -> answer -> END`.
6. `graph.invoke({"price": 25, "quantity": 3})` runs the graph, and the printed result is "The total price is 75."

## Hands-On Lab (~30 minutes)

**Graph to draw:** `START -> use_tool -> answer -> END`

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-05-Tool-Integration\example.py
```

**Walkthrough steps:**

1. Read the short description at the top of the file.
2. Find each node function (`use_tool`, `create_answer`) and the tool function (`calculate_total`).
3. Find `StateGraph` and the node registrations.
4. Follow the edges from `START` to `END`.
5. Predict the printed result before you run the file.

**Small change to try:** Change `price` or `quantity` and predict the new total before running the file again. Keep the graph structure itself unchanged — only change the input values.

**Control question:** Who decides when the tool runs? The developer does — the tool call happens at a fixed point in a fixed graph, every time.

## Assignment

**Goal:** Make one small change to `example.py` and explain how the result changes.

**Steps:**

1. Read the sample input near the bottom of `example.py`.
2. Predict the current output without running the file.
3. Run the example from the repository root:
   ```cmd
   uv run python Day-05-Tool-Integration\example.py
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

## Before You Move to Day 6

- The file runs successfully on your machine.
- You can name the tool, both nodes, the fixed path, the input, and the output.
- You can explain why Session 5's example is a workflow and not an agent.
- You changed `price` or `quantity`, predicted the new total first, then confirmed it by running the file again.
- Your three-sentence explanation matches what you actually observed.
