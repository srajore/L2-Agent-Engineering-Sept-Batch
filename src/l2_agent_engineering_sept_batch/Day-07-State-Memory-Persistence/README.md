# Day 7 — State, Memory, and Persistence

## What You'll Learn Today

- Explain the difference between state, memory, and persistence using three simple questions: what data, which thread, where stored.
- Configure a checkpointer (`InMemorySaver`) so a graph can save its state between calls.
- Use a `thread_id` to keep two conversations isolated from each other.
- Continue state across two calls in the same thread by reusing the same thread ID.
- Run `example.py`, predict its output, then change the saved name while keeping the thread ID unchanged.

## Why This Matters

Without any extra setup, a graph forgets everything the moment it finishes running — the next call starts from nothing, because a model call only ever sees the input your application sends it. That's a real limitation: you can't have a conversation that "remembers" earlier turns unless something saves and reloads state on your behalf. Session 7 introduces that missing piece. One conversation thread can continue exactly where it left off, while a completely different thread stays isolated, because memory belongs to an application thread, not magically to the model itself. Getting comfortable with this idea — save, load, isolate — is what makes multi-turn agents possible later in the course.

## Key Concepts

**State.** State is the typed, explicit set of values that nodes read and write while a graph runs — think of it as a case folder holding messages and flags. It is application data you define, not something hidden inside the model.

**Short-Term Memory vs. Persistence.** Short-term memory means saved state gets loaded again for a later turn in the same thread — it does not retrain the model, it just reopens the same case folder. Persistence is a related but separate idea: it describes *where* and *how long* those checkpoints survive. In-memory storage (what this example uses) only lasts for the current running process; a real production system would need durable storage that survives a restart.

**The Checkpointer and thread_id.** `InMemorySaver` is what actually stores checkpoints while the process runs — it's excellent for learning and tests, but not for durable production use. The `thread_id` passed in the invocation config is the stable key that identifies one conversation; two different thread IDs (like `ticket-a` and `ticket-b`) are routed to two completely separate saved folders. Never reuse one shared thread ID across different users, or their state will mix together.

**Tracing Continuity and Isolation.** When you call the graph twice with the *same* thread ID, the second call loads the first call's saved values before adding anything new — that's continuity. When you use a *different* thread ID, the new call starts with no earlier state at all — that's isolation. (This example doesn't call it, but LangGraph also lets you inspect any thread's latest saved values directly with `get_state(config)` — a handy tool for your own debugging and audit work once you start exploring beyond this file.)

**Recovery and Side Effects (a preview).** If a graph is resumed later, code that ran before the pause can end up running again. Today's example has no real side effects to worry about, but this becomes an important design concern once actions have real-world consequences — a preview of the idempotent-action idea that Session 8 builds on.

## Code Walkthrough — `Day-07-State-Memory-Persistence/example.py`

```python
"""Session 7: remember values between calls with a thread ID."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from typing import TypedDict


# This small state definition lets LangGraph save each value separately.
class MemoryState(TypedDict, total=False):
    name: str
    saved_name: str
    question: str


def remember_name(state):
    if state.get("name"):
        return {"saved_name": state["name"]}
    return {}


graph_builder = StateGraph(MemoryState)
graph_builder.add_node("remember", remember_name)
graph_builder.add_edge(START, "remember")
graph_builder.add_edge("remember", END)
graph = graph_builder.compile(checkpointer=InMemorySaver())

# The same thread ID continues the same conversation.
settings = {"configurable": {"thread_id": "student-1"}}
graph.invoke({"name": "Asha"}, config=settings)
result = graph.invoke({"question": "What is my name?"}, config=settings)

print("Remembered name:", result["saved_name"])
```

1. `MemoryState` is a `TypedDict` describing the fields the graph can hold: `name`, `saved_name`, and `question`. Marking it `total=False` means not every field has to be present on every call.
2. `remember_name` is the only node. If the incoming state has a `name`, it saves it as `saved_name`; otherwise it changes nothing.
3. The graph is compiled with `checkpointer=InMemorySaver()`, which is what makes saving and loading state possible at all — without it, each `invoke` call would start completely fresh.
4. `settings` fixes one `thread_id` (`"student-1"`) that both calls below will share.
5. The first `graph.invoke` call passes `{"name": "Asha"}`, so `remember_name` saves `saved_name = "Asha"` into that thread's checkpoint.
6. The second `graph.invoke` call passes only `{"question": "What is my name?"}` — no `name` this time — but because it uses the *same* `thread_id`, the graph reloads the earlier checkpoint and `result["saved_name"]` still contains `"Asha"`.

## Hands-On Lab (~30 minutes)

**Graph to draw:** `START -> remember -> END`, called twice with the same thread ID.

**Setup and run (Windows Command Prompt, from the repository root):**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-07-State-Memory-Persistence\example.py
```

This example is fully deterministic — it does not call Ollama or any live model, so it will run the same way every time.

**Steps:**
1. Open only `example.py` in the session folder.
2. Find the node function, then find `StateGraph` and the node registration.
3. Follow the edges from `START` to `END`, noting that the graph is invoked twice.
4. Predict the printed result before running the file.

**Small change to try:** Change the saved name (for example, from `"Asha"` to your own name) but keep the `thread_id` (`"student-1"`) unchanged. Run the file again and confirm the new name is what gets remembered.

**Control question:** The graph saves state for the selected thread. Changing the thread ID (rather than the name) is what would break continuity — try that too if you want to see isolation in action.

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

## Before You Move to Day 8

- The file runs successfully from the repository root.
- You can name the state fields, the node, and the edges.
- You can explain, in your own words, the difference between state, short-term memory, and persistence.
- You can say why two different thread IDs would keep two users' data separate.
- Your one-change assignment ran twice and your three-sentence explanation matches what you actually observed.
