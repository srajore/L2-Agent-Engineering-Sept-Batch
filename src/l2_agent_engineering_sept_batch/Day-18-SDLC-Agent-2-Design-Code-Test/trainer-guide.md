# Session 18 Trainer Guide — SDLC Agent 2: Design → Code → Test

## Outcome

Learners direct Claude Code to build a development assistant, then **verify and accept or reject** it — with particular attention to whether AI-written tests can be trusted. They do not write or study code.

## Files to Use

- `START-HERE.html` / `START-HERE.md` — **the learner handout to give out and follow in class.** One file: concept, every prompt (copy buttons in the HTML), run command, tests, and an appendix with the extra tests and the hand-in sheet. The HTML is generated from the markdown: edit the `.md`, then rebuild the HTML.
- `CLAUDE-CODE-PROMPTS.md`, `CLAUDE-CODE-CONCEPTS.md`, `README.md` — fuller reference versions of the same material (optional for learners)
- `CLAUDE-CODE-PROMPTS.md` — learner working document: spec, prompts, plan checklist, acceptance tests, weak-tests check, break-it prompts, scope checks, acceptance sheet
- `README.md` — participant handout
- `_trainer-only\Day-18-SDLC-Agent-2-Design-Code-Test\example.py` — **your reference solution.** It is deliberately **not** in the learner folder, so Claude Code cannot copy it. Also the rescue file (see `IF-BUILD-FAILS.md`).
- `IF-BUILD-FAILS.md` — what learners do when a build or setup fails
- `slides.pptx` — classroom deck

## Setup in Windows Command Prompt

```cmd
uv sync
ollama signin
ollama launch claude --model nemotron-3-ultra:cloud
uv run python _trainer-only\Day-18-SDLC-Agent-2-Design-Code-Test\example.py
```

Type `yes` at approval. The reference file calls the model for tests and code, and again for each refinement.

## Claude Code Concepts Block (added): Hooks and Subagents

Learners follow `CLAUDE-CODE-CONCEPTS.md` first (about 30 minutes): the guard hook H1–H4, then the `agent-reviewer` subagent (A1, A2) at introduction level. `_trainer-only\Day-18-SDLC-Agent-2-Design-Code-Test\trainer-reference\` holds the working files (`hooks\guard.py`, `settings.hooks.json`, `active-day.txt`, `agents\agent-reviewer.md`).

Verified while preparing this session (Claude Code 2.1.266 on Windows):

- A `PreToolUse` hook with matcher `Edit|Write` and `exit 2` blocked an edit to `example.py` and a write into another day's folder, each with the guard's message, and allowed a normal write.
- The hook command in the reference uses `uv run python .claude/hooks/guard.py` so it works without `python` on the PATH. Settings load at session start, so learners must **restart `claude`** after the hook is registered.
- The guard script reads stdin as UTF-8 with a possible BOM, because PowerShell pipes can add one.
- The read-only subagent (`tools: Read, Grep, Glob`) reviewed a stub file and returned findings. Subagent calls may ask for permission in headless mode; interactively learners just approve.
- The guard blocks `example.py` and `chain.py` in **every** day folder, so it must not be switched on before Day 16's lab (which edits Day 16's `example.py`).

Teaching point: ask learners which of rule, deny rule and hook they would use for "never edit the answer key". Deny rules fit fixed paths; hooks fit logic ("any day except today's").

Time note: the session is now planned as 100 minutes following `START-HERE`; deeper tests are optional practice after class (see the flow below).

## Suggested 100-Minute Flow (follows START-HERE)

1. **0-10 — Recap and teach, Introduce:** tests first, independent execution, the vacuous pass, the weak-tests idea.
2. **10-20 — Plan review, Practise:** Prompt 1 in plan mode; checklist; send back plans that run code in-process or skip the timeout.
3. **20-35 — Build and run, Practise:** Prompt 2; learners run `my_agent2.py` themselves in a second Command Prompt window.
4. **35-50 — Acceptance tests B1, B2, B4, B5, B6, Practise.**
5. **50-62 — Weak-tests check, Practise.** Never skip this.
6. **62-72 — Break-it, Practise:** fake tests, then always-wrong code (3 attempts then stop).
7. **72-95 — Claude Code feature, Practise:** the guard hook (H1 to H4). Set `active-day.txt`; restart `claude` after the hook is registered. The agent is already running by now.
8. **95-100 — Decision.**

### Optional practice after class (about 45 minutes)

The `agent-reviewer` subagent (A1 to A4), hook H5 and H6, B3, the infinite-loop break-it, scope checks, the acceptance sheets, and the assignment (different function). All are in the appendix of `START-HERE`. The subagent moved out of class time to fit 100 minutes.

## Live build test (done 2026-10-03, real Claude Code)

> **Model caveat:** this test used a Claude model. Participants will use `gemma4:cloud` through Ollama, which I have not tested. Pilot the Day 18 build and hook prompts on `gemma4:cloud` before class.

Prompts 1 and 2 were pasted into Claude Code in a **learner copy** (no `_trainer-only`, no trainer guides). The result was then tested by hand as a learner would.

- **Plan time:** about 1.5 minutes with the "short plan (under 15 lines), no research helpers" line. (Earlier Day 17 runs without that line took 8 and 23 minutes.)
- **Plan:** met every checklist item (tests before code, subprocess with a 15-second timeout, a check that tests do not define the function and have 4+ asserts, retry limit 3 with a stop route, a human approval step, one file, no pytest or LangChain).
- **Build:** one `my_agent2.py`, no extra files. Approval was a plain `input()` rather than `interrupt`; the spec allows either.
- **Acceptance:** B1 (tests and code generated, `ALL TESTS PASSED`, approved), B2 (tests cover valid, exactly at balance, over balance, end before start), B3 (no `def validate_leave_request` in the tests), B4 (`no` gives rejected) and all scope checks passed.
- **Weak-tests check:** with the end-before-start rule removed, the generated tests failed; with the balance rule removed, they failed too. So these tests do protect the code.
- **Not run live:** the three break-it prompts and the subagent tests. The reference solution handles them; run them in your pilot.

### Concepts block, run live

- **Hook prompt:** Claude Code created `active-day.txt`, `guard.py` and the `settings.json` entry (event `PreToolUse`, matcher `Edit|Write`, command `uv run python .claude/hooks/guard.py`). Tested live: a normal file in today's folder was created (H2); creating `example.py` there was refused with the guard's message (H3); creating a file in the Day 17 folder was refused with "active day is Day-18-..." (H4). The wording of the messages differs from the reference script, which is fine: the test looks for a refusal that says why.
- **Subagent prompt:** the file matched the spec (tools `Read, Grep, Glob`, model `sonnet`, ends with `REVIEWER: DONE`).
- **`.claude` writes need an approval prompt** (see the Day 17 guide). Settings changes load only when a session starts, so learners must restart `claude` after the hook is registered.
- The weak-tests check was run by hand: both mutated copies of the generated code were caught by the generated tests.

Things to expect: Claude Code will not run the program for the learner (it cannot type `yes` and the shell asks permission), so the prompts tell learners to run it in a second Command Prompt window.

## Pilot on the Ollama models (2026-10-04): expect first builds to fail

Prompts 1 and 2 were run headless in a fresh learner copy through `ollama launch claude --model <model> -y -- -p "..."`.

- `gpt-oss:120b-cloud`: the first `my_agent2.py` had a `SyntaxError`. After the `py_compile` line was added to Prompt 2 it compiled but crashed when run (`NameError: name 'reason' is not defined`). Not yet repaired by a fix message.
- `gemma4:cloud`: built the whole shape (tests, test data, code, validate, refine, explain) and ran to the explanation. The explanation was a jargon-heavy table about a "`leave.py` module", so B6 (plain English, no jargon) is doubtful. B1 to B5 not checked.
- A compile check does not catch undefined names. Learners still run the agent themselves and use B1 to B6 and the weak-tests check as the real verdict.
- Use the fail-page loop: name the test, send one short message, rerun all B tests. Keep `_trainer-only` rescue ready.

## Verification run 2026-10-05 (reference solution, `gpt-oss:120b-cloud`)

Run from `_trainer-only` with `echo yes |` / `echo no |`:

- `yes`: code generated, 5 asserts, a 6-case test-data table, a plain-English explanation printed before the question, `Validation after 1 attempt(s): ALL TESTS PASSED`, `Status: Code and tests approved`.
- `no`: `Status: Stopped: human rejected the code`.

This checks the **reference** only. The learner-built `my_agent2.py`, the hook and the weak-tests check were not rerun in this session.

### Prompt change 2026-10-05

"Read CLAUDE.md." was removed from the start of Prompt 1 (the constraints are already in the prompt) in `START-HERE.md` and `CLAUDE-CODE-PROMPTS.md`. Not piloted live: try it before class. H6 now reads `pyproject.toml` instead of a Day 16 file, so the day has no dependency on Day 16.

### Live learner-flow test 2026-10-06 (`gpt-oss:120b-cloud` through `ollama launch claude`, headless, clean learner copy)

Method: a learner copy without `_trainer-only`, Prompt 1 then Prompt 2 as a continuation (`-c`), the built file run with `echo yes |` and `echo no |`, then short learner-style fix messages. The Claude Code features were tested with permissions bypassed in a throwaway copy.

Prompt hardening that came out of this test (already applied in `START-HERE.md` and `CLAUDE-CODE-PROMPTS.md`): the model got the LangGraph API wrong (dict as state schema, wrong `add_conditional_edges` arguments, `from langgraph.checkpoint import InMemorySaver`), so Prompt 1 now carries a short "LangGraph facts" block; builds that compiled but printed nothing, so Prompt 1 now says exactly what the file prints when run. Expect to re-check these two additions in your own pilot.

Results for Day 18: this is the day that works. After the hardening, a first build passed B1 (code, 5 asserts, a 6-case test-data table, plain-English explanation before the question, `ALL TESTS PASSED`, `Status: Code and tests approved`) and `no` gave `Status: Stopped: human rejected the code`; scope checks passed except that a prompt string inside the agent said "No pytest", which `findstr` flags (false alarm, now explained in the guide). Before the hardening, builds compiled but ended in "All attempts exhausted" and a fix round did not repair it. The weak-tests prompt produced a plausible broken-copy run, but the transcript looked simulated rather than run: have learners ask for the real output.

Hook: the original free-text hook prompt produced an invalid `settings.json` (it even copied entries from the user's own settings), a guard that read the wrong JSON field, and once timed out. The hook prompt now gives the exact text of all three files (as the skill prompt does). Verified: `settings.json` is valid JSON, `guard.py` is identical to the prompt, and run by hand it exits 2 for `example.py`, for `chain.py`, and for a file in another Day folder, and 0 for today's folder. **Not verified: Claude Code actually firing the hook.** In headless `-p` runs (with and without `--settings`) the blocked writes still happened, so check H1 to H4 interactively on your machine, including the trust dialog, before class. The `agent-reviewer` subagent file was created with only Read, Grep, Glob (A1 pass); A2 to A4 not run.

**Bottom line for class (gpt-oss as Claude Code model):** with `gpt-oss:120b-cloud` as the Claude Code model, treat each learner build as likely to need two or three fix rounds, and plan the rescue (`_trainer-only` reference, "used rescue" on the sheet) from the start. A stronger model for Claude Code, if you can use one, will change these results: re-run this test with it.

### Re-test with a stronger Claude Code model, 2026-10-06: `nemotron-3-ultra:cloud`

Model choice: the Ollama cloud models retired earlier (qwen3-coder, deepseek-v3.1, kimi-k2, glm-4.6, minimax-m2) answer "retired"; the newer ones (kimi-k3, kimi-k2.7-code, glm-5.3, glm-5.2, deepseek-v4-pro, minimax-m3) answer "not in the Free plan". On the free plan the strongest working option was `nemotron-3-ultra:cloud` (also `nemotron-3-super`, `gemma4:31b-cloud`, `gpt-oss:20b-cloud`). Same method as the gpt-oss test above: clean learner copy, Prompt 1 then Prompt 2 with `-c`, built file run with `yes` and `no`. The built agents still call `gpt-oss:120b-cloud`; only Claude Code's model changed. The learner docs now start Claude Code with `ollama launch claude --model nemotron-3-ultra:cloud` and ask learners to check both models in "Before you start".

One prompt bug surfaced and was fixed (it also explains the gpt-oss failures where `yes` was treated as `no`): the model wrote `interrupt("...")` as a bare call and ignored its return value, so `approved` was never set. The "LangGraph facts" block now says to store it: `approved = interrupt("question")`, then route on state. Prompt 1 on Day 19 now also requires a clean sample pull request (no TODO, eval, exec, os.system or bare pass), because one build invented a flawed diff and was Blocked every run.

Day 18 result on nemotron-3-ultra: the first build passed B1 (code, tests, 6-case test-data table, explanation, `Validation after 1 attempt(s): ALL TESTS PASSED`, `Status: Code and tests approved`) and B4 (`no` gave `Status: Stopped: human rejected the code`); one file, no LangChain or pytest, subprocess present, no eval or exec. The program prints nothing until it finishes, and one run needed several minutes, so tell learners to wait. Not re-run on this model: the weak-tests check, the three break-it prompts, B2/B3/B5/B6 by eye.

Hook and subagent on nemotron-3-ultra: the hook prompt produced `active-day.txt`, `guard.py` (identical to the prompt text) and a valid `settings.json`; the subagent file was created with `tools: Read, Grep, Glob` (the always-on rule also added a `# AGENT FILE` line to it, harmless). **The hook still did not fire in any headless run** (H3 and H4 files were created, with and without `--settings` and `--setting-sources`), although run by hand the guard exits 2 for `example.py`, `chain.py` and another Day's folder. Verify H1 to H4 interactively on your machine before class, including the trust dialog; if the hook never fires there either, the likely suspects are the hook command or its PATH (`uv run python ...`), so try `python .claude/hooks/guard.py` in `settings.json`.

**Bottom line (updated):** use `nemotron-3-ultra:cloud` as Claude Code's model; with it each day's agent and the chain worked with at most one short fix round in this test. `gpt-oss:120b-cloud` as Claude Code's model mostly did not (see the gpt-oss test above). Learners on a different Ollama plan may not have the same models, so have everyone run `ollama run nemotron-3-ultra:cloud` in the pre-class check. Keep the `_trainer-only` references as the rescue.

## Reference Answers (for the trainer)

- The reference build passes B1–B6. B5 (test-data table, validated and run against the code) and B6 (plain-English code explanation) were added on 2026-10-04 to cover the use case's test-data generation and code explanation. Test data with an unreal date such as 2023-02-30 is accepted only in a case that expects "invalid". In the weak-tests check, removing the `end < start` rule makes at least one reference test fail; if a learner's tests all pass on the broken copy, their tests are weak and they should reject.
- Break-it results: fake tests are rejected (the agent retries the tests); always-wrong code gives exactly 3 attempts then a stop; an infinite loop ends with a timeout message after about 15 seconds.
- Scope checks: only `my_agent2.py` added; no `langchain` or `pytest`; `subprocess` and `timeout` found; no `eval(` or `exec(`.

## Questions to Ask Learners

1. Why are the tests written before the code?
2. What does "ALL TESTS PASSED" prove, and what does it not prove?
3. How did your weak-tests check turn out, and what did you ask Claude Code to do about it?
4. What stopped the infinite loop?

## Common Mistakes (observed while testing)

- The first reference build produced tests that redefined the function and passed trivially. This is the best teaching moment of the day.
- Exact-match assertions on error text make tests fail for the wrong reason; the prompt tells the model to assert only the first value.
- Learners let Claude Code run generated code inside their own process. Reject that plan.
- Markdown fences left in generated code cause a `SyntaxError`.
- Output differs each run; verify behaviour, not wording.
- Learners skip the weak-tests check because the run is green. Make it mandatory.

## Exit Check

Each learner shows a filled acceptance sheet, including the weak-tests result, and a one-sentence decision.
