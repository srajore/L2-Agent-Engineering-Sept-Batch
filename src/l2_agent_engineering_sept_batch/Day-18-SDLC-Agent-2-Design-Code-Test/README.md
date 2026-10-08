# Day 18 — SDLC Agent 2: Design → Code → Test

> **One file to follow:** open `START-HERE.html` (or `START-HERE.md`). It has the concept, every prompt to paste (with copy buttons in the HTML), the run command, the tests and the hand-in sheet in one place, and it is the file to use in class. This README is the background reading.

## What You'll Learn Today

- Direct Claude Code to build a development assistant that generates code and tests, without writing code yourself.
- Understand why AI-generated code and AI-generated tests cannot be trusted until something independent runs them.
- Review a plan, then run acceptance tests on the finished agent.
- Perform the **weak-tests check**: break the code on purpose and see whether the tests notice.
- Accept or reject the agent with evidence.
- Create a **hook** with Claude Code that *blocks* edits to reference files and to other days' folders, and prove it blocks (see `CLAUDE-CODE-CONCEPTS.md`).
- (Optional practice) Create a read-only **subagent** (`agent-reviewer`) and prove it cannot edit anything.
- Explain the difference between a rule (guidance) and a hook (enforcement).

## Why This Matters

Generated code looks convincing even when it is wrong. The real danger is not bad code — it is code nobody checked. Today you practise the most important verification habit in AI-assisted development: never accept "the tests pass" until you know the tests would fail on wrong code. Agent 2's output (code plus passing tests) is what Agent 3 reviews tomorrow.

## Key Concepts

**Your Role: Verifier.** You specify the function, review Claude Code's plan, run acceptance tests, and decide. You don't write or edit Python. You can read the generated tests because they are short `assert` lines.

**What Agent 2 Must Do.** From a user story and a fixed function spec it must: write the tests first, write the code, run both, retry a limited number of times if they fail, and ask a human to approve. The fixed function name and behaviour is what lets separately generated tests and code agree.

**Test Data.** Test data is the table of example inputs and expected results ("1–3 June, balance 5, valid", "end before start, invalid"). Here it is a separate artifact from the assert statements. The model proposes it, plain Python checks it (enough cases, both valid and invalid outcomes, real dates), and the agent runs every case against the generated code. Good data is the difference between tests that look thorough and tests that are.

**Code Explanation.** Once the code passes, the model explains it in a few plain-English lines for a non-programmer. This is for the human reviewer: you approve code you can follow. If the explanation says something the code does not do, or leaves out a rule, that is a finding. A model explanation is helpful but not proof, so you compare it with the tests.

**Tests First.** Writing tests first makes them the specification the code has to meet. A correct build generates tests before code.

**Independent Execution.** The agent's own Python runs the code and tests in a **separate process with a time limit**. "Tests passed" must come from that run, never from the model's say-so. A time limit means a bad piece of generated code that loops forever cannot hang your computer.

**The Vacuous Pass.** During development of this lesson the model once wrote tests that contained their own copy of the function. They passed — and proved nothing, because they tested themselves. A correct build must reject such tests. You will check for this on purpose.

**The Weak-Tests Check.** The most important acceptance test of the day: take the generated function, remove a rule (for example the "end date before start date" check), run the same tests against it, and watch. If a test fails, the tests protect you. If all tests still pass, the tests are weak — reject.

**Bounded Retry.** If the code fails the tests, the agent refines the code; if the tests are unusable, it rewrites the tests. After 3 attempts it must stop and say why.

**Break It On Purpose.** You prove the safety rules by asking Claude Code to temporarily cause the problem: fake tests, always-wrong code, an infinite loop. Each must end cleanly.

**Models Vary.** The code and tests differ every run. You verify behaviour, not wording.

## What a Good Run Looks Like

```text
Generated code:
def validate_leave_request(start_date, end_date, balance_days) -> tuple:
    ... parses dates, checks end >= start, checks days <= balance ...

Generated tests:
assert validate_leave_request("2023-06-01", "2023-06-03", 5) == (True, "")
assert validate_leave_request("2023-06-10", "2023-06-05", 5)[0] is False
... (5 asserts calling the real function)

Validation after 1 attempt(s): ALL TESTS PASSED
Approve this code and tests? (yes/no): yes
Status: Code and tests approved
```

## In Class: 100 Minutes

Everything in this day is covered inside the 100 minutes, in the order of `START-HERE`. **Practise** means you do it yourself; **Introduce** means you see it and try the short version.

| Minutes | Activity | Depth |
| --- | --- | --- |
| 0-10 | Why and what: the trap of trusting AI tests, the vacuous pass | Introduce |
| 10-20 | Agent 2 plan: Prompt 1 in plan mode; tick the checklist | Practise |
| 20-35 | Build (Prompt 2), then run `my_agent2.py` yourself in a second Command Prompt window and answer `yes` | Practise |
| 35-50 | Acceptance tests B1, B2, B4, B5, B6 (test data and the code explanation) | Practise |
| 50-62 | **Weak-tests check:** run your tests against a broken copy. Accept only if a test fails | Practise |
| 62-72 | Break-it: fake tests, and always-wrong code (3 attempts then stop) | Practise |
| 72-95 | **Claude Code feature:** the guard **hook** (H1-H4). Set `.claude\active-day.txt` to today's folder; restart Claude Code after the hook is registered | Practise |
| 95-100 | Accept or reject decision | Practise |

## Optional practice after class (about 45 minutes)

Not needed to move on. Do it if you want to go deeper.

1. **Subagent:** create `agent-reviewer` and run tests A1-A4 (appendix of `START-HERE`).
2. The hook tests you skipped: H5 (change `active-day.txt`), H6 (reading is not blocked) and H7 (clean up).
3. The third break-it prompt: make the generated code loop forever and confirm it ends by itself with a timeout.
4. Complete both acceptance sheets.
5. **Assignment:** ask Claude Code to change the function spec to something else small (for example a password-strength check), rebuild, and run your acceptance tests again. Submit: the completed sheet and one example of a test that would not have caught a real bug, with the test you asked Claude Code to add.

## Before You Move to Day 19

- You can explain a vacuous pass in one sentence.
- You ran the weak-tests check and recorded the result.
- You saw the agent stop after the retry limit and survive an infinite loop.
- You made a written accept or reject decision with evidence.
