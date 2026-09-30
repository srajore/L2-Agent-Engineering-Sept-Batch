# Session 13 Trainer Guide — Harness and Loop Engineering

## Outcome

By the end of the session, a learner can run one file and point to two separate things in it: the loop (`act`/`verify`, which repeats) and the harness (`enforce_limit`'s attempt cap, which guarantees the repeating stops).

## Files to Use

- `example.py` — the only graded learner code file
- `01_loop_engineering.ipynb`, `02_harness_engineering.ipynb` — instructor-run demo notebooks, not part of the graded assignment (see "Concept to Teach First" below)
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)
- `FAQ.md` — quick-reference answers for setup, concept, and code questions
- `infographic.html` — a single offline HTML page (open directly in a browser, no server or Ollama needed) visualizing the loop diagram, the three stop signals, the five harness components, and how prompt/context/loop/harness engineering nest inside one another; useful to have open alongside the slides during the concept talk

Do not create a test folder or extra helper modules for this introductory lesson.

## Concept to Teach First (before opening any code)

Teach the two halves of this session's title as two separate ideas, in this order, before showing `example.py`. This talking-point outline is a plain-language, deterministic-example version of two ideas currently circulating under the names "loop engineering" and "harness engineering" — introduce them as engineering discipline, not as buzzwords.

**1. Loop engineering — the repeating cycle, and why it needs more than one way to stop.**

- The underlying primitive behind any repeating agent action is: act, then check the result, then decide whether to repeat. Say this out loud before naming it: "do the step, check the step, decide again."
- A loop that only asks "did it pass yet?" is not safe by itself — if the pass condition is never reachable, that loop runs forever. This is exactly what today's `example.py` demonstrates when `PASS_THRESHOLD` is changed to `1000`.
- In real systems, every extra iteration has a real cost (time, money, tokens). So a well-designed loop is watched by *several* independent stop signals at once, not just one: a success signal, a hard cap on the number of attempts, and a cost or resource budget that can end the run even earlier than the attempt cap. None of these should be assumed to make the others unnecessary.
- Ask learners: "if we only had the attempt cap, and removed it, what happens when the pass condition is unreachable?" (Answer: it never stops — this is the danger a real production loop must never have.)

**2. Harness engineering — everything around the action that is not the action itself.**

- Introduce the analogy: a horse is raw power; a harness is what turns that power into directed, useful work. The "engine" here — the model, or in today's deterministic example, the repeated action — is not what makes a system reliable. What is wrapped around it is.
- Name the five components learners will keep meeting for the rest of the course, in plain words, with no code yet:
  1. **System of record** — the written-down rules an agent (or a process) is expected to follow, kept where the work happens, not scattered in chat threads.
  2. **Tools** — the small, deliberate, justified set of actions something is allowed to take. Too much access makes behavior unpredictable; too little makes it useless.
  3. **Feedback loops / verification** — a way to check the work without asking a human every time. This is where loop engineering and harness engineering meet.
  4. **Guardrails and permissions** — what is explicitly *not* allowed, and which actions require a stop-and-ask instead of a guess.
  5. **Observability and memory** — a record of what actually happened, so a failed run can be reconstructed instead of guessed at.
- Make the point explicit: today's `example.py` already contains two of these five in miniature — `enforce_limit`'s attempt cap is a guardrail, and the printed "Stopped because" line is a one-line observability record. The two supplementary notebooks below each build one more of these components on its own, deterministically, so each idea can be pointed at separately.

**3. How today's two notebooks extend the concept (run these live, after the concept talk, before or after `example.py` — instructor's choice):**

- `01_loop_engineering.ipynb` extends the loop-engineering idea: the same act/verify shape as `example.py`, but the router now checks three independent stop signals (verification passed, cost budget reached, iteration cap reached) instead of one, and the notebook runs the same graph three times so each stop reason happens on its own run. Ask learners, before running each cell: "which of the three signals do you expect to end this run, and why?"
- `02_harness_engineering.ipynb` extends the harness-engineering idea: a fixed allowlist (`ALLOWED_ACTIONS`) is the system of record, `check_permission` is the guardrail, and a `trace` list threaded through state is the observability record. Run it once with an allowed action and once with a blocked one, and have learners read the printed trace back as if it were a log from a failed production run.
- Neither notebook adds a model call or an agent decision (a model choosing the next node) — that boundary stays where the course puts it, at Day 6 (and revisited at Days 11–12). These notebooks are about the deterministic scaffolding *around* that boundary, which is what "harness" and "loop" refer to even when a model is involved.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Day-13-Harness-Loop-Engineering\example.py
```

This example is deterministic and does not need a live model call. It still teaches a LangGraph building block.

## Suggested 120-Minute Flow

1. **15 minutes — Concept:** Deliver the "Concept to Teach First" talking points above, with no code on screen yet — the horse/harness analogy, the "several stop signals" idea, and the five harness components.
2. **10 minutes — Predict:** Show the `example.py` graph picture and ask learners what will happen.
3. **20 minutes — Read `example.py`:** Walk through it top to bottom. Have learners physically point to which lines belong to the loop and which belong to the harness.
4. **15 minutes — Run and change `example.py`:** Execute it, then let learners set `PASS_THRESHOLD = 1000` and re-run, so they see the harness — not the loop — end the run.
5. **20 minutes — `01_loop_engineering.ipynb`:** Run it live, cell by cell. Before the final cell, ask learners to predict each run's stop reason.
6. **20 minutes — `02_harness_engineering.ipynb`:** Run it live. Read the printed `trace` back out loud as if reconstructing a failed run.
7. **10 minutes — Explain:** Ask learners to describe, across all three files, which piece was the loop, which was the harness, and why `MAX_ATTEMPTS`/`budget`/`ALLOWED_ACTIONS` all had to be written down explicitly instead of relying on things happening to work out.

## Code Walkthrough Questions

1. What value enters the graph?
2. What does each node return?
3. Which lines belong to the loop, and which belong to the harness?
4. Is the next step fixed, rule-based, or model-selected?
5. What value is printed at the end, and how does the last printed line tell you which piece of logic ended the run?
6. What one safe input change can we try to make the harness (rather than the loop) be the thing that stops the run?

## Common Mistakes

- Running the command from the wrong folder
- Reading every line at once instead of following the graph order
- Changing the graph and the input at the same time
- Confusing a normal Python function with a model decision
- Treating `enforce_limit`'s attempt cap as part of the loop's own logic, instead of as a separate, externally imposed rule
- Assuming the loop would eventually stop on its own even without `MAX_ATTEMPTS` — it wouldn't, if the passing rule were unreachable
- Adding framework helpers that are not used in `example.py`

## Exit Check

The learner should be able to point to the start, each node, the route, the end, and the printed result — and, specifically, name which node/logic is "the loop" and which is "the harness." For Session 6 and later agent examples, also ask who chooses the next action and how that choice is limited.
