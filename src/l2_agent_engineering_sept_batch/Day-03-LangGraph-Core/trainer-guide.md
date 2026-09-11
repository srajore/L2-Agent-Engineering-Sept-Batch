# Session 3 Trainer Guide — LangGraph Core

## Outcome

By the end of the session, a learner can run one file and explain how it helps them pass state through two fixed nodes.

## Files to Use

- `example.py` — the only learner code file
- `slides.pptx` — the classroom deck
- `README.md` — the participant handout (objectives, concepts, code walkthrough, lab steps, and assignment)

Do not create a test folder or extra helper modules for this introductory lesson.

## Before the Graph: Why a Framework, Why LangGraph

Open with two short questions before any code: "Why can't we just write `if/else` for an agent?" and "What else is out there besides LangGraph?"

- One model call is not an agent. Real requests need shared state, a next-step decision, tool calls, retry/failure paths, and sometimes a human check. Hand-written control flow for all of that stops being readable fast — a framework standardizes the pieces.
- Name the landscape honestly: LangChain, CrewAI, AutoGen/AG2, the OpenAI Agents SDK, LlamaIndex agents, and Semantic Kernel all solve this same orchestration problem in different styles. **This course teaches LangGraph only and does not teach LangChain classes.**
- Land on why LangGraph for L2: explicit state you can print at every step, the same graph shape for a workflow and an agent, and native support for the branches/loops/interrupts/checkpoints used later in the course.

Keep this to slides — no code yet. Slides 4–6 of `slides.pptx` carry this content.

## Setup in Windows Command Prompt

From the repository root:

```cmd
uv sync
uv run python Day-03-LangGraph-Core\example.py
```

This example is deterministic and does not need a live model call. It still teaches a LangGraph building block.

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
