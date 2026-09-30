# Day 13 — Harness and Loop Engineering

## What You'll Learn Today

- Tell apart two things this session's title bundles together: the **loop** (act, verify, retry) and the **harness** (the explicit limit that ends the loop even when verification never passes).
- Trace an act-verify-retry loop from start to a clear stop.
- Understand why keeping "do the work" and "check the work" as two separate nodes makes the check trustworthy.
- Understand why a loop's stop condition must be an explicit rule in the graph, not a lucky side effect of the numbers involved.
- Read a run's printed output and say, for that run, whether the loop stopped because it passed or because the harness gave up.
- Make a small change to `example.py`, predict the effect, and explain what happened.

## Why This Matters

A "harness" is the name for everything around the model (or, here, around a repeated action) that keeps it from running wild: deciding what's allowed, performing the action, checking whether it actually worked, and knowing when to stop — including stopping when it *hasn't* worked. A "loop" is the specific cycle of act, verify, retry that runs inside that harness. They are not the same thing, and today's file is built so you can point at each one separately: `act` and `verify` are the loop, `enforce_limit`'s attempt cap is the harness.

## Key Concepts

**The loop: act, verify, retry.** `act` performs one step and increases an attempt counter. `verify` tests that step's result against a fixed, numeric rule and records a `passed` flag. Keeping "do the work" and "check the work" as two separate nodes — rather than one node that does both — is what makes the check trustworthy: the node that verifies has no way to quietly skip the test. On its own, this cycle only knows how to repeat; it has no opinion about when to stop trying.

**The harness: an explicit attempt limit.** `enforce_limit` is the piece that isn't part of the loop's own logic — it's imposed from outside it. It reads `verify`'s `passed` flag, but it also reads `MAX_ATTEMPTS`, a hard cap the loop cannot override. If verification passes, the harness ends the run with `"done"`. If verification keeps failing but the attempt count has reached `MAX_ATTEMPTS`, the harness ends the run anyway with `"give_up"` — before this rule existed, a check that never passed would simply retry forever. That is the harness's whole job in this file: guarantee the run ends, whether or not the loop ever succeeds.

**Why this used to be invisible.** In an earlier version of this file, there was no `MAX_ATTEMPTS` at all — the loop just happened to stop because `attempt * 5` was guaranteed to reach 10 within two tries. That's a loop that *looks* bounded but isn't actually protected by anything; change the passing rule slightly and it can run forever. A real harness doesn't rely on the numbers working out. It states the limit explicitly, as its own rule, independent of whatever the loop is doing.

**Two ways out of the loop, decided by two different pieces of logic.** `enforce_limit` reads `passed` (the loop's own verdict) and `attempt` (the harness's own limit) and returns exactly one of `"try_again"` (back to `act`), `"done"` (verification passed), or `"give_up"` (the harness's limit was reached first). The printed output at the end names which one happened, so you never have to guess.

## Code Walkthrough — `Day-13-Harness-Loop-Engineering/example.py`

```python
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
```

1. `act(state)` — **the loop's "do the work" step.** Increases `attempt` by one and produces a `result` equal to `attempt * 5`, a simple stand-in for "performing one step."
2. `verify(state)` — **the loop's "check the work" step.** Checks whether `result` is at least `PASS_THRESHOLD` (10) and records the answer as `passed`. This node only judges the current attempt; it has no say in whether there will be another one. It also passes `attempt` and `result` straight through — the function that routes right after a node only sees that node's own return value, not the whole accumulated state, so anything the harness needs to see (like `attempt`) has to be re-emitted here.
3. `enforce_limit(state)` — **the harness.** This is a routing function, not a node, but it is where the harness lives: it is the only place that knows about `MAX_ATTEMPTS`. It returns `"done"` if `passed` is true, `"give_up"` if `passed` is false *and* the attempt cap has been reached, or `"try_again"` otherwise.
4. The graph wires `START -> act -> verify`, and a conditional edge out of `verify` sends execution to `act` (`try_again`), or to `END` (`done` or `give_up`) — this is what makes it a loop instead of a straight line, and what makes the loop stoppable no matter what.
5. `graph.invoke({"attempt": 0})` starts at zero attempts. `1 * 5 = 5` fails the `>= 10` check and the attempt count (1) hasn't reached `MAX_ATTEMPTS` (3), so the harness allows a retry. `2 * 5 = 10` passes, so the harness ends the run with `"done"`.
6. The script prints the attempt count, the final result, and — the line that names which piece of logic actually ended the run — whether it stopped because verification passed or because the harness's attempt limit was reached.

## Two More Examples (Instructor Demo)

**Two more examples**, each a self-contained, already-run Jupyter notebook in this folder, build on `example.py` one concept at a time — these are instructor-run demos, not part of the graded assignment. Every notebook has a markdown cell above each code cell explaining what that block does, so it can be read start to finish without running it. Neither notebook adds a model call — this stays a fully local, deterministic session.

- `01_loop_engineering.ipynb` — the same act/verify shape as `example.py`, but the router checks **three** independent stop signals instead of one: verification passed, a cost budget reached, or an iteration cap reached. The same graph is run three times so each stop reason happens on its own run.
- `02_harness_engineering.ipynb` — a fixed allowlist (`ALLOWED_ACTIONS`) as the system of record, a `check_permission` guardrail that blocks anything not on it, and an observability `trace` threaded through state so a run can be reconstructed after the fact.

## Hands-On Lab (~30 minutes)

**Goal:** watch the loop and the harness each do their own job, then force the harness to be the one that ends the run.

**Graph to draw:** `START -> act -> verify -> act or END`

Open only `example.py` in `Day-13-Harness-Loop-Engineering\`, then run it from the repository root:

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-13-Harness-Loop-Engineering\example.py
```

**Code walkthrough steps:** read the short description at the top, find each node function, find `enforce_limit` and say out loud which two things it reads (`passed`, `attempt`) and which constant it compares against (`MAX_ATTEMPTS`). Follow the edges from `START` to `END`. Predict the printed result before you run the file.

**Small change to try:** change `PASS_THRESHOLD` from `10` to `1000` — a target the loop can never reach. Run the file again. Instead of looping forever, it stops after exactly `MAX_ATTEMPTS` (3) attempts, and the last printed line now says the harness's limit was hit. This is the harness doing its job: protecting the run from a check that never passes.

**Control question:** the loop (`act`/`verify`) decides whether *this* attempt succeeded; the harness (`enforce_limit`'s attempt cap) decides whether there gets to *be* another attempt at all. Neither one can override the other.

## Assignment

**Goal:** make one small change to `example.py` and explain how the result changes.

**Steps:**
1. Read the sample input near the bottom of `example.py`.
2. Predict the current output without running the file.
3. Run it: `uv run python Day-13-Harness-Loop-Engineering\example.py` (from the repository root).
4. Change only one value — `PASS_THRESHOLD` or `MAX_ATTEMPTS`.
5. Predict the new route or output, including which line the file prints for "Stopped because:".
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:** keep the example in one Python file. Use LangGraph directly. Don't add a test folder or helper package. Don't replace `uv` commands with another package manager. Use the Windows Command Prompt commands shown above. Don't add an Ollama call — this session's example is intentionally deterministic.

## Before You Move to Day 14

- [ ] The file runs without errors.
- [ ] You can name the state, the nodes, and the edges in this graph.
- [ ] You can point to the loop (`act`, `verify`) and the harness (`enforce_limit`'s attempt cap) as two separate things in the same file.
- [ ] You can explain what stops the loop when verification never passes, and why that has to be an explicit rule rather than a coincidence of the numbers.
- [ ] You made one small change, predicted the effect first, then ran it and confirmed (or corrected) your prediction.
- [ ] You can write, in plain words, what you changed, what happened, and why.
