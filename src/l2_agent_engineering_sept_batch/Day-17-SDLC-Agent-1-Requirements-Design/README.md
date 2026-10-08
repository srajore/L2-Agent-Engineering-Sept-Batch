# Day 17 — SDLC Agent 1: Requirements → Design

> **One file to follow:** open `START-HERE.html` (or `START-HERE.md`). It has the concept, every prompt to paste (with copy buttons in the HTML), the run command, the tests and the hand-in sheet in one place, and it is the file to use in class. This README is the background reading.

## What You'll Learn Today

- Direct Claude Code to build a requirements analyst agent from a specification, without writing code yourself.
- Know what a good requirements agent must produce: user stories, Given/When/Then criteria, clarifying questions, traceability and a design.
- Review Claude Code's **plan** before it writes anything.
- Verify the finished agent by running it, using acceptance tests and deliberate "break it" checks.
- Make a clear **accept or reject** decision and tell Claude Code exactly what to fix.
- Create **rules** (`.claude\rules\`, always-on and path-scoped) and a **skill** (`/accept-check`) with Claude Code, and prove them (see `CLAUDE-CODE-CONCEPTS.md`).
- Measure how often a rule is actually followed, and understand why that makes rules guidance, not a guarantee.

## Why This Matters

Until now you built agents by hand. From now on a coding assistant writes the code, and your job moves to the part it cannot do for you: deciding what "correct" means and proving the result meets it. That is how AI-assisted development works on real teams — specify, verify, accept. Bad requirements poison every step after them, so Agent 1 is a good place to practise: its output is exactly what Agent 2 receives tomorrow.

## Key Concepts

**Your Role: Specifier, Verifier, Approver.** You write the spec (in `CLAUDE-CODE-PROMPTS.md`), Claude Code builds, and you run the acceptance tests. You never need to read or edit the Python. If you can describe a behaviour and check it, you can accept it.

**What Agent 1 Must Do.** Take a short requirement and produce: (1) user stories in "As a / I want / so that" form, (2) Given/When/Then acceptance criteria, (3) clarifying questions for vague words such as "quickly", "secure" and "easy", (4) functional and non-functional requirements, and (5) a short design — but only after a human says yes.

**Decomposition.** A sentence like "Managers approve **or** reject the request" contains two actions. A good analyst writes one story for approving and one for rejecting, both traced to the same sentence. The agent's Python validation checks this: a sentence with "and" or "or" must produce at least two stories.

**Functional and Non-Functional Requirements.** Functional requirements say what the system does ("shall let a manager approve a request"). Non-functional requirements say how well it does it: security, usability, speed, availability. Both lists are produced, validated as non-empty, shown to the human at approval, and used by the design step.

**Traceability.** Every sentence of the requirement gets an ID (R1, R2, R3). Every story must name the ID it came from, and every ID must be covered. When you verify, you can check this by looking at the output.

**Model Suggests, Python Validates, Human Approves.** A correct build keeps these jobs separate. The model writes the stories. Plain Python rules check them (valid structure, "As a" stories, Given/When/Then criteria, every ID traced, at least one question). A person approves before the design is written. If the build lets the model grade itself, reject it.

**Bounded Retry.** If the check fails, the agent tries again, at most twice, then stops. An agent that can loop forever is not acceptable.

**The Plan Is Your Cheapest Review.** In plan mode Claude Code lists what it will build. A missing validation step or retry limit is easy to spot in a plan and expensive to find after the code exists. Review the plan against the checklist before you approve.

**Break It On Purpose.** You do not have to trust that safety rules work. Ask Claude Code to temporarily make validation always fail, or make the model return garbage, and show you the output. Accept only if the agent stops cleanly.

**Scope Checks.** Three Command Prompt commands tell you without reading code whether Claude Code stayed in bounds: only one new file, no LangChain, the right model name, an approval pause present.

**Models Vary.** The wording of stories changes every run. You verify behaviour and rules, not exact words.

## What a Good Run Looks Like

```text
Clarifying questions for the stakeholder:
 - How fast is "quickly" for a manager approval?
 - What does "secure" require (MFA, roles)?
 - What makes it "easy to use"?

User stories:
 US-1 (R1): As an employee, I want to submit a leave request online, so that ...
    * Given the employee is logged in, when they submit the form, then the request is stored.
 US-2 (R2): As a manager, I want to approve or reject leave requests, so that ...

Functional requirements:
 - The system shall let employees submit leave requests online.
 - The system shall let managers approve a request. / ... reject a request.
Non-functional requirements:
 - The system shall encrypt data in transit (security).
 - A leave request shall take no more than three clicks (usability).

Approve these stories and criteria? (yes/no): yes
Status: Design ready
```

Your wording will differ. The shape must match: questions for each vague word, stories tagged R1/R2/R3, a Given/When/Then line per story, a pause, then a design.

## In Class: 100 Minutes

Everything in this day is covered inside the 100 minutes, in the order of `START-HERE`. **Practise** means you do it yourself; **Introduce** means you see it and try the short version. Do the "Before you start" setup in `START-HERE` before class.

| Minutes | Activity | Depth |
| --- | --- | --- |
| 0-10 | The concept: the agent, the artifacts, how a correct build is organised | Introduce |
| 10-20 | Plan: Prompt 1 in plan mode; tick the checklist | Practise |
| 20-35 | Build (Prompt 2), then run `my_agent1.py` yourself in a second Command Prompt window and answer `yes` | Practise |
| 35-50 | Acceptance tests A1, A2, A3, A5, A7, A8 | Practise |
| 50-60 | Break-it: validation always fails, and the agent stops after exactly 2 attempts | Practise |
| 60-90 | **Claude Code feature:** rules (R1, R2, R4, and the R3 class poll) and the `/accept-check` skill (S1, S2) | Practise / Introduce |
| 90-100 | Accept or reject decision, share results, assignment brief | |

If you reject, send Claude Code one short, precise fix request and re-run **all** the tests.

## Optional practice after class (about 45 minutes)

Not needed to move on. Do it if you want to go deeper.

1. The items not done in class: A4, A6, R5 (clean up), S3 (the skill rejects a bad file), S4 (the skill edits nothing), and the second break-it prompt (invalid JSON). All are in the appendix of `START-HERE`.
2. Complete the acceptance sheets if you did not finish them in class.
3. **Assignment:** choose your own two-sentence requirement. Ask Claude Code to run Agent 1 on it. Submit: the requirement, the completed acceptance sheet, and one case where the agent's output was weaker than you expected, with how you would tell Claude Code to improve it.

## Before You Move to Day 18

- You can state the five things Agent 1 must produce.
- You reviewed a plan against a checklist before approving.
- You ran at least one break-it test and saw the agent stop cleanly.
- You made a written accept or reject decision with evidence.
- You recorded your rule-compliance number (R3) and can explain what it means.
