# Day 1 — Generative AI and Agentic AI Foundations

## What You'll Learn Today

- How to run one small Python file and explain, in plain words, what happens inside it.
- The difference between AI, machine learning, deep learning, and generative AI.
- What a large language model (LLM) does and does not give you automatically.
- The course definition of an "agent," and why an agent's freedom is always bounded by the developer.
- How to tell whether a problem needs a fixed workflow or a bounded agent.
- How requirements and acceptance criteria turn a business need into something you can test.

## Why This Matters

Today has no framework code to speak of — it is about building a decision method you will use for the rest of the course. Before you write a single line of LangGraph (starting Day 3), you need a clear head on what generative AI actually provides (text, code, or other content generated from instructions) and what it does not provide on its own, such as current private data, verified facts, or durable memory. Once that is clear, the next question becomes practical: does this problem need a fixed, developer-controlled workflow, or does it need a bounded agent where a model is allowed to choose the next action inside limits you define? Getting this decision right early avoids two common mistakes: building an overly rigid system for a genuinely ambiguous problem, or bolting a model onto a problem that a simple rule already solves perfectly well.

## Key Concepts

**The AI capability hierarchy.** AI is the broad category of software that reasons, perceives, predicts, or supports decisions. Machine learning is a part of AI that finds patterns from examples. Deep learning is a part of machine learning that uses layered neural networks for more complex patterns. Generative AI is a part of deep learning that produces new content — text, code, images, audio — from instructions and context. These layers describe different capabilities, not a ranking of quality.

**The LLM mental model.** Instructions and context go into the model, the model generates a response token by token, and your application code reads that response. The important trap to avoid is thinking the model automatically knows your private data, verified facts, business authority, durable memory, or how to use tools, or that it can prove an action actually happened. It only sees what you explicitly hand it in the request. Your application code is what supplies the missing pieces, selectively and on purpose.

**Agents versus workflows.** This course defines an agent as software in which a model can choose a next action, within developer-defined boundaries, to pursue a goal. A workflow, in contrast, is deterministic: the developer defines every transition, and the same state always produces the same route — even if a workflow calls an LLM along the way. "Bounded autonomy" means the developer, not the model, decides which actions, tools, data, limits, and approvals are even available to choose from. More autonomy always increases how much verification you need.

**When to use which.** Use a plain workflow when rules are stable, inputs are structured, decisions are regulated, and paths are predictable — language appearing in the input is not, by itself, a reason to reach for an agent. Reach for a bounded agent when requests are genuinely ambiguous, information needs vary, tool choice needs to be dynamic, or the task needs iterative investigation. And sometimes the right answer is "don't use an agent at all" — for example when a mistake would be too costly, the needed data or authority isn't available, success can't be measured, or the latency and cost don't fit the use case. Adding a model on top of a bad process does not fix the process.

**Requirements, acceptance criteria, and the bigger picture.** A requirement describes a needed capability or constraint; an acceptance criterion describes an observable, testable result for a specific condition — replace vague words like "accurate" with a concrete example, threshold, source, or check. This connects to the software development lifecycle (SDLC: requirements, design, implementation, test, release, maintenance) and its agent-specific extension, the ADLC, which adds model behavior, prompts, context, tools, evaluation, and feedback on top of ordinary engineering discipline — it doesn't replace that discipline.

## Code Walkthrough — `Day-01-AI-Agent-Foundations/example.py`

```python
"""Session 1: see how a request moves through a fixed sequence of steps."""


def understand_request(request):
    return request.lower()


def choose_action(request):
    if "delete" in request:
        return "Ask a human for approval"
    return "Continue with the safe workflow"


request = understand_request("Delete an old user account")
action = choose_action(request)
print(action)
```

This example is intentionally deterministic — it does not call a model, and it does not use LangGraph yet. That starts Day 3. Today's point is the decision logic itself, in the plainest form possible: one function feeds the next.

1. The file starts with one sample request string.
2. `understand_request` is the first step. It lowercases the text and returns it — nothing else.
3. `choose_action` is the second step. It checks whether the word "delete" appears in the request. If so, it returns "Ask a human for approval"; otherwise it returns "Continue with the safe workflow".
4. The bottom of the file calls both functions in a fixed order — `understand_request`, then `choose_action` — and prints whatever the second one returned.
5. Nothing here is dynamic: the same input always produces the same sequence of calls and the same output.

## Hands-On Lab (~30 minutes)

**Steps to trace:** `understand_request` → `choose_action` → printed result

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-01-AI-Agent-Foundations\example.py
```

**Walkthrough steps:**

1. Read the short description at the top of the file.
2. Find each function (`understand_request`, `choose_action`).
3. Find the three lines at the bottom that call them and print the result.
4. Follow the value from the sample request, through each function, to the final print.
5. Predict the printed result before you run the file.

**Small change to try:** Change the word "delete" in the sample request to "view" and predict the new outcome before running it again.

**Control question:** Who controls every step here? The developer does — there is no model call and no framework involved yet, just two plain functions called in a fixed order.

## Assignment

**Goal:** Make one small change to `example.py` and explain how the result changes.

**Steps:**

1. Read the sample input near the bottom of `example.py`.
2. Predict the current output without running the file.
3. Run the example from the repository root:
   ```cmd
   uv run python Day-01-AI-Agent-Foundations\example.py
   ```
4. Change only one input value or one short input sentence.
5. Predict the new output.
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:**

- Keep the example in one Python file.
- Do not import LangGraph or any other framework — this session is plain Python on purpose, before Day 3 introduces LangGraph.
- Do not add a test folder or helper package.
- Do not replace `uv` commands with another package manager.
- Use the Windows Command Prompt commands shown above.
- Do not add an Ollama call — this session's example is intentionally deterministic.

## Before You Move to Day 2

- The file runs successfully on your machine.
- You can name both functions and explain the order they run in.
- You can explain who controls the next step (the developer, not a model — and not a framework, since none is used yet).
- You made one small change, predicted the effect first, then confirmed it by running the file again.
- Your three-sentence explanation matches what you actually observed.
