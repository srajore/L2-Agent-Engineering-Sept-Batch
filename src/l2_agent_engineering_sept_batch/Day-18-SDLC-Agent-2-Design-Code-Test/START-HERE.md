# Day 18: Agent 2 (Design → Code → Test). START HERE (100 min)

**This is the only file you need today.** By the end, `my_agent2.py` is built by Claude Code and running.

**Your role:** you write no code. Today's question is harder: *can I trust what the AI wrote?*

**Before you start:** complete the "Before you start" table at the top of the Day 17 `START-HERE.md` (Claude Code installed, `ollama signin`, `uv sync`). Today's agent doesn't need anything Claude built on Day 17. If you skipped Day 17, you can still do all of Day 18.

**Setup (2 windows, both in the course folder):**
- Window 1: `ollama launch claude --model nemotron-3-ultra:cloud`. This is where you paste prompts.
- Window 2: plain Command Prompt. This is where you run the agent.

| Min | Part |
| --- | --- |
| 0–10 | 1. The concept |
| 10–20 | 2. Plan (Prompt 1) |
| 20–35 | 3. Build and run (Prompt 2) |
| 35–50 | 4. Tests |
| 50–62 | 5. Do the tests protect you? |
| 62–72 | 6. Break it |
| 72–95 | 7. Claude Code feature: hook |
| 95–100 | 8. Decide, wrap-up |

---

## 1. The concept (10 min)

```
User story --> tests first --> test data --> code --> run in a separate process --> explain --> human yes
```

Agent 2 writes a function `validate_leave_request(start_date, end_date, balance_days) -> (True, "") or (False, "<reason>")`.

Ideas to teach:
- **Tests first.** The tests describe correct behaviour before any code exists.
- **Test data:** a table of 5 to 8 cases, checked by Python (valid and invalid, real dates).
- **Safe execution:** model-written code runs only in a **separate process with a timeout** (15 s), never inside the agent.
- **Fake tests:** tests that define the function themselves pass without testing anything, so Python must reject them.
- **Bounded retry:** at most 3 attempts, then stop.
- **Explain before approve:** a plain-English summary is shown before the human decides.
- **The key question:** green tests mean nothing if they'd also pass on wrong code. You'll prove otherwise in Part 5.

---

## 2. Plan first (10 min)

In Window 1 press **Shift+Tab until plan mode is on**, then paste:

```text
Create ONE new file: Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py,
a LangGraph development assistant.

Goal: from a user story and a fixed function spec, generate tests first, then a test-data
table, then code; validate all of them; refine on failure; then explain the final code in
plain English and ask a human to approve.
Function spec: validate_leave_request(start_date, end_date, balance_days) -> tuple.
Dates are YYYY-MM-DD. days = (end - start) + 1. Return (True, "") when valid; return
(False, "<reason>") when end is before start or days exceed balance_days.
LangGraph facts (use exactly this API):
- Imports: from typing import TypedDict; from langgraph.graph import StateGraph, START, END;
  from langgraph.checkpoint.memory import InMemorySaver; from langgraph.types import Command, interrupt.
- The state is a TypedDict class (total=False), passed as StateGraph(StateClass). A node is a
  function that takes state and returns a dict of updates: builder.add_node("name", fn).
- Edges: builder.add_edge(START, "a"). Routing: builder.add_conditional_edges("a", route_fn,
  {"label": "next_node", "other": END}), where route_fn(state) returns one of the labels. Use no
  other arguments.
- Compile with graph = builder.compile(checkpointer=InMemorySaver()). Run with
  config = {"configurable": {"thread_id": "t1"}}: graph.invoke(state, config=config) runs until a node
  calls interrupt("question"); ask yes/no with input(), then
  graph.invoke(Command(resume=answer.lower() == "yes"), config=config).
- A node that calls interrupt() runs again from its start on resume, so put interrupt() in its own
  small node and print nothing before it.
- The value passed to Command(resume=...) is what interrupt(...) returns inside that node. Store it in
  state: approved = interrupt("question"); return {"approved": approved}. Route on state["approved"].
- Model replies may wrap JSON in markdown fences: strip them before json.loads.
Constraints: one file, direct ollama.chat with model gpt-oss:120b-cloud, no LangChain,
no pytest, explicit conditional edges, at most 3 attempts. Run model-generated code ONLY
in a subprocess with a timeout of 15 seconds, never inside this process.
Validation must reject tests that define the function themselves, because those pass
without testing anything. Tests must have at least 4 assert statements.
Test data: the model returns a JSON list of 5 to 8 cases with name, start, end, balance and
expect_valid. Plain Python checks it: at least 4 cases, both valid and invalid outcomes, and
real dates (an unreal date is allowed only in a case that expects invalid). Run every case
against the code in the same subprocess as the asserts. Retry bad test data up to 3 times.
Explanation: after the tests pass, the model explains the code in 3 to 6 short plain-English
lines for a non-programmer, and the program prints it before the approval question.
When the file is run (no arguments, no typing except the yes/no answer) it prints
"Generated code:", "Generated tests:", "Test data:" (one line per case), "Explanation of the code:",
and "Validation after N attempt(s): ALL TESTS PASSED" (or the failure reason). Then it asks
"Approve this code and tests? (yes/no): " with input(). On yes it prints "Status: Code and tests approved".
On no it prints "Status: Stopped: human rejected the code". If all 3 attempts fail it prints
"All attempts exhausted" with the last failure reason. Print the reason every time validation fails.
The file must actually call the graph under if __name__ == "__main__".
Make a short plan first (under 15 lines). Do not explore other folders or use research helpers.
Do not edit files yet.
```

**Approve the plan only if it has all of these:**
- [ ] Tests generated **before** the code
- [ ] Generated code runs in a **subprocess with a timeout**
- [ ] A check that tests don't define the function, and have 4+ asserts
- [ ] A test-data step with a Python check; the cases run against the code
- [ ] A step that **explains the code** before the approval
- [ ] A retry limit of 3 and a stop route
- [ ] A human approval step
- [ ] One file; no pytest; no LangChain

---

## 3. Build and run (15 min)

Approve the plan, then paste:

```text
Implement the plan. Do not run the program yourself: it stops to ask me to type yes or no,
and you cannot type for me. When the file is written, check that it compiles with
uv run python -m py_compile Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py and fix any error.
Then tell me the exact command to run.
```

**Run it in Window 2** and type `yes` at the approval prompt:

```cmd
uv run python Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py
```

**The agent is now up and running.**

*If the build fails or stalls for more than 5 minutes:* tell your trainer. Don't keep retrying the same prompt. Send Claude Code one precise fix request instead (see the examples in Part 4).

---

## 4. Tests (15 min)

| # | Test | Pass when |
| --- | --- | --- |
| B1 | Run, answer `yes` | Code, tests, "ALL TESTS PASSED", status approved |
| B2 | Read the `assert` lines | They cover: valid, exactly at balance, over balance, end before start |
| B5 | Read the test-data table | 5–8 cases, valid and invalid, includes exact-balance, over-balance, end-before-start |
| B6 | Read the explanation | 3–6 plain lines, printed **before** the approval question, mentions the end-date rule and the balance rule |
| B4 | Run again, answer `no` | Status says rejected |

**Fix loop (read this once):** the first build often has a bug. Send Claude Code **one short message** naming the failed test and what you saw. After every fix, **re-run all the tests**, not just the one that failed, because a fix can quietly break something that passed. Long, detailed fix messages can make Claude Code remove features. If it says "it works" or "it compiles" but shows no output, reply: `You said it works but did not run it. Run it and show me the output.` If two fixes don't work, ask your trainer.

If a test fails, **reject**. Name the test, quote what you saw, and ask for one fix, for example:
`Test B6 failed: there is no explanation before the approval question. Add the explain step and print it.`

---

## 5. Do the tests protect you? (12 min)

This is the most important test of the day. Paste in Window 1:

```text
Take the generated function and make a copy with the "end date before start date" check removed.
Run the SAME generated tests against that broken copy and show me the output.
Then delete the broken copy. Do not change the real file.
```

- **Accept when:** at least one test **fails** against the broken copy.
- **Reject when:** all tests still pass (the tests are weak). Say: `The tests did not catch the bug. Strengthen the test generation so the end-before-start case is covered, then repeat this check.`

---

## 6. Break it on purpose (10 min)

Paste each in Window 1:

```text
Temporarily make the tests contain a copy of the function definition, run the agent, show me
the output, then restore the original.
```
**Accept when:** the agent rejects those tests and does not report a pass.

```text
Temporarily make the generated code always wrong, run the agent and show me the output, then
restore it. I need to see exactly 3 attempts and then a stop.
```
**Accept when:** exactly 3 attempts and a stop message, and the file is restored.

*(Optional, in the appendix: the infinite-loop test. The run should end by itself after about 15 seconds with a timeout message.)*

---

## 7. Claude Code feature: hook (23 min)

**Concept.** On Day 17 you measured that a rule is followed *most* of the time. A **hook** is a small program Claude Code runs automatically *before* an action, and it can **block** it (exit code 2). A rule asks politely. A hook says no every time.

Today's guard blocks any edit or write when (a) the file is named `example.py` or `chain.py` (the course's reference answers, which Claude Code must not overwrite), or (b) the file is in a `Day-` folder other than today's.

> Claude Code will ask permission before writing in `.claude`. Check the path and allow it.

Plan mode, paste, then approve:

```text
Create exactly three files for a hook guard, and nothing else. Each file's content is the text
between its START and END lines, character for character (not including those lines). Do not add,
remove, reword or "improve" anything, and do not copy anything from any other settings file. If
.claude\settings.json already exists, change only its "hooks" key and keep everything else.

FILE 1: .claude\active-day.txt
START
Day-18-SDLC-Agent-2-Design-Code-Test
END

FILE 2: .claude\hooks\guard.py
START
import json
import os
import sys

# Runs before every Edit or Write. Exit code 2 blocks the action and
# sends the stderr message back to Claude Code.
data = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
path = data.get("tool_input", {}).get("file_path", "")
project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

# Work out the path relative to the project, with forward slashes
try:
    rel = os.path.relpath(path, project).replace(os.sep, "/")
except ValueError:
    sys.exit(0)
name = rel.split("/")[-1]
top = rel.split("/")[0]

with open(os.path.join(project, ".claude", "active-day.txt")) as f:
    active = f.read().strip()

if name in ("example.py", "chain.py"):
    print("BLOCKED: example.py and chain.py are the course's reference files. Do not edit them.", file=sys.stderr)
    sys.exit(2)

if top.startswith("Day-") and top != active:
    print(f"BLOCKED: today's folder is {active}. Do not edit {top}.", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
END

FILE 3: .claude\settings.json
START
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "uv run python .claude/hooks/guard.py" }
        ]
      }
    ]
  }
}
END
Then show me the three files.
```

Plan is OK only if it creates exactly those three things, uses `PreToolUse` with matcher `Edit|Write`, blocks by **exit code 2**, and changes nothing else.

**Restart `claude`**, accept the trust dialog, then test:

| # | Ask Claude Code | Pass when |
| --- | --- | --- |
| H1 | `/hooks` | A PreToolUse hook for Edit/Write is listed |
| H2 | `Create Day-18-SDLC-Agent-2-Design-Code-Test\hook_ok.txt containing hello.` | File created |
| H3 | `Create a file named example.py in Day-18-SDLC-Agent-2-Design-Code-Test containing a print line.` | **Refused** with the guard's message |
| H4 | `Create Day-17-SDLC-Agent-1-Requirements-Design\hook_no.txt containing hi.` | **Refused**: today's folder is Day-18 |

Then ask Claude Code to delete `hook_ok.txt`.

---

## 8. Decide and wrap up (5 min)

Write **ACCEPT** or **REJECT** with one line of evidence. Accept only if B1–B6, the broken-copy check, the two break-it tests and H1–H4 passed.

**Homework (optional):** the read-only reviewer subagent, the infinite-loop test and the scope checks. All are in the appendix below.

You're ready for Day 19 if you can explain why a hook beats a rule, and why green tests can still be useless.

---

## Appendix: extra tests, scope checks, subagent and hand-in sheet (homework or spare time)

**Extra tests**

| # | Test | Pass when |
| --- | --- | --- |
| B3 | Read the tests: you see **no** `def validate_leave_request`, only calls to it | Pass |
| Infinite loop | Paste: `Temporarily make the generated code loop forever, run the agent, then restore it.` | The run ends by itself with a timeout message after about 15 seconds. It does not hang |
| H5 | Ask Claude Code to change `active-day.txt` to the Day 17 folder name, then repeat H4 | Now allowed. Change it back to the Day 18 name afterwards |
| H6 | Ask Claude Code to read `pyproject.toml` and say how many lines it has | It answers (the guard only watches edits and writes) |

**Scope checks.** Run in Window 2:

```cmd
dir Day-18-SDLC-Agent-2-Design-Code-Test
findstr /i /c:"langchain" /c:"pytest" Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py
findstr /c:"subprocess" /c:"timeout" Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py
findstr /c:"eval(" /c:"exec(" Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py
```

| Check | Pass when |
| --- | --- |
| `dir` | Only `my_agent2.py` was added |
| `langchain` / `pytest` | No output |
| `subprocess` / `timeout` | Lines found for both |
| `eval(` / `exec(` | No output |

**A hit can be a false alarm.** `findstr` reads text only. If `langchain` or `pytest` appears only inside a comment or inside a prompt telling the model *not* to use it, nothing is wrong, but the check still fails. Ask Claude Code to remove the word, or note it on your sheet and accept.

**Subagent: a read-only specialist.** Concept: a subagent is a helper with its own focus and a short list of allowed tools. A reviewer with only Read, Grep and Glob can't change anything even if it wants to. Plan mode, paste, then approve:

```text
Create the subagent .claude\agents\agent-reviewer.md.
Header: name agent-reviewer; description: read-only reviewer that tries to find ways an agent
file could fail; tools: Read, Grep, Glob only; model sonnet.
Body: you are a strict read-only reviewer of small LangGraph agent files and never edit files.
Read the file you are given and report a numbered list of at most 5 items: the most likely ways
it could fail or be unsafe (missing validation, no retry limit, no human approval, unbounded
loop, model output trusted without checks). For each item, say how a person could test it
without reading code. End with the line REVIEWER: DONE.
Show me the file.
```

| # | Test | Pass when |
| --- | --- | --- |
| SA1 | Read the file | `tools` lists only Read, Grep, Glob; it says it never edits |
| SA2 | `Use the agent-reviewer subagent to review Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py` | Numbered list of at most 5 items, each with a way to test it, ending `REVIEWER: DONE` |
| SA3 | `Use the agent-reviewer subagent to fix the problems it found in my_agent2.py.` | The file does **not** change (it has no edit tool) |
| SA4 | Turn one finding into a break-it prompt and run it | You have a new test you did not have before |

**Hand-in sheet**

| Test | Pass / Fail | Evidence |
| --- | --- | --- |
| B1 | | |
| B2 | | |
| B3 | | |
| B4 | | |
| B5 (test data) | | |
| B6 (explanation) | | |
| Broken copy fails a test | | |
| Break-it: fake tests rejected | | |
| Break-it: 3 attempts then stop | | |
| Break-it: infinite loop times out | | |
| Scope checks | | |
| Hook H1–H4 (paste the guard's message for H3) | | |
| Hook H5–H6 | | |
| Subagent SA1–SA4 | | |
| **Decision** | ACCEPT / REJECT | One sentence why |
