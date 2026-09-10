# Session 1 Trainer Guide — Generative AI and Agentic AI Foundations

## Outcome

By the end of the session, a learner can run one file and explain how it helps them decide whether a problem needs a workflow or an agent.

## Files to Use

- `example.py` — the only learner code file
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)

Do not create a test folder or extra helper modules for this introductory lesson.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Day-01-AI-Agent-Foundations\example.py
```

This example is deterministic, does not need a live model call, and deliberately does not import LangGraph — that starts Day 3. Today is plain Python only: two functions, called in a fixed order.

## Suggested 120-Minute Flow

1. **10 minutes — Predict:** Show the flow picture (`understand_request -> choose_action -> printed result`) and ask learners what will happen.
2. **25 minutes — Teach:** Explain the one session concept in plain language.
3. **30 minutes — Read:** Walk through `example.py` from top to bottom.
4. **25 minutes — Run:** Execute the file in Windows Command Prompt and trace the value through both functions.
5. **20 minutes — Change:** Let learners change the sample input near the bottom of the file.
6. **10 minutes — Explain:** Ask learners to describe the input, both functions, and the output.

## Code Walkthrough Questions

1. What value enters the first function?
2. What does each function return?
3. Is the next step fixed, rule-based, or model-selected?
4. What value is printed at the end?
5. What one safe input change can we try?

## Common Mistakes

- Running the command from the wrong folder
- Reading every line at once instead of following the call order
- Changing the code and the input at the same time
- Confusing a normal Python function with a model decision
- Adding framework helpers (including LangGraph) that are not used in `example.py` — there is no framework in this session on purpose

## Exit Check

The learner should be able to point to the input, each function, and the printed result, and explain the order they run in. For Session 6 and later agent examples, also ask who chooses the next action and how that choice is limited.

## A note for you as trainer

This is the one session in the whole course with no framework at all — no LangGraph, no graph, no nodes or edges. If a learner asks "is this LangGraph?", the honest answer is no, and that's deliberate: Day 1 is about the workflow-versus-agent decision itself, not about any particular tool. LangGraph starts fresh on Day 3, from zero, with no assumed exposure from today.
