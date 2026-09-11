# Session 2 Trainer Guide — Development Environment and First Model Call

## Outcome

By the end of the session, a learner can run one file and explain how it helps them call the course model directly with `ollama.chat` — no framework yet.

## Files to Use

- `example.py` — the only learner code file
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)

Do not create a test folder or extra helper modules for this introductory lesson.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Day-02-Development-Foundation\example.py
```

This example calls `ollama.chat` with the fixed model `gpt-oss:120b-cloud`. Keep that model name unchanged.

## Suggested 120-Minute Flow

1. **10 minutes — Predict:** Show the request-in, category-out shape and ask learners what will happen.
2. **25 minutes — Teach:** Explain the one session concept in plain language.
3. **30 minutes — Read:** Walk through `example.py` from top to bottom.
4. **25 minutes — Run:** Execute the file in Windows Command Prompt and trace the call.
5. **20 minutes — Change:** Let learners type a different IT request and compare results.
6. **10 minutes — Explain:** Ask learners to describe the input, the model call, and the output.

## Code Walkthrough Questions

1. What value is read from `input()`?
2. What two messages go into `ollama.chat`?
3. Is the next step fixed, rule-based, or model-selected?
4. What value is printed at the end?
5. What one safe input change can we try?

## Common Mistakes

- Running the command from the wrong folder
- Reading every line at once instead of following the call order
- Changing the system message and the input at the same time
- Confusing a normal Python function with a model decision
- Adding LangGraph or other framework code that is not used in `example.py` — that starts Day 3

## Exit Check

The learner should be able to point to the input, the model call, and the printed result, and explain that there is no framework involved yet. For Session 6 and later agent examples, also ask who chooses the next action and how that choice is limited.
