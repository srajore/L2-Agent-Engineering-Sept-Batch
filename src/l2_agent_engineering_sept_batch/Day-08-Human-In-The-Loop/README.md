# Day 8 — Human in the Loop

## What You'll Learn Today

- Explain why not every action an agent proposes should run automatically — some actions carry more risk than others.
- Use `interrupt` to pause a graph before a sensitive action and wait for a human decision.
- Resume a paused thread with `Command(resume=...)`, using the same thread ID.
- Trace both outcomes: an approved action completing, and a rejected action being safely denied.
- Run `example.py` once approving and once rejecting the action, and explain who controls the decision.

## Why This Matters

So far, every graph you've built has run start to finish without stopping to ask permission. But automation preparing an action and a human deciding whether it may continue are two very different things — guidance has low impact, an account change has high impact, and some actions should never be automated at all. Session 8 gives you the tool for that pause: `interrupt`. It saves the current state, hands back a review payload describing what's being proposed, and stops execution until someone responds. Because the thread has to still exist when that decision arrives — maybe seconds later, maybe much longer — this session also depends directly on the checkpointer and thread ID you learned in Session 7. Today's action is simulated, but the pattern (never act, then ask — always ask, then act) is exactly what a real approval gate needs.

## Key Concepts

**The Graph Shape.** This example's graph is `START -> approval -> finish -> END`. The `approval` node always calls `interrupt(...)` — every invocation pauses for a human decision, with no risk-classification step and no conditional edge that could skip the gate. Once the human answers, `finish` reads that answer and branches with a plain `if/else`: act (report completion) if approved, deny (report cancellation) if not. Placing the pause *before* the branch is what makes the gate meaningful — by the time `finish` runs, the decision has already been made by a person, not the graph.

**What `interrupt` Actually Does.** `interrupt` saves state, returns a review payload, and pauses execution — it does not create a review screen or any UI for you. The payload it returns should include the proposed action and a clear question, using values that could safely be turned into JSON — enough context for a person to decide, without exposing anything unnecessary.

**The Paused Result and Resuming.** When a graph hits an `interrupt`, the caller doesn't get a normal final result — instead, `__interrupt__` in the returned object contains the review request. A pause like this is an expected, ordinary state, not an error. To continue, you call the graph again with `Command(resume=value)` and the *same* thread ID, supplying the human's decision so it flows back into the paused node.

**Approval and Rejection.** An approved decision reaches the simulated action and reports completion; a rejected decision returns a clear message and performs no action at all — rejection is not treated as an exception, it's just another valid outcome. (Not built in this file: a real system might let ordinary low-risk requests bypass the approval gate entirely, since over-approving everything can make a system unusable. Deciding what counts as "high impact" enough to need a human is normally handled by stable, deterministic rules in application code — not by asking the model to judge risk itself. Here, every request pauses for approval, regardless of what the action is.)

**Maker and Checker, and Replay Safety.** A well-designed approval flow separates the actor proposing the action from the actor approving it — production systems must authenticate both roles independently. It's also worth knowing that resuming a graph re-runs the node from its start, so any code that ran *before* the interrupt needs to be safe to repeat. That's why idempotent design (repeating an action with the same request ID shouldn't repeat its real-world effect) becomes essential once real external systems are involved.

## Code Walkthrough — `Day-08-Human-In-The-Loop/example.py`

```python
"""Session 8: pause a graph and ask a human for approval."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


def ask_for_approval(state):
    approved = interrupt("Approve this action? (yes/no)")
    return {"approved": approved}


def finish(state):
    message = "Action completed." if state["approved"] else "Action cancelled."
    return {"message": message}


graph_builder = StateGraph(dict)
graph_builder.add_node("approval", ask_for_approval)
graph_builder.add_node("finish", finish)
graph_builder.add_edge(START, "approval")
graph_builder.add_edge("approval", "finish")
graph_builder.add_edge("finish", END)
graph = graph_builder.compile(checkpointer=InMemorySaver())

settings = {"configurable": {"thread_id": "approval-1"}}
graph.invoke({"action": "Reset the account"}, config=settings)
answer = input("Approve the account reset? (yes/no): ")
result = graph.invoke(Command(resume=answer.lower() == "yes"), config=settings)
print(result["message"])
```

1. `ask_for_approval` calls `interrupt(...)` with a plain question string — this pauses the graph right there and hands the question back to the caller.
2. The graph is compiled with `checkpointer=InMemorySaver()`, which is required so the paused thread can be resumed later — without a checkpointer, `interrupt` would have nothing to resume from.
3. The first `graph.invoke` call starts the graph and immediately hits the interrupt, pausing before any decision has been made.
4. `input(...)` collects a real yes/no answer from the person running the program in Command Prompt.
5. The second `graph.invoke` call passes `Command(resume=answer.lower() == "yes")` — a `True` or `False` value — using the *same* `thread_id`, so it resumes the paused `ask_for_approval` node with that value as `approved`.
6. `finish` reads `state["approved"]` and returns either `"Action completed."` or `"Action cancelled."`, which the last line prints.

## Hands-On Lab (~30 minutes)

**Graph to draw:** `START -> approval -> finish -> END`

**Setup and run (Windows Command Prompt, from the repository root):**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-08-Human-In-The-Loop\example.py
```

This example is fully deterministic and does not call Ollama or any live model — the only external input is the yes/no you type at the prompt.

**Steps:**
1. Open only `example.py` in the session folder.
2. Find each node function, then find `StateGraph` and the node registrations.
3. Follow the edges from `START` to `END`, noting where the interrupt pauses things.
4. Predict the printed result before running the file.

**Small change to try:** Run the file twice — once typing `yes` at the prompt, and once typing `no`. Confirm the printed message matches your approval each time.

**Control question:** A person controls the approval decision — the graph and its rules only decide *when* to pause and ask, never what the answer should be.

## Assignment

**Goal:** Make one small change to `example.py` and explain how the result changes.

**Steps:**
1. Read the sample input near the bottom of the file and predict the current output without running it.
2. Run the example from the repository root using the command above.
3. Change only one input value or one short input sentence.
4. Predict the new output before running again.
5. Run the same command again and compare to your prediction.
6. Write three short sentences: what you changed, what happened, and why.

**Rules:** Keep the example in one Python file. Use LangGraph directly. Do not add a test folder or helper package, and do not replace `uv` with another package manager. Use the Windows Command Prompt commands shown above. Do not add an Ollama call — this session's example is intentionally deterministic.

## Before You Move to Day 9

- The file runs successfully from the repository root, for both a `yes` and a `no` answer.
- You can name the state, the nodes, and the edges.
- You can explain who controls the next step (a human, through the approval decision) and why the pause happens before the action, not after.
- Your one-change assignment ran twice and your three-sentence explanation matches what you actually observed.
