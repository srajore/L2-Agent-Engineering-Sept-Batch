# L2 Capstone Rubric

Maximum score: 100 points  
Suggested completion threshold: 70 points

| Area | Points | Full-credit evidence |
| --- | ---: | --- |
| Graph explanation | 15 | Correctly names START, nodes, routes, and END |
| Guardrail understanding | 20 | Explains the input filter, PII redaction and output check, and which are deterministic |
| Route tracing | 15 | Correctly predicts one allowed and one blocked request |
| Evaluation understanding | 20 | Explains guardrail accuracy vs. answer quality, the 1–5 judge score, and one weakness of an LLM judge |
| Managed vs framework guardrails | 10 | Names one use and one trade-off for AWS Bedrock Guardrails and for NeMo Guardrails |
| Code change | 10 | Adds one test case, predicts and explains the observed result |
| Delivery discipline | 10 | Uses `uv`, Windows Command Prompt, one Python file, and no test folder |

## Performance Levels

- **Strong: 85–100** — Runs the example and explains every decision without help.
- **Competent: 70–84** — Runs the example and explains both routes with minor prompts.
- **Developing: 50–69** — Runs part of the example but needs help tracing state or routing.
- **Incomplete: below 50** — Cannot run or explain the example safely.

## Critical Problems

- The learner cannot show a successful run.
- The blocked route is bypassed.
- Real credentials, AWS keys or private data are added to a file.
- A model-backed extension changes the required model from `gpt-oss:120b-cloud`.
- The learner claims this classroom example is production-ready.
