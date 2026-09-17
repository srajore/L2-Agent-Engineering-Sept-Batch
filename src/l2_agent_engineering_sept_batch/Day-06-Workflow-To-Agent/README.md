# Day 6 — From Workflow to Agent

## What You'll Learn Today

- Explain the difference between a fixed workflow (Session 5) and an agent that lets the model choose the next step (Session 6).
- Describe the two permitted actions the model may choose from: `TOOL` or `ANSWER`.
- Trace both routes through the graph: the tool branch and the direct-answer branch.
- Explain how the code validates the model's answer before using it to route, instead of trusting it blindly.
- Run `example.py`, predict its output, then change the sample request and predict again.

## Why This Matters

Up to Session 5, you built the whole path yourself: every edge in the graph was fixed, so the program always followed `START -> use_tool -> answer -> END`. Today that changes for the first time. The graph still defines the only legal choices, but now the model itself decides which of two allowed paths to take: call a tool, or answer directly. This is the smallest possible version of an "agent" — not because the model has unlimited freedom, but because it makes one bounded decision instead of following a path you wrote in advance. Learning to trust a model's choice while still keeping it inside a small, validated menu is the core idea of the whole session.

## Key Concepts

**Two Permitted Actions.** The model is only ever allowed to answer with one of two words: `TOOL` or `ANSWER`. Giving the model a small menu like this, instead of open-ended freedom, makes its behavior much easier to understand, test, and reason about.

**Calling the Course Model.** The `decide` node sends one prompt to `ollama.chat` using the fixed model `gpt-oss:120b-cloud`. The prompt tells the model exactly when to return `TOOL` (a password request) and when to return `ANSWER` (anything else) — it asks for one word only.

**Read, Normalize, and Validate.** Real model output can vary slightly in spacing or capitalization, so the code strips whitespace and converts the text to uppercase before comparing it. Then it checks the result against the two allowed values. If the model ever returns something else, the code safely falls back to `ANSWER` rather than letting an unexpected value control the graph. This means model text never becomes an arbitrary node name — it can only ever select one of the two paths you already built.

**State and the Conditional Edge.** The `decide` node stores its choice by returning `{"action": action}`, so the decision becomes a visible part of the state instead of a hidden variable. The `next_node` function then reads that field and returns `"tool"` or `"answer"`, which LangGraph matches against the two real node names to pick the branch. This routing function is only two lines long — routing logic doesn't need to be complicated to be effective.

**One Decision, Then Stop.** Both the `tool` branch and the `answer` branch lead straight to `END`. The model makes exactly one decision per run — bounded does not mean uncontrolled.

## Code Walkthrough — `Day-06-Workflow-To-Agent/example.py`

```python
"""Session 6: the model chooses one permitted next action."""

import ollama
from langgraph.graph import END, START, StateGraph


MODEL = "gpt-oss:120b-cloud"


def decide(state):
    prompt = """Choose the next action for this IT request.
Return only TOOL for a password request.
Return only ANSWER for anything else.

Request: """ + state["request"]

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    action = response["message"]["content"].strip().upper()

    if action not in ["TOOL", "ANSWER"]:
        action = "ANSWER"

    return {"action": action}


def next_node(state):
    return state["action"].lower()


def use_tool(state):
    return {"answer": "Tool result: open the password reset page."}


def answer_directly(state):
    return {"answer": "Direct answer: your request was received."}


graph_builder = StateGraph(dict)
graph_builder.add_node("decide", decide)
graph_builder.add_node("tool", use_tool)
graph_builder.add_node("answer", answer_directly)
graph_builder.add_edge(START, "decide")
graph_builder.add_conditional_edges("decide", next_node)
graph_builder.add_edge("tool", END)
graph_builder.add_edge("answer", END)
graph = graph_builder.compile()

result = graph.invoke({"request": "How do I reset my password?"})
print(result["answer"])
```

1. `decide` builds a prompt containing the IT request and sends it to Ollama, asking for exactly one word back.
2. The response text is cleaned up (stripped and uppercased) and checked against the two allowed values, falling back to `ANSWER` if anything unexpected comes back.
3. `decide` returns `{"action": action}`, which LangGraph merges into the shared state dictionary.
4. `next_node` reads `state["action"]` and returns it in lowercase — this is the conditional edge that routes to either the `tool` node or the `answer` node.
5. `use_tool` and `answer_directly` are plain Python functions with no model call — they just build the final `answer` text for their branch.
6. Both branches connect straight to `END`, and the last line prints whichever `answer` value was produced.

## Hands-On Lab (~30 minutes)

**Graph to draw:** `START -> decide -> tool or answer -> END`

**Setup and run (Windows Command Prompt, from the repository root):**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-06-Workflow-To-Agent\example.py
```

This example makes a live call to `ollama.chat` with the model `gpt-oss:120b-cloud`, so make sure Ollama is running locally and signed in before you run it.

**Steps:**
1. Open only `example.py` in the session folder.
2. Find each node function, then find `StateGraph` and the node registrations.
3. Follow the edges from `START` to `END` on paper or out loud.
4. Predict the printed result before you run the file.
5. Run the command above and check your prediction.

**Small change to try:** Edit the sample request near the bottom of the file. Try a password request (like the one already there) and then try a general request such as `"What are your support hours?"`. Predict the route each time before running.

**Control question:** The model chooses the action. The graph limits the choices to only `tool` or `answer` — the model can never pick a node that doesn't exist.

## Assignment

**Goal:** Make one small change to `example.py` and explain how the result changes.

**Steps:**
1. Read the sample request near the bottom of the file and predict the current output without running it.
2. Run the example from the repository root using the command above.
3. Change only one input value or one short request sentence.
4. Predict the new route or output before running again.
5. Run the same command again and compare to your prediction.
6. Write three short sentences: what you changed, what happened, and why.

**Rules:** Keep the example in one Python file. Use LangGraph directly. Do not add a test folder or helper package, and do not replace `uv` with another package manager. Use the Windows Command Prompt commands shown above. Keep `MODEL = "gpt-oss:120b-cloud"` unchanged.

## Before You Move to Day 7

- The file runs successfully from the repository root.
- You can name the input, the node(s), the route taken, and the printed output.
- You can explain who chooses the next action (the model) and who limits that choice (the graph).
- Your one-change assignment ran twice and your three-sentence explanation matches what you actually observed.
