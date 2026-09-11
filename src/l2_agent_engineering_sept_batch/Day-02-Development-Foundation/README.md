# Day 2 — Development Environment and First Model Call

## What You'll Learn Today

- How the course software stack fits together: VS Code, Python, `uv`, Ollama, and Git.
- How to run `uv sync` and `uv run` so your project uses an isolated, reproducible environment.
- How the fixed course model, `gpt-oss:120b-cloud`, is reached through a local Ollama connection.
- The difference between a model, a client library, and an API.
- What system, user (human), and assistant (AI) message roles are for, and how they shape a model's answer.
- How to call the model directly with `ollama.chat`, and read the response it sends back.

## Why This Matters

Session 1 was about deciding when to use a model at all. Today you actually make your first live call to one. The goal is small on purpose: one ticket goes in, and the application should come back with something useful, wired through one plain model call — no framework, no graph, no tools, no memory, and no agent loop yet. Getting comfortable with the plumbing now — the software stack, the isolated `uv` environment, and how a request reaches the cloud-hosted model through a local Ollama connection — means that when Day 3 introduces LangGraph, you are only ever adding one new idea at a time instead of debugging your setup, your logic, and a new framework all at once.

## Key Concepts

**The course software stack.** VS Code is where you edit code. Python runs it. `uv` manages your packages and creates an isolated environment, so `uv sync` builds that environment and `uv run` executes your code inside it — you never need to activate anything manually. Ollama is the piece that connects your code to the model, and Git records your changes. When something breaks, it helps to ask which one of these layers actually owns the failure, and check that layer first.

**Reaching the model.** Your Python code talks to a local Ollama service running on your machine. Once you are signed in, Ollama can run the fixed model `gpt-oss:120b-cloud` through its cloud service and hand the result back through that same local interface. In other words, the model is cloud-hosted even though your code only ever points at a local address. A useful debugging order is: check your `uv` version, run `uv sync`, confirm you are signed in to Ollama, confirm the model is reachable, and only then look at your own code.

**Model, client, and API — three different things.** The model is what actually generates the response. The client library (here, the `ollama` Python package) is what builds and sends the request. The API is the agreed shape of that request and its response. Swapping out a client library does not retrain or change the underlying model.

**Message roles.** A model call is built from a small stack of messages with roles: a system message holds stable, unchanging instructions about how the model should behave; a user (human) message holds the specific request for this call; an assistant (AI) message holds what the model answered. The order and the wording of these messages genuinely changes the model's behavior, so a good system message is worth writing carefully — it should state the task, the shape of the expected output, any allowed categories, and what to do about missing information, without asking the model to invent facts it doesn't have.

**Response objects and safe configuration.** What comes back from `ollama.chat` is not just a plain string — it is a structured response that can carry model metadata, timing, and usage information alongside the actual text your application needs to extract. Keeping the model name and base URL in one visible, central place (rather than scattered across files) prevents different parts of a project from silently drifting onto different models. The model name itself is fine to keep visible in code, but real secrets — credentials, tokens, private ticket data — never belong in source control.

## Code Walkthrough — `Day-02-Development-Foundation/example.py`

```python
"""Session 2: make one Ollama call and read the response it sends back."""

import sys

import ollama

sys.stdout.reconfigure(encoding="utf-8")  # the model may answer with punctuation Command Prompt cannot print


MODEL = "gpt-oss:120b-cloud"

request = input("Enter an IT request: ")

response = ollama.chat(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Classify the request in one word."},
        {"role": "user", "content": request},
    ],
)

print("Category:", response["message"]["content"])
```

1. `sys.stdout.reconfigure(encoding="utf-8")` makes sure Command Prompt can print any punctuation the model might return.
2. `MODEL` is set once, at the top, to the fixed course model. Keep this value unchanged.
3. The program asks you to type an IT request, then calls `ollama.chat` with two messages: a system message telling the model to classify the request in one word, and a user message containing the request text you typed.
4. There is no branching and no framework here — the developer controls every step, and the model only produces text. LangGraph is introduced from zero starting Day 3.
5. The last line prints the category the model returned, read out of `response["message"]["content"]`.

## Hands-On Lab (~30 minutes)

**Steps to trace:** typed request -> `ollama.chat` -> printed category

**Setup and run, from the repository root, in Windows Command Prompt:**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-02-Development-Foundation\example.py
```

**Walkthrough steps:**

1. Read the short description at the top of the file.
2. Find where the request is read with `input()`.
3. Find the `ollama.chat` call and its system and user messages.
4. Follow the value from the typed request, into the call, to the printed result.
5. Predict the printed result before you run the file — then type an IT request when prompted and see what category comes back.

**Small change to try:** Type a different IT request (for example, one about a password reset versus one about a broken printer) and compare the category the model returns.

**Control question:** Who controls what happens here? The developer does — there is exactly one step, and it always runs. The model only produces text; it does not choose what happens next.

## Assignment

**Goal:** Make one small change to `example.py` and explain how the result changes.

**Steps:**

1. Run the example once and note the IT request you type in and the category it returns.
2. Predict what category a different request would get, before typing it.
3. Run the example again from the repository root:
   ```cmd
   uv run python Day-02-Development-Foundation\example.py
   ```
4. This time, type a different IT request.
5. Compare the new category to your prediction.
6. Write three short sentences: what request you used, what category came back, and why you think the model chose that category.

**Rules:**

- Keep the example in one Python file.
- Do not import LangGraph or any other framework — this session is a plain model call on purpose, before Day 3 introduces LangGraph.
- Do not add a test folder or helper package.
- Do not replace `uv` commands with another package manager.
- Use the Windows Command Prompt commands shown above.
- Keep `MODEL = "gpt-oss:120b-cloud"` unchanged.

## Before You Move to Day 3

- The file still runs and successfully reaches the model.
- You can name the input, the model call, and the output.
- You can explain who controls the next step (the developer, not a framework, since none is used yet) versus what the model actually produces (just text).
- You tried at least two different IT requests and compared the categories returned.
- Your explanation uses simple words and matches what you actually observed.

**A note on the source material:** the slides for this session describe a richer system prompt (with output labels, allowed categories, and a missing-information rule), but the actual `example.py` uses a simpler one-line instruction, "Classify the request in one word." This walkthrough follows the real code. Also, the assignment steps in the original `assignment.md` refer to "the sample input near the bottom of `example.py`," but the file actually reads input interactively via `input()` rather than using a fixed sample value — the steps above have been adapted to match the real behavior of the file.
