# Final L2 Capstone

## Objective

Demonstrate the guardrail-and-evaluation graph, explain each layer, and show evidence of how well it works.

## Files

- `Day-20-Evaluation-Guardrails-Capstone\example.py` — the only capstone code file
- `Day-20-Evaluation-Guardrails-Capstone\guardrails.ipynb` — the guided notebook (LangGraph guardrails, AWS Bedrock Guardrails, NeMo Guardrails, evaluations)
- `Day-20-Evaluation-Guardrails-Capstone\assessment\golden-cases.json` — five test cases with the expected outcome
- `Day-20-Evaluation-Guardrails-Capstone\assessment\rubric.md` — scoring guide

Do not create a test folder or extra helper modules.

## Run in Windows Command Prompt

From the repository root:

```cmd
uv sync
ollama signin
uv run python Day-20-Evaluation-Guardrails-Capstone\example.py
```

## Tasks

1. Draw the graph: `START -> input_filter -> refuse or redact_pii -> agent -> output_check -> evaluate -> END`.
2. Mark which nodes are deterministic guardrails and which node uses a model.
3. Predict the PASS/FAIL and judge score for each case in the `CASES` list before running.
4. Run the command and compare.
5. Add one new case to `CASES` (one that should be blocked, or one containing an email), predict the result, then run.
6. Read notebook sections 9 and 10 (Bedrock and NeMo). They are awareness only; run them only if your trainer provides AWS access / the extra install.
7. Restore the original `CASES` list.

## Five-Minute Demonstration

1. Show the graph and name each guardrail layer.
2. Trace one allowed request and one blocked request.
3. Show that an email or card number is hidden before the model sees it.
4. Explain how the judge produces a 1–5 score and why it is only one kind of evidence.
5. Show your added test case and its observed result.
6. Explain when you would use AWS Bedrock Guardrails or NeMo Guardrails instead of your own nodes.
7. Name one limitation (for example: keyword rules block harmless text).

## Completion Criteria

- `example.py` runs successfully and prints a PASS for every guardrail case.
- The learner explains both graph routes and the three guardrail layers.
- The learner distinguishes a guardrail (is this allowed?) from an evaluation (is this good?).
- The learner can name one trade-off each for hand-written guardrails, Bedrock Guardrails and NeMo Guardrails.
- The learner uses LangGraph directly and keeps the example in one file.
- Any model call uses `ollama.chat` with `gpt-oss:120b-cloud`.
