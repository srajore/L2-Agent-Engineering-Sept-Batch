# Session 19 Trainer Guide — SDLC Agent 3: Review → Release, and the Agent Chain

## Outcome

Learners direct Claude Code to build a review/release agent and then a chain connecting all three agents. They **verify and accept or reject** both using acceptance tests. They do not write or study code.

## Files to Use

- `START-HERE.html` / `START-HERE.md` — **the learner handout to give out and follow in class.** One file: concept, every prompt (copy buttons in the HTML), run command, tests, and an appendix with the extra tests and the hand-in sheet. The HTML is generated from the markdown: edit the `.md`, then rebuild the HTML.
- `CLAUDE-CODE-PROMPTS.md`, `CLAUDE-CODE-CONCEPTS.md`, `README.md` — fuller reference versions of the same material (optional for learners)
- `CLAUDE-CODE-PROMPTS.md` — learner working document: specs, prompts, plan checklists, gate tests, chain tests, scope checks, acceptance sheet
- `README.md` — participant handout
- `_trainer-only\Day-19-SDLC-Agent-3-Review-Release\example.py` — **reference for Agent 3** (deliberately not in the learner folder, so Claude Code cannot copy it; also the rescue file)
- `IF-BUILD-FAILS.md` — what learners do when a build or setup fails
- `_trainer-only\Day-19-SDLC-Agent-3-Review-Release\chain.py` — **reference for the chain** (all three agents as subgraphs of one parent graph, self-contained). A second runnable file for this day is a deliberate exception to the one-file rule, because agent-to-agent communication cannot be shown with one agent.
- `slides.pptx` — classroom deck

## Setup in Windows Command Prompt

```cmd
uv sync
ollama signin
ollama launch claude --model nemotron-3-ultra:cloud
uv run python _trainer-only\Day-19-SDLC-Agent-3-Review-Release\example.py
uv run python _trainer-only\Day-19-SDLC-Agent-3-Review-Release\chain.py
```

`chain.py` makes at least 6 model calls and needs three `yes` answers. Allow several minutes.

## Claude Code Concepts Block (added): Integration and Headless Mode

Learners follow `CLAUDE-CODE-CONCEPTS.md` alongside the labs: the guard hook (H1–H4) and the read-only subagent (SA1–SA4) are built in class today, then integration tests I1–I5, headless tests P1–P2, and the 13-row driver's check. Everything from Days 16–19 must work together. They set `.claude\active-day.txt` to the Day 19 folder first.

**Headless mode:** the form `ollama launch claude --model gpt-oss:120b-cloud -y -- -p "..." --allowedTools "Bash,Read"` was confirmed in the 2026-10-04 pilot (see below). Other claims in this section were first verified with a Claude model, so pilot on your own machine. If it fails for a learner, have them run `/accept-check` inside a normal session.

Verified while preparing this session (Claude Code 2.1.266 on Windows): `claude -p "/accept-check <file>" --allowedTools "Bash,Read"` runs a skill headlessly and prints the table and decision. In headless mode nothing can ask permission, so tools must be listed in `--allowedTools`.

Use the driver's check as the end-of-block assessment: each ticked row needs proof (output, file or message).

Time note: the session is now planned as 100 minutes following `START-HERE`; deeper tests are optional practice after class (see the flow below).

## Suggested 100-Minute Flow (follows START-HERE)

Day 18 ran out of time before hooks and subagents, so Day 19 opens with the guard hook (H1 to H4) and adds the read-only subagent (SA1 to SA3) after Agent 3 is built. The hook prompt sets `active-day.txt` to the Day 19 folder from the start, so nothing needs changing later. If a learner already built the Day 18 guard, they only need to change `active-day.txt`.

1. **0-5 — Recap and teach, Introduce:** finding vs gate vs approval; verification debt; subgraphs and handoffs.
2. **5-25 — Guard hook, Practise:** plan mode, approve, restart Claude Code, tests H1 to H4. If it is not working by minute 25, drop it (nothing later depends on it) and move on.
3. **25-41 — Agent 3, Practise:** plan (Prompt 1), build (Prompt 2), run it yourselves.
4. **41-49 — Read-only subagent, Practise:** plan mode, approve, restart Claude Code, `/agents`, tests SA1 to SA3 (review `my_agent3.py`; SA3 proves it cannot edit). If it is not working by minute 49, drop it and move on (nothing later depends on it); SA3 and SA4 can go to homework. The prompt omits the `model` line, so the subagent uses the session model; not yet piloted on Ollama.
5. **49-57 — Agent 3 tests, Practise:** C1, C2, C7, C8 from real runs (check C7 and C8 during the C1 run); C4 and C5 as simulated gates.
6. **57-72 — Chain, Practise:** first check that each learner's `my_agent1.py` and `my_agent2.py` run (give a working copy if not), then plan (Prompt 3), build (Prompt 4), run it yourselves.
7. **72-82 — Chain tests D1 to D4, Practise.**
8. **82-90 — Headless mode (P1) and the driver's check, Introduce.**
9. **90-100 — Decisions for Agent 3 and the chain.**

### Optional practice after class (about 45 minutes)

C3, C6, C9, D5, SA4, I5, P2, finishing the driver's check with proof for each row, the acceptance sheets, and the extra-gate assignment. All are in the appendix of `START-HERE`. The driver's check is the course's Claude Code assessment: review it before Day 20.

## Live build test (done 2026-10-03, real Claude Code)

Prompts 1–4 were pasted into Claude Code in a learner copy (with `my_agent1.py` and `my_agent2.py` already built from the Day 17 and 18 prompts). Each plan took about 3 minutes with the "short plan" line.

- **Agent 3 plan and build:** met every checklist item (gates are plain Python; unreadable review becomes one HIGH finding; a blocked route skips the notes; approval comes after the notes; one file). The built agent uses `interrupt` with a checkpointer. Its changelog and release notes are templated from the findings rather than written by the model, which the spec allows.
- **Gate tests:** with a stubbed clean review, release succeeded; with `tests_passed` False, with `eval(` in the code, with a HIGH finding and with a review of the text `hello`, release was blocked each time and **no release notes were printed**.
- **C1 and C2 with the real model:** the reviewer called a missing validation HIGH, so the agent blocked. This is the documented model variance: C1 and C2 can legitimately end in Blocked, and then the `no` path is not reached. Use a re-run, or the stubbed review, to show the approval step.
- **Chain build:** one self-contained `my_chain.py`, no imports from other files, no LangChain; three subgraphs, two handoff nodes, stop rules after Agents 1 and 2, one checkpointer and a loop on interrupts.
- **Chain tests:** D1 (`yes, yes, yes`) ended Released with a handoff list of exactly two entries (D4: no duplicates). D2 (`yes, no`) ended Stopped in Agent 2 with no Agent 3 output. D3 (`no`) ended Stopped in Agent 1 with nothing after it. D5 (is the function about the leave request?) matched.
- **Quirk:** the stories are printed twice at Agent 1's approval because the node re-runs when the graph resumes. Cosmetic: tell learners not to reject for it.
- **Ollama must be running.** During this test it had stopped; the failure shows as `ConnectionError: Failed to connect to Ollama`. Check it before class.

## Pilot on the Ollama models (2026-10-04): expect first builds to fail

Prompts 1 to 4 were run headless in a fresh learner copy through `ollama launch claude --model <model> -y -- -p "..."`, with the built files run afterwards.

- `gpt-oss:120b-cloud`: Agent 3 first came out as one escaped string (`SyntaxError`); with the `py_compile` line it ran and printed the PR state, but not the readable review layout. The chain planned to load the other agents with `exec` (against the "one self-contained file" rule; the plan checklist catches this) and crashed with `NameError: name 'agent1_path' is not defined`.
- `gemma4:cloud`: Agent 3 crashed when run. The chain printed **"Released Successfully" with `Handoffs: []`**: no agent ran, yet it claimed success. This is exactly what D1 (output shows stories, then code, then gates) and D4 (two handoff entries) exist to catch. Use it as the class example of why a printed success is not evidence.
- The `py_compile` check does not catch undefined names or empty runs. Learners must run the agent and chain themselves and judge by C1 to C8 and D1 to D4.
- Verified: `ollama launch claude --model gpt-oss:120b-cloud -y -- -p "..."` works headless, so the Day 19 headless step (P1) is confirmed for `gpt-oss`; allowed tools must still be listed with `--allowedTools`.
- Plan the 100 minutes with a fix loop in mind: if a build is not working after 2 fix messages, use the rescue file and write "used rescue" on the sheet.

## Verification run 2026-10-05 (reference solutions, `gpt-oss:120b-cloud`)

Run from `_trainer-only` with piped answers:

- Agent 3 `yes`: `Reviewing PR: Add leave request validation`, 3 findings that each quote the added line (1 MEDIUM, 2 LOW), 3 gates PASS, verification debt listed, changelog, release notes, documentation with all four headings printed before the question, `Status: Released`.
- Agent 3 `no`: `Status: Stopped: human declined the release`.
- Chain `yes, yes, yes`: ends `Released`; handoff log has exactly 2 entries (Agent 1 to Agent 2, Agent 2 to Agent 3).
- Chain `no` at Agent 1: `Final status: Stopped in Agent 1`, no Agent 2 or 3 output.
- Chain `yes, no`: `Final status: Stopped in Agent 2`, no Agent 3 output.

This checks the **references** only. Learner-built `my_agent3.py` and `my_chain.py`, the simulated gate failures (C3 to C6, C9) and the headless run were not rerun in this session.

### Prompt change 2026-10-05

"Read CLAUDE.md." was removed from Prompt 1, and `InMemorySaver` / `Command(resume=...)` were named in the approval constraint, in `START-HERE.md` and `CLAUDE-CODE-PROMPTS.md`. Not piloted live. The `START-HERE` headless command is now `ollama launch claude --model nemotron-3-ultra:cloud -y -- -p "..." --allowedTools "Bash,Read"`, the form the 2026-10-04 pilot confirmed.

### Live learner-flow test 2026-10-06 (`gpt-oss:120b-cloud` through `ollama launch claude`, headless, clean learner copy)

Method: a learner copy without `_trainer-only`, Prompt 1 then Prompt 2 as a continuation (`-c`), the built file run with `echo yes |` and `echo no |`, then short learner-style fix messages. The Claude Code features were tested with permissions bypassed in a throwaway copy.

Prompt hardening that came out of this test (already applied in `START-HERE.md` and `CLAUDE-CODE-PROMPTS.md`): the model got the LangGraph API wrong (dict as state schema, wrong `add_conditional_edges` arguments, `from langgraph.checkpoint import InMemorySaver`), so Prompt 1 now carries a short "LangGraph facts" block; builds that compiled but printed nothing, so Prompt 1 now says exactly what the file prints when run. Expect to re-check these two additions in your own pilot.

Results for Day 19: Agent 3 ran after the hardening but was not clean: it printed the findings, gates and documentation headings, but a failed gate (HIGH finding) still ended `Status: Released` (C5 would fail), the PR title printed twice (known cosmetic quirk), and the changelog and release notes were empty. `no` gave `Status: Stopped: human declined the release`. Earlier builds failed with `ImportError: InMemorySaver` and with a `SyntaxError` that survived two fix rounds while the model claimed "it compiles" without showing the check. The chain, built on top of known-good agents, failed twice: first it printed nothing (no interrupt loop), then after the loop was added to Prompt 3 it crashed with `ValueError: Found edge starting at unknown node 'validate'`. Treat the chain as a trainer demo with `_trainer-only/Day-19.../chain.py` unless your own pilot says otherwise. The headless accept-check command and the gate simulations (C3 to C6, C9) were not re-run.

Slides: `slides.pptx` for Days 17 to 19 were edited on 2026-10-06 (100-minute plan, no Day 16 or CLAUDE.md wording, new order: build the agent first, Claude Code feature second) and rendered in PowerPoint to check the changed slides. Originals are in _pre-claude-code-agents-backup/slides-before-2026-10-06.

**Bottom line for class (gpt-oss as Claude Code model):** with `gpt-oss:120b-cloud` as the Claude Code model, treat each learner build as likely to need two or three fix rounds, and plan the rescue (`_trainer-only` reference, "used rescue" on the sheet) from the start. A stronger model for Claude Code, if you can use one, will change these results: re-run this test with it.

### Re-test with a stronger Claude Code model, 2026-10-06: `nemotron-3-ultra:cloud`

Model choice: the Ollama cloud models retired earlier (qwen3-coder, deepseek-v3.1, kimi-k2, glm-4.6, minimax-m2) answer "retired"; the newer ones (kimi-k3, kimi-k2.7-code, glm-5.3, glm-5.2, deepseek-v4-pro, minimax-m3) answer "not in the Free plan". On the free plan the strongest working option was `nemotron-3-ultra:cloud` (also `nemotron-3-super`, `gemma4:31b-cloud`, `gpt-oss:20b-cloud`). Same method as the gpt-oss test above: clean learner copy, Prompt 1 then Prompt 2 with `-c`, built file run with `yes` and `no`. The built agents still call `gpt-oss:120b-cloud`; only Claude Code's model changed. The learner docs now start Claude Code with `ollama launch claude --model nemotron-3-ultra:cloud` and ask learners to check both models in "Before you start".

One prompt bug surfaced and was fixed (it also explains the gpt-oss failures where `yes` was treated as `no`): the model wrote `interrupt("...")` as a bare call and ignored its return value, so `approved` was never set. The "LangGraph facts" block now says to store it: `approved = interrupt("question")`, then route on state. Prompt 1 on Day 19 now also requires a clean sample pull request (no TODO, eval, exec, os.system or bare pass), because one build invented a flawed diff and was Blocked every run.

Day 19 result on nemotron-3-ultra: Agent 3, first build: `Reviewing PR: ...`, findings that quote the added line, three gates all PASS, verification debt, release notes and documentation, approval prompt, `Status: Released` on `yes` and `Status: Stopped: human declined the release` on `no`. The chain, built on known-good agents: D1 (`yes, yes, yes`) ended `Final status: Released` with exactly two handoff entries; D2 (`yes, no`) ended `Stopped in Agent 2` with one handoff and no Agent 3 output; D3 (`no`) ended `Stopped in Agent 1` with no handoffs; one file, no LangChain, no imports from the agent files. The chain prompt now carries the interrupt loop (`while "__interrupt__" in result: ...`), without which both models built a chain that printed nothing. Not re-run on this model: gate simulations C3 to C6 and C9, the documentation retry, and the headless accept-check (the `-p` form with `-y` itself ran fine for every build above).

Slides: the headless command slide now names `nemotron-3-ultra:cloud`.

**Bottom line (updated):** use `nemotron-3-ultra:cloud` as Claude Code's model; with it each day's agent and the chain worked with at most one short fix round in this test. `gpt-oss:120b-cloud` as Claude Code's model mostly did not (see the gpt-oss test above). Learners on a different Ollama plan may not have the same models, so have everyone run `ollama run nemotron-3-ultra:cloud` in the pre-class check. Keep the `_trainer-only` references as the rescue.

## Reference Answers (for the trainer)

- Reference Agent 3 takes a sample pull request (title, description, diff) and generates documentation with four headings that Python checks (added 2026-10-04 for the use case's PR review and documentation topics; C7, C8, C9). It passes C1–C8: `tests_passed=False` blocks on `tests passed`; `eval(` blocks on `no forbidden calls`; a HIGH finding blocks and prints no release notes; unreadable review JSON is treated as HIGH.
- Reference chain: three `yes` → `Released`; `yes, no` → `Stopped in Agent 2` with no Agent 3 output; `no` first → `Stopped in Agent 1`; handoff log has exactly two entries.
- Scope checks: only the expected new files; no `langchain`; no imports from other day files.

## Questions to Ask Learners

1. Which of your tests proves a gate is enforced by Python and not by the model?
2. What exactly travels through the Agent 2 → Agent 3 handoff?
3. What happened to Agent 3 when you answered `no` at Agent 2? How do you know?
4. Why is an unreadable review treated as HIGH?

## Common Mistakes (observed while testing)

- The review model is not deterministic: the same clean sample was released in one run and blocked in another because of a different severity label. This is the lesson, not a bug. Do not "fix" it by trusting the model more.
- A list reducer (`operator.add`) for the handoff log doubles the entries, because a subgraph returns the state it was given. Learners should catch this in test D4.
- Agents 1 and 2 share a `tries` counter; if the handoff does not reset it, Agent 2 can stop almost immediately.
- Piping `yes` from PowerShell adds a trailing space; use Command Prompt.
- Claude Code creates shared modules or imports across day folders; the scope checks catch it.

## Exit Check

Each learner shows a filled acceptance sheet with a decision for Agent 3 and a decision for the chain, each backed by evidence.


## Rehearsal 2026-10-07 (trainer machine, direct runs, not a live Claude Code build)

- `my_agent2.py` from the Day 18 class had to be replaced with a working build: the model must write the tests, test data and code (the old file hard-coded the code), approval had to handle yes/no, and the Unicode console crash had to be fixed.
- The chain was rebuilt by assembling the node code of `my_agent1.py`, `my_agent2.py` and `my_agent3.py`. With the real model: D1 released 5 of 5, D2 and D3 stopped correctly, exactly two handoffs.
- Problems found that are now written into Prompt 3 (they would break a learner's chain): Agent 1 compared its resume value to the string "yes", so a chain resuming with True always rejected; the agents did not set a `status` the parent could test; output printed before an interrupt is lost, so it is built into the `interrupt()` value; function and class names clash between files.
- Prompt 1 now defines HIGH as a crash or wrong result for input that matches the type annotations. Before, the reviewer called a `None` input HIGH about one run in three and blocked a good run; with the sentence, 6 of 6 Agent 3 runs and 5 of 5 chain runs released.
- **Not yet done:** a live Claude Code (`nemotron-3-ultra:cloud`) build from the revised Prompts 1 and 3, the guard hook and the Part 4A subagent built from the START-HERE prompts in a live session, and the `slides.pptx` update for the new 100-minute plan. Pilot these before relying on them.
