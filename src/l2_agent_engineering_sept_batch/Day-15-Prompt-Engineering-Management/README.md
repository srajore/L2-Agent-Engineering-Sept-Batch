# Day 15 — Prompt Engineering and Management

## What You'll Learn Today

- Explain why prompts need structure, version history, and a reversible choice of which one is active, just like code does.
- Identify the parts of a well-formed prompt: role, objective, constraints, context instructions, and output contract.
- Render a prompt template by filling in a runtime variable — the request text.
- Select between two versions of a prompt (v1 and v2) before calling the model.
- Explain what "promotion" and "rollback" mean when managing prompt versions.
- Make a small change to `example.py`, predict the effect, and explain what happened.

## Why This Matters

Up to now, instructions to the model have been short strings embedded directly next to the model call — that's fine at first, but it gets harder to compare and improve as behavior evolves. Today's session treats a prompt as something worth managing on its own: something you can name, version, test, and switch between, the same way you'd manage a piece of code. To make the difference concrete, this session compares two versions of the same instruction on one support ticket — v1 asks for a brief answer, while v2 adds a length constraint (one short sentence) and a rule to abstain instead of guessing.

## Key Concepts

**The parts of a prompt.** The *role* names the assistant's function and its domain, and should constrain what it's allowed to talk about rather than add personality for its own sake. The *objective* describes one measurable outcome the user should walk away with, not a vague goal. *Constraints* rule out bad behavior directly — for example, don't invent facts, and abstain when there's no approved context to work from (this stays separate from the runtime permission and limit checks your code already enforces). *Context instructions* tell the model how to use the context and source ID it's given, keeping trusted instruction text clearly apart from the runtime data itself. An *output contract* defines a machine-checkable format for the answer, like a required marker or a bracketed source ID. This session's prompts don't go that far — `v2` instead adds two plain-language constraints: keep the answer to one short sentence, and don't guess when unsure. A stricter version could add a real output contract on top of that, since a fixed format is easy for code to check automatically.

**Templates and variables.** A prompt template has runtime variables — here, the `request` text — which get filled in when the template is rendered. (A template with more moving parts, like retrieved context, would have more variables to fill in; that's Day 12's territory, not this file's.) Rendering a template does not call the model by itself; it's purely a text-assembly step you can inspect before anything is sent. Validating that a template contains exactly the variables you expect (no more, no fewer) catches wiring mistakes early, before you ever run it against real test cases.

**Naming, versions, and evidence.** In a system with more than two prompts, you'd want a stable identifier (like `service-resolution`) that names what a prompt is *for*, while separate version labels (v1, v2, ...) describe specific revisions of its content — the identifier stays the same even as the wording changes. A registry mapping versions to their files, and a changelog recording what actually changed in behavior, make both the current choice and its history visible to anyone looking at the project. Today's file keeps this much simpler: `PROMPTS` is a flat dictionary holding both versions, and the `version` value passed into the graph is the only record of which one ran.

**Testing before promoting, and rolling back.** In a fuller setup, you'd freeze a fixed set of test cases — the same requests, run against both prompt versions, each checked with a simple deterministic rule (does the answer contain every required term for that case?) — before promoting a version to active. A word-match check like this can't fully prove semantic quality, but it gives a repeatable, explainable signal. Rollback matters just as much as promotion: being able to switch back to a previously retained version, without deleting the newer one or its evidence, matters when something needs to be re-checked. This file doesn't build that test harness or a promotion/rollback mechanism — it shows only the smallest piece those systems rely on: picking one named version (`state["version"]`) before the model is ever called, which is what makes switching between v1 and v2 possible at all.

## Code Walkthrough — `Day-15-Prompt-Engineering-Management/example.py`

```python
"""Session 15: select and use a clearly versioned prompt."""

import sys

import ollama
from langgraph.graph import END, START, StateGraph

sys.stdout.reconfigure(encoding="utf-8")  # the model may answer with punctuation Command Prompt cannot print


MODEL = "gpt-oss:120b-cloud"
PROMPTS = {
    "v1": "Answer the IT request.",
    "v2": "Answer the IT request in one short sentence. Do not guess.",
}


def create_prompt(state):
    instruction = PROMPTS[state["version"]]
    return {"prompt": f"{instruction}\nRequest: {state['request']}"}


def ask_model(state):
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": state["prompt"]}],
    )
    return {"answer": response["message"]["content"]}


graph_builder = StateGraph(dict)
graph_builder.add_node("create_prompt", create_prompt)
graph_builder.add_node("ask_model", ask_model)
graph_builder.add_edge(START, "create_prompt")
graph_builder.add_edge("create_prompt", "ask_model")
graph_builder.add_edge("ask_model", END)
graph = graph_builder.compile()

result = graph.invoke({"version": "v2", "request": "The VPN is down."})
print("Prompt version: v2")
print(result["answer"])
```

1. The `sys.stdout.reconfigure(encoding="utf-8")` line near the top is a Windows-console safety fix — it makes sure punctuation the model might return can actually be printed in Command Prompt without crashing.
2. `MODEL` is fixed to `"gpt-oss:120b-cloud"` — keep this unchanged. `PROMPTS` is a small dictionary holding both versions: `v1` is a bare instruction, `v2` adds "in one short sentence" and "Do not guess."
3. `create_prompt(state)` looks up the instruction for whichever `version` was requested, and renders it together with the actual `request` text into one `prompt` string.
4. `ask_model(state)` sends that rendered `prompt` to `ollama.chat` and returns the model's `answer`.
5. The graph wires `START -> create_prompt -> ask_model -> END` — the prompt is always fully assembled before the model is called.
6. `graph.invoke({"version": "v2", "request": "The VPN is down."})` runs the graph selecting v2, and the script prints which version was used along with the model's answer.

## Hands-On Lab (~30 minutes)

**Goal:** select a prompt version before calling the model.

**Graph to draw:** `START -> create_prompt -> ask_model -> END`

This lab needs **Ollama running locally** with the `gpt-oss:120b-cloud` model available, since `ask_model` makes a real call to it. Open only `example.py` in `Day-15-Prompt-Engineering-Management\`, then run it from the repository root:

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-15-Prompt-Engineering-Management\example.py
```

**Code walkthrough steps:** read the short description at the top, find each node function, find `StateGraph` and the node registrations, then follow the edges from `START` to `END`. Predict the printed result before you run the file.

**Small change to try:** run the file with `version` set to `"v1"` and then again with `"v2"`, using the same request, and compare the two answers.

**Control question:** the graph selects an approved prompt version — the choice is explicit in the state, not hidden.

## Assignment

**Goal:** make one small change to `example.py` and explain how the result changes.

**Steps:**
1. Read the sample input near the bottom of `example.py`.
2. Predict the current output without running the file.
3. Run it: `uv run python Day-15-Prompt-Engineering-Management\example.py` (from the repository root).
4. Change only one input value or one short input sentence.
5. Predict the new route or output.
6. Run the same command again.
7. Write three short sentences: what you changed, what happened, and why.

**Rules:** keep the example in one Python file. Use LangGraph directly. Don't add a test folder or helper package. Don't replace `uv` commands with another package manager. Use the Windows Command Prompt commands shown above. Keep `MODEL = "gpt-oss:120b-cloud"` unchanged.

## Before You Move to Day 16

- [ ] The file runs without errors (Ollama is running locally with `gpt-oss:120b-cloud` available).
- [ ] You can name the state, the nodes, and the edges in this graph.
- [ ] You can explain who (or what) controls the next step, and which prompt version was actually used.
- [ ] You made one small change, predicted the effect first, then ran it and confirmed (or corrected) your prediction.
- [ ] You can write, in plain words, what you changed, what happened, and why.
