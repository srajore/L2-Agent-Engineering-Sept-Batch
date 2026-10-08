# Session 17 Trainer Guide — SDLC Agent 1: Requirements → Design

## Outcome

Learners direct Claude Code to build a requirements analyst agent and then **verify and accept or reject** it using acceptance tests. They do not write or study code.

## Files to Use

- `START-HERE.html` / `START-HERE.md` — **the learner handout to give out and follow in class.** One file: concept, every prompt (copy buttons in the HTML), run command, tests, and an appendix with the extra tests and the hand-in sheet. The HTML is generated from the markdown: edit the `.md`, then rebuild the HTML.
- `CLAUDE-CODE-PROMPTS.md`, `CLAUDE-CODE-CONCEPTS.md`, `README.md` — fuller reference versions of the same material (optional for learners)
- `CLAUDE-CODE-PROMPTS.md` — the learner's working document: spec, prompts, plan checklist, acceptance tests, break-it prompts, scope checks, acceptance sheet
- `README.md` — participant handout (concepts, what a good run looks like)
- `_trainer-only\Day-17-SDLC-Agent-1-Requirements-Design\example.py` — **your reference solution.** It is deliberately **not** in the learner folder, so Claude Code cannot read and copy it. Use it to confirm a learner's build is acceptable, to demonstrate a fix, or as the rescue file (see `IF-BUILD-FAILS.md`).
- `IF-BUILD-FAILS.md` — what learners do when a build or setup fails
- `slides.pptx` — classroom deck (Why, What, How, lab)

## Setup in Windows Command Prompt

```cmd
uv sync
ollama signin
ollama launch claude --model nemotron-3-ultra:cloud
uv run python _trainer-only\Day-17-SDLC-Agent-1-Requirements-Design\example.py
```

Learners need both Claude Code and Ollama signed in. Type `yes` at the approval prompt.

## Claude Code Concepts Block (added): Rules and Skills

Learners follow `CLAUDE-CODE-CONCEPTS.md` first (about 25 minutes): rules R1, R2, R4 (R3 as a class poll), then the `/accept-check` skill S1–S2. `_trainer-only\Day-17-SDLC-Agent-1-Requirements-Design\trainer-reference\` holds the working files (`rules\agent-style.md`, `rules\agent-files.md`, `skills\accept-check\SKILL.md`). Do not hand these out.

Verified while preparing this session (Claude Code 2.1.266 on Windows):

- Both rule files load: Claude Code can quote them back.
- The path-scoped rule (`paths: Day-*/my_*.py`) fired when an existing matching file was edited (the last line `# REVIEWED BY RULE` was added).
- **The always-on rule was followed on only 1 of 3 new files** (`# AGENT FILE` as first line). So R3 is a measurement, not a pass or fail. This is the lesson that sets up hooks on Day 18. Expect learners' numbers to vary.
- `/accept-check` ran correctly as a slash command, in a normal session and as `claude -p "/accept-check <file>"`.

Time note: the session is now planned as 100 minutes following `START-HERE`; deeper tests are optional practice after class (see the flow below).

## Suggested 100-Minute Flow (follows START-HERE)

Learners complete the "Before you start" table in `START-HERE.md` **before class** (about 10 minutes, covers Days 17 to 19).

1. **0-10 — The concept, Introduce:** specify, verify, accept; artifacts, traceability, decomposition, model-suggests / Python-validates / human-approves. Show the "good run" output.
2. **10-20 — Plan review, Practise:** Prompt 1 in plan mode; tick the checklist. Make them send back at least one plan that fails.
3. **20-35 — Build and run, Practise:** Prompt 2; learners run `my_agent1.py` themselves in a second Command Prompt window.
4. **35-50 — Acceptance tests A1, A2, A3, A5, A7, A8, Practise.**
5. **50-60 — Break-it 1, Practise:** always-failing validation stops after exactly 2 attempts.
6. **60-90 — Claude Code feature, Practise / Introduce:** rules (R1, R2, R4; R3 as a class poll) and the `/accept-check` skill (S1, S2). The agent is already running by now.
7. **90-100 — Decision, share, assignment brief.**

### Optional practice after class (about 45 minutes)

A4, A6, R5, S3, S4, the invalid-JSON break-it, scope checks, the acceptance sheets, and the assignment (own two-sentence requirement). All are in the appendix of `START-HERE`.

## Live build test (done 2026-10-03, real Claude Code)

> **Model caveat:** this test used a Claude model. Participants will use `gemma4:cloud` through Ollama, which I have not tested. Treat the results and timings below as a best case, and pilot the Day 17 prompts on `gemma4:cloud` before class.

I pasted Prompts 1 and 2 into Claude Code in a **learner copy** of the repository (no `_trainer-only`, no trainer guides), then ran the acceptance tests on what it built.

- **Plan:** met every item on the plan checklist (one file, numbering step, model step, separate Python validation, retry limit of 2 and a stop route, approval pause, no LangChain).
- **Build:** a single `my_agent1.py` with no extra files, direct `ollama.chat` with `gpt-oss:120b-cloud`, `interrupt` with `InMemorySaver`, and an explicit conditional route for retry, approve and give-up.
- **Acceptance:** A1 (full run, status `Design ready`), A2 (R1, R2, R3 all traced), A3 (a question for "quickly", "secure" and "easy to use"), A4 (a Given/When/Then line for every story), A5 (answering `no` printed `Status: stopped` and no design) and all scope checks passed.
- **Not run live:** A6 and the two break-it prompts. The reference solution passes them; a real build may differ, so run them in your own pilot.

Things the test exposed, now fixed in the prompts:

1. **Planning time:** without the line "Make a short plan first (under 15 lines). Do not explore other folders or use research helpers", the plan step took about 8 and 23 minutes in two headless runs. The prompts now include the line. Check the time on your own machine.
2. **Claude Code cannot type at a prompt, and it asks permission to run programs.** Prompt 2 now tells Claude Code *not* to run the program; learners run it themselves in a second Command Prompt window. (In headless mode the shell was refused outright; interactive learners will see permission prompts instead.)
3. **Claude Code reads everything in the repo.** In the trainer's repo it found `_trainer-only\...\example.py` and used it to shape its plan. Always run learners from a copy made without `_trainer-only` (command in `_trainer-only\README.md`, tested). Its research helper also falsely claimed to have read an "answer key"; Claude Code verified the file did not exist and discarded the claim, but expect odd statements like this.

### Concepts block, run live

- **Rules prompt:** Claude Code produced both rule files exactly as specified (always-on and `paths: Day-*/my_*.py`).
- **Skill prompt:** a loosely worded spec was **ignored**. Claude Code built its own eight-check skill from the repo's `CLAUDE.md` and the new rules, with different wording and no `findstr` commands. The prompt now gives the exact file text between START and END, and Claude Code then wrote it correctly. `/accept-check` returned `DECISION: ACCEPT` on a good agent file and `DECISION: REJECT` on a file containing `import langchain`. S1 therefore compares the file with the prompt text.
- **Writing into `.claude`:** this folder is protected. In headless mode every write was refused (an allow rule does not override it). In a normal interactive session learners get a permission prompt and approve it. I could only test with permissions bypassed in a throwaway copy, so **watch the first prompt on your own machine** and note exactly how it looks.
- **Everything built earlier now steers later builds.** With the `# AGENT FILE` rule loaded, Claude Code even started the hook script (Day 18) with that comment line. Harmless, and a nice demonstration that rules do get applied.

## Pilot on the Ollama models (2026-10-04): expect first builds to fail

Prompts 1 and 2 were run headless through `ollama launch claude --model <model> -y -- -p "..."` in a fresh learner copy, on `gpt-oss:120b-cloud` and on `gemma4:cloud`. Neither produced a clean Agent 1 on the first build, so plan for a fix loop in class and keep the rescue file ready.

- `gpt-oss:120b-cloud`: the first file had a stray quote (`SyntaxError`). One fix message in the fail-page format repaired it. A second fix then tagged stories R1 to R3 (A2 passed) but dropped the Given/When/Then, the functional lists and the split of "approve or reject" (A4, A7, A8 failed), and the `no` answer printed the wrong status. A long detailed fix message made it remove the approval step. Lesson: **rerun every test A1 to A8 after each fix**, not just the failed one, and keep fix messages short.
- `gemma4:cloud`: ran, but used its own requirement ("log in and reset their passwords") instead of the leave sentences and stopped at the approval prompt. A1 to A8 fail until fixed.
- Prompt 2 now ends with a `py_compile` check. That removed the `SyntaxError` on `gpt-oss`; it does not catch undefined names or ignored specs, so tests A1 to A8 remain the real check.
- Headless plan mode returns only the plan file, not the plan text. Learners read the plan in an interactive session.
- Verified: `ollama launch claude --model gpt-oss:120b-cloud -y -- -p "..."` works, so the headless form used on Day 19 (P1) is confirmed for `gpt-oss`.

## Verification run 2026-10-05 (reference solution, `gpt-oss:120b-cloud`)

Run from `_trainer-only` with `echo yes |` / `echo no |`:

- `yes`: 3 clarifying questions (quickly, secure, easy to use); 5 stories, with R2 split into an approve story and a reject story; 6 functional and 5 non-functional requirements; `Status: Design ready` and a design.
- `no`: `Status: Stopped: human rejected the stories`, no design printed.

This checks the **reference** only. The learner-built `my_agent1.py` was not rebuilt in this run.

### Prompt change 2026-10-05: prompts no longer depend on repo files

Prompt 1 used to begin "Read CLAUDE.md" and say "like Day-08". For a standalone learner pack both were removed: the `interrupt` / `Command(resume=...)` / `InMemorySaver` recipe is now written into the prompt itself, and the project rules were already stated in the prompt. Prompt 1 in `START-HERE.md` and `CLAUDE-CODE-PROMPTS.md` was updated together. **The changed prompt has not been piloted on a live Claude Code build.** Pilot it before class. `slides.pptx` and `IF-BUILD-FAILS.md` were not edited: check them for the old wording.

### Live learner-flow test 2026-10-06 (`gpt-oss:120b-cloud` through `ollama launch claude`, headless, clean learner copy)

Method: a learner copy without `_trainer-only`, Prompt 1 then Prompt 2 as a continuation (`-c`), the built file run with `echo yes |` and `echo no |`, then short learner-style fix messages. The Claude Code features were tested with permissions bypassed in a throwaway copy.

Prompt hardening that came out of this test (already applied in `START-HERE.md` and `CLAUDE-CODE-PROMPTS.md`): the model got the LangGraph API wrong (dict as state schema, wrong `add_conditional_edges` arguments, `from langgraph.checkpoint import InMemorySaver`), so Prompt 1 now carries a short "LangGraph facts" block; builds that compiled but printed nothing, so Prompt 1 now says exactly what the file prints when run. Expect to re-check these two additions in your own pilot.

Results for Day 17: of five builds, none passed A1 to A8. Typical first-build failures: `StateGraph()` with no or a dict schema, the run call left commented out, asking for typed input instead of using the sample requirement, every story tagged `REQ-001` (A2), `no` printing "Design ready" (A5), the requirement not split into approve and reject stories (A8). One build reached `Status: Design ready` on `yes` after two fix rounds but still failed A5 and A8. Twice the model printed its tool call as JSON text and never wrote `my_agent1.py`: if no file appears, just resend Prompt 2.

Claude Code features: the rules prompt originally produced a markdown heading (`# Paths:`) instead of a `paths:` header, so Prompt "rules" now gives the exact YAML header (verified: a real `paths:` header, and the scoped rule fired, last line `# REVIEWED BY RULE`, R4 pass). R2 now expects only the always-on rule to be quoted, because a path-scoped rule loads only when a matching file is used. The skill prompt (exact text) produced an identical `SKILL.md` (S1 pass); `/accept-check` on a file with `import langchain` gave three FAIL and `DECISION: REJECT` (S3 pass). On a good stub file the model once edited the file instead of running the check (the always-on rule made it add `# AGENT FILE`), so S2/S4 are not reliable headless: confirm interactively. Scope check false alarm: a comment such as "No LangChain" makes `findstr` fail; the guide now says so.

**Bottom line for class (gpt-oss as Claude Code model):** with `gpt-oss:120b-cloud` as the Claude Code model, treat each learner build as likely to need two or three fix rounds, and plan the rescue (`_trainer-only` reference, "used rescue" on the sheet) from the start. A stronger model for Claude Code, if you can use one, will change these results: re-run this test with it.

### Re-test with a stronger Claude Code model, 2026-10-06: `nemotron-3-ultra:cloud`

Model choice: the Ollama cloud models retired earlier (qwen3-coder, deepseek-v3.1, kimi-k2, glm-4.6, minimax-m2) answer "retired"; the newer ones (kimi-k3, kimi-k2.7-code, glm-5.3, glm-5.2, deepseek-v4-pro, minimax-m3) answer "not in the Free plan". On the free plan the strongest working option was `nemotron-3-ultra:cloud` (also `nemotron-3-super`, `gemma4:31b-cloud`, `gpt-oss:20b-cloud`). Same method as the gpt-oss test above: clean learner copy, Prompt 1 then Prompt 2 with `-c`, built file run with `yes` and `no`. The built agents still call `gpt-oss:120b-cloud`; only Claude Code's model changed. The learner docs now start Claude Code with `ollama launch claude --model nemotron-3-ultra:cloud` and ask learners to check both models in "Before you start".

One prompt bug surfaced and was fixed (it also explains the gpt-oss failures where `yes` was treated as `no`): the model wrote `interrupt("...")` as a bare call and ignored its return value, so `approved` was never set. The "LangGraph facts" block now says to store it: `approved = interrupt("question")`, then route on state. Prompt 1 on Day 19 now also requires a clean sample pull request (no TODO, eval, exec, os.system or bare pass), because one build invented a flawed diff and was Blocked every run.

Day 17 result on nemotron-3-ultra: the first build after the fix wrote one file, no LangChain, and the stories and lists were correct (R1, R2 twice for approve and reject, R3 twice; Given/When/Then on every story; functional and non-functional lists; a design after `yes`; `no` gave `Status: Stopped: human rejected the stories`). It lacked the `Approve these stories and criteria? (yes/no)` line and `Status: Design ready`, so I sent one short learner-style fix message; after it A1, A2, A3, A5, A7 and A8 passed (the approval question now prints twice, a cosmetic repeat from the node re-running on resume). Earlier builds on the unfixed prompt ended `Status: Stopped: validation failed after 2 attempts` even with good content.

Claude Code features on nemotron-3-ultra: the rules prompt gave a real `paths:` header; the skill file was identical to the prompt text; `/accept-check` on a good stub file gave three PASS and `DECISION: ACCEPT` and left the file unchanged; on a file with `import langchain` it gave three FAIL and `DECISION: REJECT`. Not re-run: the R3 compliance poll, R5, S4 beyond the unchanged-file check.

**Bottom line (updated):** use `nemotron-3-ultra:cloud` as Claude Code's model; with it each day's agent and the chain worked with at most one short fix round in this test. `gpt-oss:120b-cloud` as Claude Code's model mostly did not (see the gpt-oss test above). Learners on a different Ollama plan may not have the same models, so have everyone run `ollama run nemotron-3-ultra:cloud` in the pre-class check. Keep the `_trainer-only` references as the rescue.

## Reference Answers (for the trainer)

- The reference build passes A1–A8 and both break-it tests. A7 and A8 were added on 2026-10-04 to cover the use case's functional/non-functional requirements and user-story decomposition: in a reference run R2 became two stories (approve, reject) and both requirement lists were printed. Break-it 1 shows exactly 2 analysis attempts and then the stop status. Break-it 2 reports a problem and retries or stops.
- Expected scope checks: only `my_agent1.py` added; no `langchain`; model name and `interrupt` found.
- A6 (different input): in a reference run, the one-sentence email requirement produced one story traced to R1 and two clarifying questions (recipients, email contents), then a design after `yes`. The rule "at least one clarifying question" is enforced even when no word is vague, so the agent always asks something; use that to discuss whether that rule is right.

## Questions to Ask Learners

1. Which part of the plan told you validation would not be done by the model?
2. What would you have done if the output had passed A1 but failed A3?
3. Why is "Claude Code says it works" not evidence?
4. What did your break-it test prove that a normal run could not?

## Common Mistakes (observed while testing)

- Learners accept a plan without ticking the checklist. Insist on ticking every box.
- Learners trust a claim of success without a run. Make them paste output as evidence.
- Output wording differs each run; learners reject on wording. Coach them to verify rules and shape.
- Running with piped input from PowerShell adds a trailing space to the answer. Use Command Prompt and type the answer.
- Claude Code adds LangChain or splits files; scope checks catch this.
- Break-it edits are not restored; ask learners to confirm the file was restored.

## Exit Check

Each learner shows a filled acceptance sheet with evidence and a one-sentence decision.
