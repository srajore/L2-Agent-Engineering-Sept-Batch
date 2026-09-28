# Session 12 Trainer Guide — Context Engineering

## Outcome

By the end of the session, a learner can run one file and explain how it helps them build a small context block for one model call.

## Files to Use

- `example.py` — the graded learner code file (labelled context assembly)
- `02_context_selection.ipynb`, `03_context_compression.ipynb`, `04_context_offloading.ipynb`, `05_context_isolation.ipynb` — supplementary, instructor-run demo notebooks, each adding one more context engineering technique on top of `example.py` (selection, compression/budget, offloading, isolation). Already executed with real output saved in each cell, and a markdown cell above every code cell explains what it does — open them in Jupyter or VS Code and read top to bottom. Not part of the graded assignment. **These four are a documented exception to "agent boundary only at Day 6"** (see `CLAUDE.md`'s "Model-backed days" section and `curriculum/delivery-standard.md`): in each one, the model's own output selects the next node via `add_conditional_edges`, validated against a fixed allowlist with a safe-default fallback — the same pattern as Day 6's `decide` node, applied to context engineering.
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)
- `FAQ.md` — reference Q&A for setup, the five context types, the four strategies, and common mistakes; point learners here for self-serve troubleshooting

Do not create a test folder or extra helper modules for this introductory lesson.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Day-12-Context-Engineering\example.py
```

This example calls `ollama.chat` with the fixed model `gpt-oss:120b-cloud`. Keep that model name unchanged.

## Suggested 120-Minute Flow

1. **10 minutes — Predict:** Show the graph picture and ask learners what will happen.
2. **25 minutes — Teach:** Explain the one session concept in plain language.
3. **30 minutes — Read:** Walk through `example.py` from top to bottom.
4. **25 minutes — Run:** Execute the file in Windows Command Prompt and trace the state.
5. **20 minutes — Change:** Let learners change one sample input near the bottom of the file.
6. **10 minutes — Explain:** Ask learners to describe the input, nodes, route, and output.

## Code Walkthrough Questions

1. What value enters the graph?
2. What does each node return?
3. Is the next step fixed, rule-based, or model-selected?
4. What value is printed at the end?
5. What one safe input change can we try?

## Common Mistakes

- Running the command from the wrong folder
- Reading every line at once instead of following the graph order
- Changing the graph and the input at the same time
- Confusing a normal Python function with a model decision
- Adding framework helpers that are not used in `example.py`

## Exit Check

The learner should be able to point to the start, each node, the route, the end, and the printed result. For Session 6 and later agent examples, also ask who chooses the next action and how that choice is limited.

If time allows, demo `04_context_offloading.ipynb` and ask the learner to explain, in their own words, why a large result is stored outside the context instead of sent every time — and where in the notebook the graph decides whether to read it back. Then ask them to point out specifically *who* makes that decision (the model, via `decide_detail_level`) versus Session 4's routing (a developer-written `if`/`else`) — this is the same contrast the Session 11 trainer-guide draws, now applied to a context engineering technique instead of a request-routing one.
