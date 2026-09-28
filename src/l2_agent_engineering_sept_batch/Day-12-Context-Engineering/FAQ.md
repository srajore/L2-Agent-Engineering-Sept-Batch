# Day 12 — Context Engineering: FAQ

## Setup and running

**Do I need Ollama for today's session?**
Yes. Day 12 is one of the model-backed sessions (2, 6, 9, 12, 15, 17). `example.py` and all four supplementary notebooks call `ollama.chat` for real, so Ollama must be running locally with `gpt-oss:120b-cloud` available.

**What's the exact command to run `example.py`?**
From the repository root, in Windows Command Prompt:
```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-12-Context-Engineering\example.py
```

**I get a connection error calling the model. What's wrong?**
Ollama isn't running, or `gpt-oss:120b-cloud` isn't available on this machine. Confirm Ollama is running locally and the model is pulled/available before re-running.

**Do I need `ollama signin` for Day 12?**
It's a one-time setup step for the whole course, not something you redo per day (see the root `CODE_GUIDE.md`). If you haven't run it yet on this machine, run `ollama signin` once; if `ollama.chat` fails with an authentication-style error rather than a connection error, that's the likely cause.

**How do I run the `.ipynb` notebooks?**
Open them in VS Code (with the Jupyter extension) or Jupyter itself and run cells normally — or just read them, since all four were already executed and their real output is saved in place. They live in this same folder: `02_context_selection.ipynb`, `03_context_compression.ipynb`, `04_context_offloading.ipynb`, `05_context_isolation.ipynb`.

**Can I re-run the notebooks myself?**
Yes, they call the live model the same way `example.py` does, so re-running will produce a fresh (possibly slightly different) answer each time. If you re-run and save, you'll overwrite the saved output — that's fine, it's expected if you're experimenting.

## What is context engineering, in one sentence?

Deciding, on purpose, what a model actually sees for one call — the current question, any useful state, relevant history, retrieved evidence, and tool results — each one labelled so you can see exactly what the model received and why. A bigger or more capable model doesn't remove the need for this.

## The five context types

**What are the five context types?**
- **Task** — the current user question; it anchors the whole call.
- **State** — execution facts the app already knows (route, status, counters, results). Only the fields the model actually needs belong in the prompt.
- **Memory** — relevant earlier turns. The model doesn't remember previous turns on its own — the app has to resend this history itself.
- **RAG** — retrieved, source-labelled passages (like `KB-102`). Both relevance and whether the source is authorized to be shown matter.
- **Tool** — the result of an action the system just took, with secrets or irrelevant raw fields stripped out first.

**Why label each section (`TASK`, `TOOL`, `RAG`, `MEMORY`)?**
So you can inspect exactly what went into a call, and so citation checks are possible later — you can trace an answer back to the labelled section it came from.

**What's the priority order when assembling context?**
`TASK` first, then `TOOL`, then `RAG`, then `MEMORY` — current tool output outranks related RAG or memory content, since it's the freshest fact. `03_context_compression.ipynb` joins its sections (`TASK`, `RAG`, `MEMORY` — it has no separate `TOOL` section) in that same task-first order, but which section actually gets *dropped* when the budget is tight is now the model's own decision (see the next section) — `MEMORY` is what the code falls back to if the model's answer isn't usable.

## The four strategies

**What are the four context engineering strategies covered this session?**
- **Select** (`02_context_selection.ipynb`) — the model reads every candidate RAG passage and picks the relevant one (or `NONE`); that choice routes to `include_rag` or `skip_rag`.
- **Compress** (`03_context_compression.ipynb`) — the model picks which section to cut when over budget (`RAG` or `MEMORY`). `TASK` is never offered as an option.
- **Offload** (`04_context_offloading.ipynb`) — write a large result to external storage; the model decides `FULL` or `SUMMARY` for how much of it the request actually needs.
- **Isolate** (`05_context_isolation.ipynb`) — the model triages which specialist(s) the task needs (`NETWORK`, `ACCOUNT`, or `BOTH`); LangGraph only runs the branch(es) chosen, and whichever runs still gets its own separate context and its own model call.

In each of these four, the deciding step is a genuine agent decision — the model's own output is what `add_conditional_edges` routes on, exactly like Day 6, not a hand-written `if`/`else`. See `CLAUDE.md`'s "Model-backed days" section for why this is a documented exception to the "agent boundary only at Day 6" rule.

**What is context offloading, specifically?**
Keeping large or bulky information out of the active context window and storing it somewhere external instead (a file, vector store, or database — in `04_context_offloading.ipynb` it's a plain dict called `OFFLOAD_STORE` standing in for one of those). The model decides whether the request needs the full text (`FULL`) or just the short reference and summary (`SUMMARY`, the safe default) — only on `FULL` is the full text read back and appended to the context, via a conditional route (`add_conditional_edges`).

**Why does compression drop whole sections instead of truncating text mid-sentence?**
Truncating mid-string risks cutting off a qualifier or a source detail right when you need it most. `03_context_compression.ipynb` avoids that by dropping one whole labelled section at a time — the model decides which one, and the drop is recorded — so nothing is silently corrupted, only silently omitted (and you can see what was omitted).

**Why is `TASK` never dropped?**
It's the question itself — the one thing the model call can't function without. Every other section supports answering the task; the task is the reason for the call. `03_context_compression.ipynb` doesn't just trust the model to know this — `TASK` is never even offered to it as an option, so an off-the-rails answer can't remove it.

**What happens if the model's answer doesn't match one of the allowed options?**
Every one of the four notebooks corrects it to a safe default, the same pattern Day 6 and Day 11 use: `02` falls back to `NONE` (skip the passage), `03` falls back to `MEMORY` (the old fixed-priority answer), `04` falls back to `SUMMARY` (don't over-share), and `05` falls back to `BOTH` (consult an extra specialist rather than risk skipping a needed one).

**How is context isolation different from just building one context with everything in it?**
In isolation, each specialist gets its own separate context and makes its own model call — neither one ever sees the other's facts. Only the final *results* (not the raw contexts) are merged afterward. This prevents one specialist's information from leaking into, or distracting, the other's answer. In `05_context_isolation.ipynb`, the model also decides which specialist(s) are needed in the first place — the branch(es) it doesn't pick simply never run, and `merge_results` reports the skipped one as `(not consulted)`.

## Code questions

**Why does `example.py` use `class State(TypedDict)` instead of a plain `dict`?**
Passing a typed `State` to `StateGraph(State)` (instead of `StateGraph(dict)`) tells LangGraph to merge each node's returned keys into state one field at a time, and it documents every field the graph can hold. This is the same pattern used from Day 4 onward.

**What does `sys.stdout.reconfigure(encoding="utf-8")` do, and why isn't it in the notebooks?**
It's a Windows Command Prompt safety fix in `example.py`, so punctuation the model returns can always be printed without crashing the console. It's deliberately left out of the notebooks because Jupyter's own output stream already handles UTF-8 and doesn't support `.reconfigure` — including that line in a notebook would raise `AttributeError: 'OutStream' object has no attribute 'reconfigure'`.

**Is the routing in `04_context_offloading.ipynb` an agent, like Day 6?**
Yes. `decide_detail_level` calls the model, and its output (`FULL` or `SUMMARY`) is what `add_conditional_edges` routes on — the same pattern as Day 6's `decide` node. This is a documented, deliberate exception: Day 12's `example.py` stays a fixed pipeline (it's the graded file), but all four supplementary notebooks (`02`–`05`) are agents by this course's own definition, alongside Day 6 and Day 11. See `CLAUDE.md`'s "Model-backed days" section.

**Do the four supplementary notebooks count toward the graded assignment?**
No. `example.py` is the only graded file. The four notebooks are instructor-run demos that build on `example.py` one technique at a time — useful for understanding the fuller picture of context engineering, but not required for the Day 12 assignment.

## Troubleshooting / common mistakes

- Running the command from the wrong folder — always run from the repository root.
- Reading every line of `example.py` at once instead of following the graph order (`START -> build_context -> ask_model -> END`).
- Changing the graph and the sample input at the same time — change one thing, predict, then run.
- Confusing a normal Python function with a model decision — in the notebooks, only the functions that call `ollama.chat` and feed `add_conditional_edges` (like `classify_rag`, `decide_cut`, `decide_detail_level`, `triage_ticket`) are agent decisions; helper functions like `include_rag`/`skip_rag`, the two `drop_*_section` functions, and `build_network_context`/`build_account_context` are plain code that just carries out what was already decided.
- Adding framework helpers that aren't used anywhere in `example.py`.
- Changing `MODEL = "gpt-oss:120b-cloud"` — keep it exactly as is across the whole course.

## Assignment

**What am I actually being asked to do?**
Make one small change to `example.py` (one input value or one short sentence), predict the new output before running, run it, and write three short sentences: what you changed, what happened, and why.

**Can I change the graph structure for the assignment?**
No — keep the example in one Python file, use LangGraph directly, and change only a sample input value, not the graph itself.
