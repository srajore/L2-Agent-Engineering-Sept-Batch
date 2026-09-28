# Day 12 — Context Engineering

## What You'll Learn Today

- Explain how an application chooses what a model actually sees for one call.
- Classify context into task, state, memory, RAG, and tool categories.
- Build a small, clearly labelled context block before sending it to a model.
- Understand why a hard character or token limit keeps context from growing without bound, even though today's file is small enough not to need one.
- Run a graph that builds context in one node and calls the model in the next.
- Make a small change to `example.py`, predict the effect, and explain what happened.

## Why This Matters

A model's answer is only as good as what it's actually given to read — missing facts cause it to guess, and too much irrelevant text can bury the facts that matter. This is true no matter how capable the model is; a bigger model does not remove the need to design its input carefully. Today you'll practice deciding, on purpose, what goes into a model call: the current question, any useful state, relevant history, retrieved evidence, and tool results — each one labelled so you can see exactly what the model received and why.

## Key Concepts

**The five context types.** *Task* context is the current user question — it anchors the whole call. *State* context is execution facts your application already knows (route, status, counters, results) — not every internal field belongs in the prompt, only the ones the model actually needs. *Memory* context is relevant earlier messages that help resolve follow-up wording; the application has to resend this history itself, since the model does not remember previous turns on its own. *RAG* context is retrieved, source-labelled passages (like `KB-102`) that supply grounded facts — both relevance and whether the source is authorized to be shown matter here. *Tool* context is the result of an action the system took — current operational facts, with any secrets or irrelevant raw fields stripped out first.

**Provenance labels and priority.** Labelling each section — `TASK`, `TOOL`, `RAG`, `MEMORY` — lets you inspect exactly what went into a call and supports later citation checks. When you assemble multiple sections, task comes first, and current tool output takes priority over related RAG or memory content — the ordering should match what the next decision actually needs.

**Selecting what's relevant.** In a system with more sources to draw on than today's file has, you wouldn't include everything you have — a simple, transparent rule decides what qualifies: RAG text only when its words meaningfully overlap the question, memory only when the current message shows signs of depending on an earlier one (words like "it" or "again"). Rules like these are simple on purpose — they're explainable and testable — even though they have real limits, such as missing a synonym that means the same thing but uses different words.

**The character budget.** As the number of context sources grows, a hard limit on size — a character or token budget — keeps the assembled context bounded and predictable before it's ever sent to the model. Today's file only ever combines one user question and one fact, so it stays well within any reasonable budget without needing one. But cutting text to fit a budget carries risk in general — a truncation can remove a qualifier or a source detail right when you need it most, so any real compression needs a check that it hasn't broken the meaning of what's left.

## Code Walkthrough — `Day-12-Context-Engineering/example.py`

```python
"""Session 12: build a small, clearly labelled model context."""

import sys
from typing import TypedDict

import ollama
from langgraph.graph import END, START, StateGraph

sys.stdout.reconfigure(encoding="utf-8")  # the model may answer with punctuation Command Prompt cannot print


MODEL = "gpt-oss:120b-cloud"


class State(TypedDict):
    user: str
    fact: str
    context: str
    answer: str


def build_context(state: State):
    context = f"USER: {state['user']}\nFACT: {state['fact']}"
    return {"context": context}


def ask_model(state: State):
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": state["context"]}],
    )
    return {
        "context": state["context"],
        "answer": response["message"]["content"],
    }


graph_builder = StateGraph(State)
graph_builder.add_node("build_context", build_context)
graph_builder.add_node("ask_model", ask_model)
graph_builder.add_edge(START, "build_context")
graph_builder.add_edge("build_context", "ask_model")
graph_builder.add_edge("ask_model", END)
graph = graph_builder.compile()

result = graph.invoke({"user": "How do I reset my password?", "fact": "Use /reset."})
print("Context sent to the model:\n", result["context"])
print("\nAnswer:\n", result["answer"])
```

1. The `sys.stdout.reconfigure(encoding="utf-8")` line near the top is a Windows-console safety fix — it makes sure punctuation the model might return can actually be printed in Command Prompt without crashing.
2. `MODEL` is fixed to `"gpt-oss:120b-cloud"` — this stays the same across the whole course; don't change it.
3. `State` is a `TypedDict` naming every field the graph can hold: `user`, `fact`, `context`, `answer`. Passing it to `StateGraph(State)` (instead of a plain `dict`) tells LangGraph to merge each node's returned keys into state one field at a time, instead of replacing the whole state with whatever a node returns.
4. `build_context(state)` combines the user's question and one supplied fact into a small labelled string (`USER: ...` and `FACT: ...`) and stores it as `context`.
5. `ask_model(state)` sends that exact `context` string as the message to `ollama.chat`, and returns both the original `context` (so it can still be printed later) and the model's `answer`.
6. The graph wires `START -> build_context -> ask_model -> END` — context is always built before the model is ever called.
7. `graph.invoke(...)` runs it with a sample password-reset question and fact, then the script prints the exact context that was sent and the model's answer, so you can see precisely what the model saw.

**Four more examples**, each a self-contained, already-run Jupyter notebook in this folder, build on `example.py` one technique at a time — these are instructor-run demos, not part of the graded assignment. Every notebook has a markdown cell above each code cell explaining what that block does, so it can be read start to finish without running it.

Unlike `example.py`, these four notebooks are a deliberate exception to this course's "agent boundary only at Day 6" framing (see `CLAUDE.md`): in each one, the **model's own output** decides which node runs next, routed with `add_conditional_edges` exactly like Day 6 — not a hand-written keyword rule. Every model decision is validated against a fixed allowlist and corrected to a safe default if the reply doesn't match:

- `02_context_selection.ipynb` — the model reads every candidate RAG passage and picks the one relevant label (or `NONE`); that choice routes to `include_rag` or `skip_rag`.
- `03_context_compression.ipynb` — when the assembled sections are over budget, the model picks **which one** to cut (`RAG` or `MEMORY`; `TASK` is never offered). An invalid reply falls back to `MEMORY` — the same section the old fixed-priority rule would have dropped first, now the safe default instead of the only option.
- `04_context_offloading.ipynb` — **context offloading**: a large result is written to `OFFLOAD_STORE` (a stand-in for a file, vector store, or database) instead of the context. The model decides `FULL` or `SUMMARY` for how much detail the request actually needs (default `SUMMARY`, so it never over-shares by mistake); only on `FULL` is the full text read back and sent.
- `05_context_isolation.ipynb` — **context isolation**: the model triages the ticket first (`NETWORK`, `ACCOUNT`, or `BOTH`, default `BOTH`) and LangGraph only runs the specialist branch(es) chosen — each specialist still gets its own separate, labelled context and its own model call, so neither sees the other's information. Only the results, never the raw contexts, are merged.

Together with `example.py`'s labelled context assembly, these four notebooks cover the four context engineering strategies used in practice — **select** what's relevant, **compress** to fit a budget, **offload** what's too large to keep in the model's context, and **isolate** so independent sub-tasks don't share context they shouldn't — each one taught as something an agent decides, not a fixed rule.

## Hands-On Lab (~30 minutes)

**Goal:** build labelled context before calling the model.

**Graph to draw:** `START -> build_context -> ask_model -> END`

This lab needs **Ollama running locally** with the `gpt-oss:120b-cloud` model available, since `ask_model` makes a real call to it. Open only `example.py` in `Day-12-Context-Engineering\`, then run it from the repository root:

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-12-Context-Engineering\example.py
```

**Code walkthrough steps:** read the short description at the top, find each node function, find `StateGraph` and the node registrations, then follow the edges from `START` to `END`. Predict the printed result before you run the file.

**Small change to try:** change the `fact` value and inspect the exact context that gets sent to the model.

**Control question:** the graph controls which context reaches the model — nothing else decides this.

## Assignment

**Goal:** make one small change to `example.py` and explain how the result changes.

**Steps:**
1. Read the sample input near the bottom of `example.py`.
2. Predict the current output without running the file.
3. Run it: `uv run python Day-12-Context-Engineering\example.py` (from the repository root).
4. Change only one input value or one short input sentence.
5. Predict the new route or output.
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:** keep the example in one Python file. Use LangGraph directly. Don't add a test folder or helper package. Don't replace `uv` commands with another package manager. Use the Windows Command Prompt commands shown above. Keep `MODEL = "gpt-oss:120b-cloud"` unchanged.

## Before You Move to Day 13

- [ ] The file runs without errors (Ollama is running locally with `gpt-oss:120b-cloud` available).
- [ ] You can name the state, the nodes, and the edges in this graph.
- [ ] You can explain who (or what) controls the next step, and what exact context was sent to the model.
- [ ] You made one small change, predicted the effect first, then ran it and confirmed (or corrected) your prediction.
- [ ] You can write, in plain words, what you changed, what happened, and why.
