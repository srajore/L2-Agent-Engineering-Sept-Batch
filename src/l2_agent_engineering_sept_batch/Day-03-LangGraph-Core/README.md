# Day 3 — LangGraph Core

## What You'll Learn Today

- Why agent development needs a framework at all, instead of hand-written `if`/`else` code.
- Where LangGraph sits among other agent frameworks, and why this course teaches LangGraph specifically.
- The core building blocks: state, nodes, edges, `START`, `END`, compilation, and invocation.
- How to read a `TypedDict`-style state schema and understand partial state updates.
- How to trace state as it flows through several fixed nodes in a row.
- How to run a multi-node LangGraph file and predict its output before running it.

## Why This Matters

By Session 2, a single function was already doing too much — cleaning input, checking for gaps, generating content, and deciding on a status all at once. That is exactly the moment orchestration becomes necessary: something has to coordinate the steps, the shared data between them, how execution moves from one to the next, and how things end. You could write this by hand with nested `if`/`else` and retry logic, but that stops being readable after just a few steps. A framework gives you standard building blocks instead — state, steps, and transitions — so today introduces the smallest possible LangGraph graph and builds it up into the four-node application you'll trace by hand.

## Key Concepts

**Why a framework, and why LangGraph.** One model call is not an agent. A real request needs shared state across steps, a decision about what happens next, tool calls with real results, error and retry paths, and sometimes a pause for human approval — hand-rolled control flow for all of that becomes unreadable fast. Several frameworks solve this same orchestration problem in different styles: LangChain (a general-purpose toolkit whose abstractions this course intentionally avoids), CrewAI (role-playing multi-agent "crews"), AutoGen/AG2 (agents that message each other), the OpenAI Agents SDK (a lightweight loop tied to OpenAI's tool-calling format), LlamaIndex agents (data/RAG-first), and Semantic Kernel (plugin-based, common in enterprise Microsoft stacks). This course teaches LangGraph only, and does not teach LangChain classes, because LangGraph keeps state explicit and printable at every step, uses the same graph shape for a plain workflow and a model-driven agent, and natively supports the branches, loops, interrupts, and checkpoints you'll need in later sessions.

**State, nodes, and edges.** State is the shared data structure that moves through the graph — in Session 3's example it holds fields like the raw text, normalized text, and a word count. A `TypedDict`-style schema is just a dictionary shape that tells you (and your tools) which keys and value types to expect; it improves clarity but doesn't validate every value at runtime. Nodes are plain functions that read from state and return a partial update — a node only needs to return the fields it actually changed, and LangGraph merges that update into the accumulated state. Edges connect nodes together: a normal edge always sends execution from one named node to the next, with no branching based on state (that comes in Session 4).

**START, END, and one responsibility per node.** `START` and `END` are virtual markers — `START` connects your input to the first real node, and `END` marks a terminal point; neither one does any business work itself. A well-designed node has a clear, named purpose, clear inputs, a clear update it returns, and a way to test it independently — avoid both giant nodes that do everything and meaningless one-line fragments that do nothing useful on their own.

**Building, compiling, and running the graph.** Building a graph is four steps: create a `StateGraph`, add each node, add the edges between them, then compile. Compilation checks that the graph's structure is valid and turns your draft into a runnable object — it does not prove your business logic is correct, only that the graph itself is well-formed. Calling `.invoke()` on the compiled graph sends your starting state into the first node; as each node's update is applied, the state accumulates, and whatever remains at `END` is what `.invoke()` returns. This is still a fixed workflow — even once a session later adds a real LLM call into a node, the developer is still the one who defines every possible transition; only in Session 4 does state itself start selecting the route, and only in Session 6 does a model get to choose an action.

## Code Walkthrough — `Day-03-LangGraph-Core/example.py`

```python
"""Session 3: learn state, nodes, edges, START, and END."""

from langgraph.graph import END, START, StateGraph


def clean_text(state):
    return {"text": state["text"].strip()}


def count_words(state):
    return {"word_count": len(state["text"].split())}


def create_message(state):
    message = f"Your requirement has {state['word_count']} words."
    return {"message": message}


graph_builder = StateGraph(dict)
graph_builder.add_node("clean", clean_text)
graph_builder.add_node("count", count_words)
graph_builder.add_node("message", create_message)
graph_builder.add_edge(START, "clean")
graph_builder.add_edge("clean", "count")
graph_builder.add_edge("count", "message")
graph_builder.add_edge("message", END)
graph = graph_builder.compile()

result = graph.invoke({"text": "  User can reset a password  "})
print(result["message"])
```

1. `clean_text` is the first node. It reads `state["text"]`, strips leading and trailing whitespace, and returns the cleaned text as an update.
2. `count_words` is the second node. It reads the (already cleaned) text, splits it into words, and returns the count as `word_count`.
3. `create_message` is the third node. It reads `word_count` from state and builds a friendly sentence, returned as `message`.
4. `StateGraph(dict)` creates the graph builder, the three `add_node` calls register the functions above under the names `clean`, `count`, and `message`, and the four `add_edge` calls wire the fixed path: `START -> clean -> count -> message -> END`.
5. `graph.invoke(...)` runs the whole path on one sample requirement text, and the final message is printed.

## Hands-On Lab (~30 minutes)

**Graph to draw:** `START -> clean -> count -> message -> END`

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-03-LangGraph-Core\example.py
```

**Walkthrough steps:**

1. Read the short description at the top of the file.
2. Find each node function (`clean_text`, `count_words`, `create_message`).
3. Find `StateGraph` and the node registrations.
4. Follow the edges from `START` to `END`.
5. Predict the printed result before you run the file.

**Small change to try:** Change the sample requirement text and predict the new word count before running the file again.

**Control question:** Who controls every transition in this graph? The developer does — the path is fixed no matter what the input text says.

## Assignment

**Goal:** Make one small change to `example.py` and explain how the result changes.

**Steps:**

1. Read the sample input near the bottom of `example.py`.
2. Predict the current output without running the file.
3. Run the example from the repository root:
   ```cmd
   uv run python Day-03-LangGraph-Core\example.py
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

## Before You Move to Day 4

- The file runs successfully on your machine.
- You can name the state, all three nodes, and the edges connecting them.
- You can explain who controls the next step (the developer, using fixed edges).
- You made one small change to the input text, predicted the new word count first, then confirmed it by running the file again.
- Your three-sentence explanation matches what you actually observed.
