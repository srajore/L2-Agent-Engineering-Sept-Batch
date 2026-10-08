# Day 19 — SDLC Agent 3: Review → Release, and Agents Talking to Each Other

> **One file to follow:** open `START-HERE.html` (or `START-HERE.md`). It has the concept, every prompt to paste (with copy buttons in the HTML), the run command, the tests and the hand-in sheet in one place, and it is the file to use in class. This README is the background reading.

## What You'll Learn Today

- Direct Claude Code to build a review and release agent, then connect all three SDLC agents into one chain, without writing code yourself.
- Tell the difference between a **finding** (advice), a **gate** (a rule that blocks) and an **approval** (a human decision).
- Verify that quality gates really block release, one gate at a time.
- Verify agent-to-agent handoff: what one agent passes to the next, and that the chain stops when a human says no.
- Accept or reject both Agent 3 and the chain with evidence.
- Prove that your Claude Code setup (rules, skill, hook, subagent) works together while you build. Today you create the hook and the read-only subagent.
- Run Claude Code **headless** (`claude -p`) for a repeatable check.
- Complete the Claude Code driver's check: 13 practical tasks that show you can drive Claude Code end to end (appendix of `START-HERE`).

## Why This Matters

Releasing is the point of no return. A model reviewer is useful but inconsistent: while building this lab, the same kind of code was labelled "MEDIUM" risk in one run (and released) and "HIGH" risk in another (and blocked). So the model only suggests; plain Python gates decide whether release is allowed; and a person approves. Then you connect the agents so requirements flow into code and code flows into review — and you verify that the connection is safe.

## Key Concepts

**Your Role: Verifier.** You specify, review plans, run acceptance tests and decide. You do not read or write Python.

**Finding, Gate, Approval.** A finding is the reviewer's observation with a severity (HIGH, MEDIUM, LOW). A gate is a Python rule: `tests passed`, `no HIGH findings`, `no forbidden calls` (`eval(`, `exec(`, `os.system(`, `TODO`). An approval is a person typing yes or no. If any gate fails, release is blocked and no release notes are written.

**Safe Failure.** If the model's review is not readable (not valid JSON), the agent must treat it as a HIGH finding. An unreadable review must never count as a clean review.

**Verification Debt.** Findings that do not block release are still listed and shown to the approver. Shipping with known, recorded issues is a decision; shipping with hidden ones is an accident.

**Pull-Request Review.** Real teams review a *change*, not a whole file. Here the input is a pull request: a title, a description and a diff, where lines starting with `+` are the added code. The reviewer reads the PR as a whole and each finding quotes the added line it refers to, so a human can jump straight to the problem.

**Documentation Is a Release Artifact.** Besides the changelog and release notes, the agent writes short documentation with four fixed headings: Purpose, Parameters, Returns, Example. Plain Python checks that all four are present and that the function is named. If the documentation is still incomplete after one retry, release is blocked as "documentation incomplete". Documentation that cannot be checked mechanically is at least checked for completeness.

**Release Artifacts Before Approval.** The changelog, release notes and documentation are drafted and shown before the human decides, so the person approves what will really be published.

**Agent-to-Agent Communication.** In the chain, each agent is its own small graph used as one step of a larger parent graph. Between agents sits a short **handoff step** that turns one agent's output into the next agent's input (Agent 1's stories become Agent 2's story; Agent 2's code is packaged as a pull request for Agent 3) and records a line in a handoff log. There are no hidden messages: you can read the log.

**Stop Rules.** The chain continues only if an agent finishes successfully. A `no` at Agent 1 or Agent 2 ends the chain right there; later agents must not run.

**Things To Look For.** Two bugs appeared while building the reference chain, so watch for them when you verify: a handoff log with duplicate entries (it should have exactly two), and a later agent stopping immediately because it inherited an earlier agent's counter.

**Models Vary.** Review severity and wording differ from run to run. If a good sample is Blocked because of a HIGH finding, read the finding and decide whether you agree; run again if needed.

## What a Good Chain Run Looks Like

```text
AGENT 1 stories: US-1 (R1): As an employee, I want to request leave online ...
Approve? (yes/no)  > yes

AGENT 2 code: def validate_leave_request ...   Tests: ALL TESTS PASSED
Approve? (yes/no)  > yes

AGENT 3 release: Gates: PASS tests passed, PASS no HIGH findings, PASS no forbidden calls
Changelog: Added validation for leave requests ...
Approve release? (yes/no)  > yes

Handoffs:
 - Agent 1 -> Agent 2: 2 stories and a design
 - Agent 2 -> Agent 3: code (25 lines), tests passed = True
Final status: Released
```

## In Class: 100 Minutes

Day 18 ran out of time before hooks and subagents, so today starts with the guard hook (about 20 minutes), adds the read-only subagent after Agent 3 is built, and then builds the chain.

Everything in this day is covered inside the 100 minutes, in the order of `START-HERE`. **Practise** means you do it yourself; **Introduce** means you see it and try the short version.

| Minutes | Activity | Depth |
| --- | --- | --- |
| 0-5 | Why and what: findings, gates, approvals; subgraphs and handoffs | Introduce |
| 5-25 | **Claude Code feature:** the guard hook (plan, restart, tests H1-H4) | Practise |
| 25-41 | Agent 3 plan (Prompt 1), build (Prompt 2), then run it yourself in a second Command Prompt window | Practise |
| 41-49 | **Claude Code feature:** the read-only subagent (create it, run one review, prove it cannot edit: SA1-SA3) | Practise |
| 49-57 | Agent 3 tests: C1, C2, C7, C8 and the gate tests C4, C5 | Practise |
| 57-72 | Chain plan (Prompt 3) and build (Prompt 4) after checking your Day 17 and Day 18 agents run, then run it yourself | Practise |
| 72-82 | Chain tests D1-D4: happy path, stop at Agent 2, stop at Agent 1, handoff log | Practise |
| 82-90 | **Claude Code feature:** headless mode (one `claude -p` run, P1); skim the driver's check | Introduce |
| 90-100 | Decisions for Agent 3 and the chain | Practise |

## Optional practice after class (about 45 minutes)

Not needed to move on. Do it if you want to go deeper.

1. Chain test D5 (the real hand-off) and integration test I5 (ask the `agent-reviewer` subagent (built in class) to review `my_chain.py` and turn one finding into a test).
2. Headless test P2 (`claude -p` on a file with `import langchain` gives REJECT).
3. Finish the **Claude Code driver's check**: tick every one of the 13 tasks with proof (appendix of `START-HERE`).
4. Complete the acceptance sheets.
5. **Assignment:** ask Claude Code to add one more gate (for example "the code must have a docstring"). Write the acceptance test for it first, then run it. Submit: your test, the evidence, and a one-line accept or reject.

## Before You Move to Day 20

- You can explain finding, gate and approval to a colleague.
- You saw each gate block release, one at a time.
- You ran the chain with three `yes`, with a `no` at Agent 2, and with a `no` at Agent 1.
- You checked the handoff log has no duplicates.
