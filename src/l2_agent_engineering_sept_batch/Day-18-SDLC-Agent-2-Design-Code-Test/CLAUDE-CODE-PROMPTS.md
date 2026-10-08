# Day 18 — Build Agent 2 with Claude Code (you verify and accept)

**Your role today:** you do not write code. Claude Code builds a development assistant that writes code and tests. Your job is harder than it sounds: decide whether you can **trust** what it produced. Your trainer keeps the reference answer separately; you will not have a copy. If a build keeps failing, see `IF-BUILD-FAILS.md`.

Run commands in Windows Command Prompt from the repository root. Start Claude Code with `ollama launch claude --model nemotron-3-ultra:cloud`.

**Time plan:** in class do the first two break-it prompts; the third (the infinite loop) is shown by the trainer and is optional practice afterwards.

## 1. The specification (what Agent 2 must do)

| | |
| --- | --- |
| **Input** | A user story and a fixed function spec (below) |
| **Output** | A Python function, plain `assert` tests, a **test-data table**, a **plain-English explanation of the code**, and a validation result |
| **Function** | `validate_leave_request(start_date: str, end_date: str, balance_days: int) -> tuple`. Dates are `YYYY-MM-DD`. Days requested = (end - start) + 1. Returns `(True, "")` if valid, `(False, "<reason>")` if end is before start, or days requested exceed the balance |
| **Order** | Write the tests first, then the test data, then the code |
| **Test data** | The model produces a table of 5 to 8 cases (name, start, end, balance, expected valid or not). Plain Python checks it: at least 4 cases, both valid and invalid ones, real dates (an unreal date is only allowed in a case that expects "invalid"). The cases are run against the code in the same subprocess as the asserts |
| **Explanation** | After the tests pass, the model explains the final code in 3 to 6 plain-English lines for a non-programmer; it is shown to the human before approval |
| **Must** | Validate with plain Python: both parse, tests have 4+ asserts, tests do **not** define the function themselves, then run code + tests in a **separate process with a timeout** |
| **Must** | Retry at most 3 times (refine the code, or rewrite unusable tests), then stop |
| **Must** | Ask a human to approve before finishing |
| **Must not** | Use pytest, a tests folder, LangChain, or touch other folders |

## 2. Prompt 1 — ask for a plan only (plan mode on)

```
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

> **Tip from testing:** without the "short plan" line, Claude Code can spend many minutes researching before it answers. Keep the line.

### Accept the PLAN only if it has all of these

- [ ] Tests are generated **before** the code
- [ ] Generated code is run in a **subprocess with a timeout**
- [ ] A check that tests do **not** define the function, and have 4+ asserts
- [ ] A **test-data** step with a Python check, and the cases run against the code
- [ ] A step that **explains the code** in plain English before the approval
- [ ] A retry limit of 3 and a stop route
- [ ] A human approval step
- [ ] One file; no pytest; no LangChain

## 3. Prompt 2 — build and run

```
Implement the plan. Do not run the program yourself: it stops to ask me to type yes or no,
and you cannot type for me. When the file is written, check that it compiles with
uv run python -m py_compile Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py and fix any error.
Then tell me the exact command to run.
```

Claude Code cannot type at a prompt, and it asks your permission before running programs. So **you run the agent yourself**, in a second Command Prompt window opened in the repository root. Read the generated code, the tests, the validation output and the number of attempts that it prints:

```cmd
uv run python Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py
```

Type `yes` at the approval prompt for the first run.

## 4. Acceptance tests

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| B1 | Full run | Run, answer `yes` | Code, tests and "ALL TESTS PASSED" printed; status approved |
| B2 | Tests are readable and complete | Read the generated `assert` lines (they are plain English-like checks) | They cover: valid request, exactly at balance, over balance, end date before start date |
| B3 | Tests call the real function | Read the tests | You see **no** `def validate_leave_request` in the tests, only calls to it |
| B4 | Human gate | Run, answer `no` | Status says rejected; nothing is approved |
| B5 | Test data | Read the printed test-data table | 5 to 8 cases; at least one valid and one invalid; includes "exactly at balance", "over balance" and "end before start"; and the run says ALL TESTS PASSED, so the cases were run too |
| B6 | Code explanation | Read the explanation printed before the approval question | 3 to 6 plain-English lines that describe what the code checks and what it returns, with no jargon you cannot follow. Compare it with the code's behaviour: does it mention the end-date rule and the balance rule? |

## 5. The most important test: do the tests protect you?

Green tests mean nothing if they would also pass on wrong code. Make Claude Code prove otherwise:

```
Take the generated function and make a copy with the "end date before start date" check removed.
Run the SAME generated tests against that broken copy and show me the output.
Then delete the broken copy. Do not change the real file.
```

- **Accept when:** at least one test **fails** against the broken copy.
- **Reject when:** all tests still pass. The tests are weak. Say: `The tests did not catch the bug. Strengthen the test generation so the end-before-start case is covered, then repeat this check.`

## 6. Prove the safety rules by breaking things

```
Temporarily make the tests contain a copy of the function definition, run the agent, show me
the output, then restore the original.
```
- **Accept when:** the agent rejects those tests (it must not report a pass).

```
Temporarily make the generated code always wrong, run the agent and show me the output, then
restore it. I need to see exactly 3 attempts and then a stop.
```
- **Accept when:** three attempts and a stop message are shown; the file is restored.

```
Temporarily make the generated code loop forever, run the agent, then restore it.
```
- **Accept when:** the run ends by itself with a timeout message (about 15 seconds), not a hang.

## 7. Scope checks

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
| `eval(` / `exec(` | No output in the agent file |

## 8. Accept or reject

**ACCEPT** only if B1–B6, the weak-tests check, all three break-it tests and the scope checks pass.
**REJECT** on any failure. Name the failed test, quote what you saw, and ask for one specific fix.

- `Test B3 failed: the tests contain def validate_leave_request. Make validation reject that.`
- `Test B5 failed: there is no invalid case in the test data. Make the Python check require both valid and invalid cases, and run the cases against the code.`
- `Test B6 failed: there is no explanation before the approval question. Add the explain step and print it.`
- `The broken copy passed all your tests, so they are weak. Add a test for end before start.`
- `The agent hung on the infinite-loop test. Add a timeout.`

## 9. Acceptance sheet (hand this in)

| Test | Pass / Fail | Evidence |
| --- | --- | --- |
| B1 | | |
| B2 | | |
| B3 | | |
| B4 | | |
| B5 (test data) | | |
| B6 (explanation) | | |
| Weak-tests check (broken copy fails a test) | | |
| Break-it: fake tests rejected | | |
| Break-it: 3 attempts then stop | | |
| Break-it: infinite loop times out | | |
| Scope checks | | |
| **Decision** | ACCEPT / REJECT | One sentence why |
