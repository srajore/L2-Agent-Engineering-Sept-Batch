# Session 20 Trainer Guide — Guardrails, Evaluation, and Capstone

## Outcome

By the end of the session, a learner can run one file, explain its three guardrail layers, read its evaluation results (including a false positive), and say when to use AWS Bedrock Guardrails or NeMo Guardrails instead of hand-written nodes.

## Files to Use

- `example.py` — the only graded code file (needs `ollama signin`)
- `guardrails.ipynb` — the guided notebook: sections 1–8 guardrails in LangGraph, 9 AWS Bedrock Guardrails, 10 NeMo Guardrails, 11 evaluations
- `slides.pptx` — the classroom deck (15 slides: guardrails, layers, Bedrock/NeMo awareness slide, evaluation, code, lab, assignment)
- `README.md` — the participant handout
- `assessment\` — capstone brief, rubric, and golden cases

Do not create a test folder or extra helper modules.

## Setup in Windows Command Prompt

```cmd
uv sync
ollama signin
uv run python Day-20-Evaluation-Guardrails-Capstone\example.py
```

Expected: four lines, all `PASS`, judge scores of 4–5 for cases 1–2 and `-` for the blocked cases 3–4.

### Optional extras (awareness only; the slides just introduce Bedrock and NeMo, no live demo needed)

- **AWS Bedrock Guardrails (notebook section 9):** needs an AWS account. Create a guardrail in the Bedrock console, then set `BEDROCK_GUARDRAIL_ID`, `BEDROCK_GUARDRAIL_VERSION`, `AWS_REGION` and AWS credentials, and run `uv add boto3`. Without them the notebook prints "Bedrock skipped" and continues — demo the console and show the `apply_guardrail` call instead. **Not live-tested** (no AWS account available during authoring); the API shape follows the boto3 `bedrock-runtime` `apply_guardrail` reference.
- **NeMo Guardrails (notebook section 10):** `uv add nemoguardrails langchain-ollama` (large install; NeMo uses LangChain internally, learners write none). Live-tested with `gpt-oss:120b-cloud`: the allowed question is answered and the hacking question returns "I'm sorry, I can't respond to that." Not added to `pyproject.toml`, so the default `uv sync` stays light.

## Suggested 120-Minute Flow

1. **10 minutes — Why:** An agent that demos well is not releasable. Two questions: is it safe, and how do we know it works?
2. **20 minutes — Guardrails:** Deterministic vs model-based; guardrail = node + edge. Walk the `example.py` graph.
3. **20 minutes — Run and predict:** Learners predict each case, then run. Cover the PII redaction.
4. **15 minutes — Managed and framework guardrails:** Notebook sections 9–10 and the comparison table. Bedrock = managed policy via `ApplyGuardrail`; NeMo = YAML/Colang rails in your process.
5. **25 minutes — Evaluation:** Notebook section 11: golden set, deterministic checks, LLM-as-judge, false positives/negatives. Let learners find the `malware` false positive.
6. **20 minutes — Change:** Lab steps 4–6 / the assignment.
7. **10 minutes — Capstone demo prep:** Use `assessment\final-capstone.md` and `rubric.md`.

## Code Walkthrough Questions

1. Which nodes are deterministic and which call a model?
2. Why does a blocked request skip `agent` and `evaluate`?
3. What does the model actually see when the question contains an email?
4. Why can a judge score of 5 still not prove the agent is safe?
5. If we remove `"malware"` from `BANNED_WORDS`, what do we gain and what could go wrong?

## Common Mistakes

- Forgetting `ollama signin` (the file now makes model calls)
- Treating the LLM judge's score as ground truth
- Confusing a guardrail (before/around the work) with an evaluation (measuring many cases)
- Putting AWS keys in a file instead of environment variables
- Expecting the Bedrock or NeMo cells to run without their setup (they skip by design)
- Adding framework helpers that are not used in `example.py`

## Exit Check

The learner can point to each guardrail layer, name the route a blocked request takes, explain one false positive, and state one trade-off for Bedrock Guardrails and for NeMo Guardrails.

## Known Limitations

- The judge and the agent use the same model; real evaluations prefer a different or stronger judge and human spot-checks.
- The test set is tiny (a teaching size). Real sets hold 20–50+ cases drawn from real traffic.
