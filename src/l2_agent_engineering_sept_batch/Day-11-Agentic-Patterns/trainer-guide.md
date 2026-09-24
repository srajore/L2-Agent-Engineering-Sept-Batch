# Session 11 Trainer Guide — Agentic Patterns

## Outcome

By the end of the session, a learner can run one file and explain why it is an agent, not a workflow — specifically, that the model's own output is what LangGraph routes on.

## Files to Use

- `example.py` — the graded learner code file (router pattern, rebuilt as an agent)
- `pattern-1-fixed-pipeline.py`, `pattern-3-planner-executor.py`, `pattern-4-evaluator-optimizer.py` — supplementary, instructor-run demo files covering the other three buildable patterns from the slides, in the same agent style. Not part of the graded assignment.
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)

Do not create a test folder or extra helper modules for this lesson.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
ollama signin
uv run python Day-11-Agentic-Patterns\example.py
```

This session is model-backed — every file calls `ollama.chat(model="gpt-oss:120b-cloud", ...)`, and each call's output is what LangGraph routes on. Because the call is live, output can vary slightly between runs; that's expected and worth pointing out rather than treating as a bug.

## Suggested 120-Minute Flow

1. **10 minutes — Predict:** Show the graph picture and ask learners what will happen.
2. **25 minutes — Teach:** Explain the one session concept in plain language, and contrast it against Days 1–5's fixed control flow and Day 2's model call that never changes the path.
3. **30 minutes — Read:** Walk through `example.py` from top to bottom.
4. **25 minutes — Run:** Execute the file in Windows Command Prompt and trace the state.
5. **20 minutes — Change:** Let learners change one sample input near the bottom of the file and predict which route the model will pick.
6. **10 minutes — Explain:** Ask learners to describe the input, nodes, route, and output — and to say in their own words why the model's output (not the `ollama.chat` call itself) is what makes this an agent.

## Code Walkthrough Questions

1. What value enters the graph?
2. What does each node return?
3. Is the next step fixed, rule-based, or model-selected?
4. What value is printed at the end?
5. What one safe input change can we try?
6. If you replaced the model call with a keyword `if`/`else` rule but kept everything else the same, would this still be an agent? (No — this is the point of the session.)

## Common Mistakes

- Running the command from the wrong folder
- Forgetting `ollama signin`, so the model call fails with a connection/auth error
- Reading every line at once instead of following the graph order
- Changing the graph and the input at the same time
- Assuming any file that calls a model is automatically an "agent" — point back to Day 2 (a model call on a fixed path) as the counter-example
- Adding framework helpers that are not used in `example.py`

## Exit Check

The learner should be able to point to the start, each node, the route, the end, and the printed result — and to explain, using this file specifically, that the model's own output selects the next node. Also ask them to contrast this with `pattern-1-fixed-pipeline.py`'s docstring, which explains why a fixed pipeline had to gain a real decision point before it could become an agent at all.
