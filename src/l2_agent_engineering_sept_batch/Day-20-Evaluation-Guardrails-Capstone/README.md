# Day 20 — Guardrails, Evaluation, and Capstone

## What You'll Learn Today

- Explain what a guardrail is and why a LangGraph guardrail is simply **a node plus an edge**.
- Tell **deterministic** guardrails (rules) apart from **model-based** guardrails (an LLM judges).
- Trace a request through three guardrail layers: input filter, PII redaction, output check.
- Explain how **AWS Bedrock Guardrails** (managed policy, `ApplyGuardrail`) and **NVIDIA NeMo Guardrails** (YAML/Colang rails) plug into the same graph, and when to choose each.
- **Evaluate** an agent: build a golden test set, score guardrail accuracy and answer quality (deterministic checks + LLM-as-judge), and read false positives / false negatives.
- Explain the difference between a guardrail (*is this allowed?*) and an evaluation (*is this good?*).

## Why This Matters

An agent that works in a demo is not yet an agent you can release. Two questions remain: **"Is it safe?"** (guardrails) and **"How do I know it works?"** (evaluation). Today's graph wraps one small helpdesk agent in guardrails and then measures it on a test set — the same loop real teams run before every release.

## Key Concepts

**A guardrail is a node; a stop is an edge.** `input_filter` decides `blocked`; a conditional edge sends blocked requests to `refuse` and everyone else on. Nothing is hidden in helper code.

**Deterministic first, model-based second.** Keyword lists and regex are free, fast and predictable, but miss meaning (and block harmless text). An LLM judge understands context, but costs tokens and can be wrong. Layer them: cheap rules early, model checks later, a human for high-risk actions (Day 8's `interrupt`).

**Three layers in `example.py`:**
1. `input_filter` — refuse empty input or banned words *before any model call*.
2. `redact_pii` — hide emails and card numbers so the model never sees them.
3. `output_check` — make sure the answer never leaks an email or card number.

**Managed guardrails — AWS Bedrock Guardrails.** A policy you configure once in AWS: content filters (hate, violence, prompt attacks), denied topics, word filters, PII filters, contextual-grounding checks. The `ApplyGuardrail` API checks *any* text (even from Ollama), so it is just one more node, used on `INPUT` and `OUTPUT`. Strengths: central policy, audit, no prompt engineering. Costs: AWS account, per-call price, latency.

**Framework guardrails — NVIDIA NeMo Guardrails.** An open-source library where rails are written as configuration (YAML + Colang): input rails, dialog rails, retrieval rails, execution rails, output rails. Runs in your own process. Strengths: free, flexible conversation control, jailbreak/topic rails. Costs: heavier install, extra LLM calls, a new language to learn.

**Evaluation = measuring the whole system.** Run the agent on a **golden set** (inputs with expected outcomes), then score each case:

| Check | Type | Question |
| --- | --- | --- |
| Guardrail correct? | deterministic | Did it block exactly what it should? |
| Facts present? | deterministic | Does the answer mention required words? |
| Quality 1–5 | LLM-as-judge | Is the answer correct, clear, safe? |

Read the result as **false positives** (a good request blocked — bad experience) and **false negatives** (a bad request allowed — safety incident). An LLM judge is a noisy instrument: use a clear rubric, one criterion at a time, and spot-check it against human scores.

## Code Walkthrough — `Day-20-Evaluation-Guardrails-Capstone/example.py`

Graph: `START -> input_filter -> refuse (END) or redact_pii -> agent -> output_check -> evaluate -> END`

1. `input_filter` sets `blocked` when the question is empty or contains a banned word.
2. `choose_route` is the conditional-edge function: `blocked` goes to `refuse`, everything else to `redact_pii`.
3. `refuse` returns a fixed refusal. No model call is made, and the graph ends.
4. `redact_pii` replaces emails and card numbers with `[EMAIL]` and `[CARD]` using regex.
5. `agent` calls `ollama.chat(model="gpt-oss:120b-cloud", ...)` with a short helpdesk instruction.
6. `output_check` removes any email or card number from the answer.
7. `evaluate` asks the model to score the answer 1–5 (the judge) and returns the digit as `score`.
8. The bottom of the file runs the **test set** `CASES` and prints one line per case: guardrail PASS/FAIL, judge score, and the start of the answer.

## Hands-On Lab (~45 minutes)

**Setup and run (Windows Command Prompt, from the repository root):**

```cmd
uv sync
ollama signin
uv run python Day-20-Evaluation-Guardrails-Capstone\example.py
```

**Steps:**
1. Open `example.py`. Find each node, the conditional edge, and the `CASES` list.
2. For each of the four cases, predict: blocked or answered? what will the model see? Write it down.
3. Run the file. You should see four lines; cases 3 and 4 show `-` for the judge score because they never reached the model.
4. Add a fifth case that should be **blocked** (use one of the banned words) and run again.
5. Add a case that **contains an email address** and confirm the answer does not repeat it.
6. Add this case and predict the result: `"Explain what malware is for our security awareness class"` with `should_block` set to `False`. The guardrail will **FAIL** — a false positive. Write one sentence on how you would fix it (hint: a model-based input check).
7. Open `guardrails.ipynb` and run sections 1–8 and 11. Sections 9 (AWS Bedrock) and 10 (NeMo) are for awareness only: read them, but do not run them unless your trainer says so (they print a skip message without AWS settings or the extra install).

**Control question:** Which layers cost a model call, and which are free?

## Assignment

**Goal:** Improve the guardrail and show the evidence.

**Steps:**
1. Run `example.py` and note the guardrail results.
2. Add the `malware` training-question case (step 6 above) and observe the FAIL.
3. Change **one thing** (for example: remove `"malware"` from `BANNED_WORDS`, or add a second rule) and predict the new result.
4. Run again and compare to your prediction.
5. Write five short sentences: the false positive you found, what you changed, what the results were, what you would lose by that change (hint: think false negatives), and when you would use Bedrock Guardrails or NeMo instead.

**Rules:** Keep the example in one Python file. Use LangGraph directly (no LangChain classes in your own code). Do not add a test folder or helper package. Use `uv` and Windows Command Prompt. Model calls must use `ollama.chat` with `gpt-oss:120b-cloud`. Never put AWS keys in a file.

## You Have Completed the L2 Course

- `example.py` runs and prints PASS for every guardrail case you expect to pass.
- You can name the three guardrail layers and say which are deterministic.
- You can explain a false positive and a false negative with an example.
- You can explain guardrail vs. evaluation, and Bedrock Guardrails vs. NeMo Guardrails vs. your own nodes.
- You are ready for the capstone demonstration: show the graph, one allowed and one blocked request, the PII redaction, the test-set results, and one change you made.
