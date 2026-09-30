# Day 13 — Harness & Loop Engineering: FAQ

## Setup and running

**Do I need Ollama for today's session?**
No. Day 13 is not one of the model-backed sessions (2, 6, 9, 11, 12, 15, 17). `example.py` and both supplementary notebooks are fully deterministic — no `ollama.chat` call anywhere in this folder.

**What's the exact command to run `example.py`?**
From the repository root, in Windows Command Prompt:
```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-13-Harness-Loop-Engineering\example.py
```

**How do I run the `.ipynb` notebooks?**
Open them in VS Code (with the Jupyter extension) or Jupyter itself and run cells normally — or just read them, since both were already executed and their real output is saved in place. They live in this same folder: `01_loop_engineering.ipynb`, `02_harness_engineering.ipynb`.

**Can I re-run the notebooks myself?**
Yes. Unlike Day 12's model-backed notebooks, these are fully deterministic — no live model call means re-running will always print the exact same output, every time, on any machine.

**Do I need `ollama signin` for Day 13?**
No. That's only needed for the model-backed days listed above.

## What's a loop vs. a harness, in one sentence?

A **loop** is the repeating cycle itself — do the step, check the step, decide whether to repeat (`act` → `verify` → retry). A **harness** is everything deliberately built *around* that cycle: what it's allowed to do, and the rules that guarantee it stops, whether or not it ever succeeds.

## The three code files, compared

| File | Stop signals | State style |
| --- | --- | --- |
| `example.py` | One: `enforce_limit`'s attempt cap | Plain `dict` — every node must re-emit every field it wants to keep |
| `01_loop_engineering.ipynb` | Three: verification passed, cost budget, iteration cap | `State(TypedDict)` — a node returns only the field(s) it changed |
| `02_harness_engineering.ipynb` | N/A (this one is about *permissions*, not stopping) | `State(TypedDict)` |

## Loop engineering questions

**Why does a loop need more than one stop signal?**
Because no single signal is fully trustworthy on its own. If a loop only checks "did it pass yet?", an unreachable pass condition means it never stops. `01_loop_engineering.ipynb`'s `route_after_verify` checks three independent things — verification passed, a cost budget, and an iteration cap — so at least one of them is guaranteed to end the run.

**What happens if none of the three conditions in `route_after_verify` are true?**
The router returns `"retry"`, which routes back to `act` for another attempt — that's the loop doing its normal job.

**Is `cost_per_attempt` a real cost?**
No — it's a stand-in. Day 13 doesn't call a model, so there's no real token or dollar cost to measure. `cost_per_attempt` plays the same role a real API call's cost or latency would once a loop is actually calling a model (from Day 6 onward).

**What's the difference between the loop's decision and the harness's decision, concretely?**
`verify` (the loop) only judges whether *this* attempt's `result` passed — it has no opinion about cost or attempt count. `route_after_verify` (the harness logic) reads `passed` plus two limits it didn't decide itself, `budget` and `max_attempts`. Neither piece can override the other; that split is what makes the stop trustworthy instead of accidental.

## Harness engineering questions

**What is `ALLOWED_ACTIONS`, and why is it a plain Python set instead of a LangChain tool?**
It's the harness's system of record for what the graph may do — a fixed allowlist. This course never uses LangChain tools or `ToolNode` (see `CLAUDE.md`'s code rules); `check_permission` is a plain membership test (`in ALLOWED_ACTIONS`) against plain local data.

**What does `trace` actually do?**
It's the observability record. Every node appends one line to it describing what it just decided or did, so after a run finishes you can read back exactly what happened and why — without having to guess.

**What happens if the requested action isn't in `ALLOWED_ACTIONS` at all?**
Nothing crashes. `check_permission` sets `allowed = False`, `route_after_permission` routes to `reject_action`, and the run ends normally with an explanatory `trace` entry and an `output` saying it was blocked.

**Is `check_permission` an agent decision, like Day 6?**
No. It's a fixed rule — a plain `in` check against a Python set — not a model's own output. Day 6 is where this course's "the model chooses the next node" boundary begins; Day 13's routing (here and in `example.py`) stays fully developer-controlled and deterministic, same as Days 1–5.

## Code questions

**Why does `example.py` use `StateGraph(dict)` while the two notebooks use `class State(TypedDict)`?**
With a plain, unlabeled `dict`, LangGraph has no idea what fields exist, so it treats the whole state as one blob — whatever a node returns **replaces it entirely**. That's why `example.py`'s `verify` re-emits `attempt` and `result` just to keep them; it's a deliberate, documented lesson in that file. The two notebooks instead declare a named `State(TypedDict)`, which gives each field its own channel — LangGraph then merges a node's return **key by key**, so a node only returns what it actually changed, and everything else carries forward automatically. This is the same pattern Day 12's notebooks use.

**Why don't the notebooks use a shortcut like `{**state, "field": value}` instead of listing every field?**
Two reasons. First, with the `TypedDict` schema they don't need to — unreturned fields already carry forward on their own, so there's nothing to spread. Second, even where a node returns several fields, this course spells each one out by name rather than using dict-unpacking, since `**state` is more advanced Python than this course otherwise uses and hides which fields actually change.

**Do the two notebooks count toward the graded assignment?**
No. `example.py` is the only graded file. `01_loop_engineering.ipynb` and `02_harness_engineering.ipynb` are instructor-run demos that each extend one half of today's concept — useful for the fuller picture, not required for the assignment.

## Visual materials

**What is `infographic.html`, and how do I open it?**
A single, self-contained HTML file — no server, no internet connection, and no Ollama required. Double-click it, or open it from a browser with File → Open, and it renders fully offline.

**What do the nested rings in `infographic.html` mean?**
They show how four course concepts nest inside one another, read from the outside in: a **harness** contains a **loop**; every turn of that loop assembles **context** (Day 12); every assembled context produces one **prompt**.

**What are the horizontal bar "meters" under the loop diagram?**
They plot `01_loop_engineering.ipynb`'s three actual runs — an attempts-bar and a cost-bar per run — with whichever one crossed its limit first highlighted in orange, so you can see the three different stop reasons compared side by side instead of just reading them as text.

## Troubleshooting / common mistakes

- Running the command from the wrong folder — always run from the repository root.
- Copying a notebook's node (which only returns the fields it changed) into a plain-`dict` graph like `example.py`'s and getting a `KeyError` — a `TypedDict` schema lets unreturned fields carry forward automatically; a plain `dict` graph doesn't, so every field has to be re-emitted there. Check which state style the file you're editing actually uses before copying code between them.
- Treating `check_permission`'s allow/block decision as something a model chose — it's a fixed Python rule, not an agent decision.
- Assuming a loop would eventually stop on its own even without an explicit cap — it wouldn't, if the passing condition were unreachable.
- Adding framework helpers (LangChain tools, `ToolNode`, etc.) that aren't used anywhere in this folder's code.

## Assignment

**What am I actually being asked to do?**
Make one small change to `example.py` — `PASS_THRESHOLD` or `MAX_ATTEMPTS` — predict the new output before running, run it, and write three short sentences: what you changed, what happened, and why.

**Can I use the notebooks for the assignment?**
No — the assignment is scoped to `example.py` only. Keep the example in one Python file, use LangGraph directly, and change only a constant's value, not the graph itself.
