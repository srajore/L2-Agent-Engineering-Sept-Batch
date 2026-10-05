# Day 14 — Token Taxonomy and Economics

## What You'll Learn Today

- Explain where an agent's token usage actually comes from, not just the user's message.
- Classify token sources: instructions, conversation, retrieved evidence, tool schemas and results, and output.
- Estimate a simple word or character budget for each part of a request before it's sent.
- Explain why repeated loop calls can amplify token usage.
- Connect measured token usage to cost and to context-window limits.
- Make a small change to `example.py`, predict the effect, and explain what happened.

## Why This Matters

When people think about "how many tokens a call uses," they usually only picture the user's question — but a real agent run also carries system instructions, retained history, retrieved passages, tool schemas and tool results, and finally the generated output. If you only measure the visible user message, you'll miss most of what's actually driving cost and latency, especially once a loop repeats the same instructions and context on every iteration. Today's goal is to practice measuring each part separately, so you know exactly where growth is coming from before you try to fix it.

## Key Concepts

**Tokens versus characters and words.** A tokenizer splits text into vocabulary pieces before the model processes it, and those pieces don't line up neatly with words — token boundaries are irregular. As a rough, order-of-magnitude estimate for English text, dividing character count by four is a reasonable heuristic, but this number is not accurate enough for billing or for strictly enforcing a context limit — it's a warm-up estimate, nothing more.

**Where tokens come from.** *System* tokens are the role, policy, constraints, and output-format instructions — and because these repeat on every call, they can end up costing more than a short user question ever does. *Conversation* tokens are the current question plus any retained history messages (this is exactly what the selection rules from Day 12 control). *RAG* tokens come from every retrieved passage and its source label — both how many passages you retrieve and how large each chunk is will matter. *Tool* tokens come from tool descriptions, argument schemas, and returned results, which can also repeat across calls — a short question can still carry a surprisingly large tool menu. *Output* tokens are the generated answer, plus any reasoning usage the provider reports separately.

**Reading usage metadata.** When a model response includes something like `usage_metadata`, it can report input tokens, output tokens, and a total — use these reported numbers when they're available, and remember that a missing field means "unavailable," not "zero."

**From measurement to a budget.** Once you measure each component of a saved trace, you can sum them for a single call, and see how repeated instructions and context can roughly double your estimate across two calls. All of this needs to fit inside the model's context window — input and output share one bounded capacity — though the maximum size a model supports is not by itself a good target to aim for. Multiplying measured input and output tokens by their approved rate per million connects usage to actual cost (this repository doesn't store a specific current provider price). And a wider budget also has to weigh latency and quality together: more calls or longer context can slow a response down, while cutting context too aggressively can remove evidence the model actually needed — so the goal is a run budget with a maximum number of calls, input tokens, output tokens, a latency target, and an estimated cost, all judged against your acceptance criteria rather than an arbitrary limit.

## Code Walkthrough — `Day-14-Token-Taxonomy-Economics/example.py`

```python
"""Session 14: estimate the size of each part of a model request."""

from langgraph.graph import END, START, StateGraph


def count_words(text):
    return len(text.split())


def measure(state):
    counts = {
        "instruction": count_words(state["instruction"]),
        "question": count_words(state["question"]),
        "context": count_words(state["context"]),
    }
    return {"counts": counts, "total": sum(counts.values())}


graph_builder = StateGraph(dict)
graph_builder.add_node("measure", measure)
graph_builder.add_edge(START, "measure")
graph_builder.add_edge("measure", END)
graph = graph_builder.compile()

result = graph.invoke(
    {
        "instruction": "Answer using the context.",
        "question": "How do I reset my password?",
        "context": "Open the reset page.",
    }
)
print("Word estimate by part:", result["counts"])
print("Total word estimate:", result["total"])
```

1. `count_words(text)` is a tiny helper that splits text on whitespace and counts the pieces — a simple, deterministic stand-in for a token estimate.
2. `measure(state)` calls that helper on three separate parts of the input — `instruction`, `question`, and `context` — and stores each count in a `counts` dictionary, keeping them separate so you can see which part is biggest.
3. `measure` also sums all three counts into a single `total`, so you get both the breakdown and the overall estimate.
4. The graph is the simplest shape possible: `START -> measure -> END` — one node does all the work, no branching or looping.
5. `graph.invoke(...)` runs it with a sample instruction, question, and context, and the script prints the per-part word counts followed by the total.

## Hands-On Lab (~30 minutes)

**Goal:** measure instruction, question, and context separately.

**Graph to draw:** `START -> measure -> END`

Open only `example.py` in `Day-14-Token-Taxonomy-Economics\`, then run it from the repository root:

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-14-Token-Taxonomy-Economics\example.py
```

**Code walkthrough steps:** read the short description at the top, find each node function, find `StateGraph` and the node registrations, then follow the edges from `START` to `END`. Predict the printed result before you run the file.

**Small change to try:** make the `context` value longer and compare the new total to the old one.

**Control question:** the measurement is deterministic — running it twice with the same input always gives the same counts.

## Assignment

**Goal:** make one small change to `example.py` and explain how the result changes.

**Steps:**
1. Read the sample input near the bottom of `example.py`.
2. Predict the current output without running the file.
3. Run it: `uv run python Day-14-Token-Taxonomy-Economics\example.py` (from the repository root).
4. Change only one input value or one short input sentence.
5. Predict the new route or output.
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:** keep the example in one Python file. Use LangGraph directly. Don't add a test folder or helper package. Don't replace `uv` commands with another package manager. Use the Windows Command Prompt commands shown above. Don't add an Ollama call — this session's example is intentionally deterministic.

## Before You Move to Day 15

- [ ] The file runs without errors.
- [ ] You can name the state, the nodes, and the edges in this graph.
- [ ] You can explain who (or what) controls the next step, and where each word count comes from.
- [ ] You made one small change, predicted the effect first, then ran it and confirmed (or corrected) your prediction.
- [ ] You can write, in plain words, what you changed, what happened, and why.
