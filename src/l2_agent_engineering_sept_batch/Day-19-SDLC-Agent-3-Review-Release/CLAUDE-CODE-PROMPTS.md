# Day 19 — Build Agent 3 and the Agent Chain with Claude Code (you verify and accept)

**Your role today:** you do not write code. Claude Code builds the review/release agent, then connects all three agents. You verify behaviour and accept or reject. Your trainer keeps the reference answers separately; you will not have copies. If a build keeps failing, see `IF-BUILD-FAILS.md`.

Run commands in Windows Command Prompt from the repository root. Start Claude Code with `ollama launch claude --model nemotron-3-ultra:cloud`.

**Time plan:** in class do Parts A and B up to test D4. Test D5 is optional practice afterwards.

## Part A — Agent 3: review and release

### A1. The specification

| | |
| --- | --- |
| **Input** | A **pull request**: a title, a description and a diff (lines starting with `+` are the added code), plus whether its tests passed |
| **Output** | Review findings (HIGH / MEDIUM / LOW) that each **quote the added line** they refer to, gate results, verification debt, changelog, release notes, **documentation**, final status |
| **Gates (plain Python)** | `tests passed`, `no HIGH findings`, `no forbidden calls` (`eval(`, `exec(`, `os.system(`, `TODO`) |
| **Documentation** | The model writes short documentation with exactly four headings (`## Purpose`, `## Parameters`, `## Returns`, `## Example`). Plain Python checks that all four headings and the function name are present; one retry; if still incomplete the status is **Blocked: documentation incomplete** |
| **Must** | If the model's review is not valid JSON, count it as a HIGH finding |
| **Must** | List non-HIGH findings as verification debt and show them at approval |
| **Must** | Any failed gate goes to a **blocked** status and skips release notes |
| **Must** | Ask a human to approve before status becomes **Released** |
| **Must not** | LangChain, extra files, touching other folders |

### A2. Prompt 1 — plan only (plan mode on)

```text
Create ONE new file: Day-19-SDLC-Agent-3-Review-Release\my_agent3.py,
a LangGraph review and release assistant.

Goal: review a pull request (title, description, unified diff) with the model (JSON findings
with severity HIGH/MEDIUM/LOW, each quoting the added line it refers to), apply quality gates in
plain Python, draft a changelog, release notes and short documentation, ask a human to approve,
then release. Documentation has exactly four headings: ## Purpose, ## Parameters, ## Returns,
## Example. Plain Python checks they and the function name are present; allow one retry; if still
incomplete the status is Blocked: documentation incomplete.
Gates (plain Python, not the model): tests passed; no HIGH finding; no forbidden calls
(eval(, exec(, os.system(, TODO) in the code.
Tell the reviewing model: HIGH means the code crashes or gives a wrong result for input that matches
the type annotations, or has a security flaw; None or wrong-type inputs are at most MEDIUM.
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
explicit conditional edges, interrupt for approval (InMemorySaver checkpointer and
Command(resume=...)). If the model review is not valid JSON,
treat it as a HIGH finding. Non-HIGH findings are listed as verification debt. A failed gate
goes to a blocked node and skips the release notes.
Use a hard-coded sample pull request (a title, a description and a unified diff that adds one
small leave-validation function; the code under review is the added lines) and tests_passed = True.
The added code must be clean working code with a docstring: no TODO, eval, exec, os.system or bare pass,
so that a good run can be released.
Print "Reviewing PR: <title>" first.
Graph shape: START -> review -> gates. After gates: all pass goes to release_notes -> docs -> approval;
any failure goes to blocked then END (no release notes). Docs incomplete after one retry goes to
blocked. After approval: yes goes to release then END; no goes to stopped then END. The approval
node only calls interrupt().
When the file is run (no arguments, no typing except the yes/no answer) it prints
"Reviewing PR: <title>", "Review findings:" (one line each: [SEVERITY] text (line: the added line)),
"Quality gates:" (PASS or FAIL for each gate), "Verification debt:", "Changelog:", "Release notes:" and
"Documentation:". Then it asks "Approve this release? (yes/no): " with input(). On yes it prints
"Status: Released". On no it prints "Status: Stopped: human declined the release". If a gate fails it
prints "Status: Blocked: <gate name>" and prints no release notes. The file must actually call the
graph under if __name__ == "__main__".
Make a short plan first (under 15 lines). Do not explore other folders or use research helpers.
Do not edit files yet.
```

**Accept the PLAN only if:** the input is a pull request (title, description, diff); the gates are Python (not model calls); unreadable review counts as HIGH; a blocked route skips release notes; there is a documentation step with a Python check; approval comes after the release notes and documentation; one file.

### A3. Prompt 2 — build and run

```
Implement the plan. Do not run the program yourself: it stops to ask me to type yes or no,
and you cannot type for me. When the file is written, check that it compiles with
uv run python -m py_compile Day-19-SDLC-Agent-3-Review-Release\my_agent3.py and fix any error.
Then tell me the exact command to run.
```

Claude Code cannot type at a prompt, so **you run the agent yourself** in a second Command Prompt window opened in the repository root, and read the PR header, findings, gate results, verification debt, changelog, release notes, documentation and final status:

```cmd
uv run python Day-19-SDLC-Agent-3-Review-Release\my_agent3.py
```

### A4. Acceptance tests

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| C1 | Full run | Run, answer `yes` | Findings, three gates, debt, changelog, notes, then `Released` (or `Blocked` if the reviewer called something HIGH — see note) |
| C2 | Human gate | Run, answer `no` | Status says the human declined; not Released |
| C3 | Gate: tests failed | Ask Claude Code: `Run the agent with tests_passed set to False and show the status.` | `Blocked ... tests passed` |
| C4 | Gate: forbidden call | `Run it with the code containing eval( and show the status.` | `Blocked ... no forbidden calls` |
| C5 | Gate: HIGH finding | `Pretend the model review returned one HIGH finding, run it, show the status.` | `Blocked ... no HIGH findings`, and no release notes printed |
| C6 | Broken review | `Pretend the model review is the text "hello" (not JSON). Run and show the status.` | Blocked, treated as a HIGH finding |
| C7 | PR review | In the C1 output, read the first lines | It starts with `Reviewing PR: <title>`, and each finding names the added line it refers to |
| C8 | Documentation | In a run that reaches approval, read the documentation printed before the question | Four headings: Purpose, Parameters, Returns, Example; it names the function; it is printed **before** you are asked to approve |
| C9 | Incomplete documentation | `Pretend the documentation never has an Example heading. Run and show the status.` | After one retry: `Blocked ... documentation incomplete` (this one can be optional practice afterwards) |

> **Note:** the reviewer model does not label severity the same way every run. If C1 comes back Blocked because of a HIGH finding, that is not a defect — run it again, and read the finding to decide whether you agree with it.

### A5. Scope checks

```cmd
dir Day-19-SDLC-Agent-3-Review-Release
findstr /i /c:"langchain" Day-19-SDLC-Agent-3-Review-Release\my_agent3.py
findstr /c:"interrupt" /c:"gpt-oss:120b-cloud" Day-19-SDLC-Agent-3-Review-Release\my_agent3.py
```

Pass when: only the new file was added; no `langchain`; `interrupt` and the model name are found.

## Part B — Connect the agents into a chain

### B1. The specification

| | |
| --- | --- |
| **Shape** | One parent graph. Agents 1, 2 and 3 are each their own compiled graph used as one node of the parent |
| **Between agents** | A small **handoff node** turns one agent's output into the next agent's input and records a line in a `handoffs` list. The Agent 2 → Agent 3 handoff packages Agent 2's code as a **pull request** (title, description, diff of added lines) |
| **Rule** | The chain must **stop** if an agent does not finish successfully |
| **Humans** | Each agent keeps its own approval pause; one checkpointer, one thread ID, a loop that asks you yes/no |
| **Must not** | Shared helper modules, imports from other days, LangChain |

### B2. Prompt 3 — plan only

```text
Create Day-19-SDLC-Agent-3-Review-Release\my_chain.py. Combine my three agents
(@Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py, @Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py,
@Day-19-SDLC-Agent-3-Review-Release\my_agent3.py) into ONE self-contained file.
Each agent stays its own compiled StateGraph and becomes a node of a parent graph that shares one
state schema. Between agents add small handoff nodes that convert outputs to inputs and append
a line to a handoffs list. The parent must stop if an agent does not finish successfully.
When run, it prints each agent's output in turn, asks that agent's yes/no question, and at the end prints
"Handoffs:" (exactly two entries) and "Final status: Released", "Final status: Stopped in Agent 1"
or "Final status: Stopped in Agent 2". Call the parent graph under if __name__ == "__main__" with this loop:
config = {"configurable": {"thread_id": "chain-1"}}; result = parent.invoke(state, config=config);
while "__interrupt__" in result: answer = input("Approve? (yes/no): ");
result = parent.invoke(Command(resume=answer.strip().lower() == "yes"), config=config).
Each agent keeps its own approval pause, so the loop runs once per agent.
Make the copied agents work inside the chain:
- Every approval node must accept the loop's True/False answer, for example
  approved = answer is True or str(answer).strip().lower() == "yes".
- Each agent sets state["status"] when it ends: Agent 1 "Agent 1 done" or "Stopped in Agent 1";
  Agent 2 "Code and tests approved" or a "Stopped: ..." text. The parent continues only on
  "Agent 1 done" and then "Code and tests approved"; anything else goes to a stop node that sets
  "Stopped in Agent 1" or "Stopped in Agent 2" and then END. Agent 3 ends with its own final status.
- Show each agent's output at its approval pause by building the text into the value passed to
  interrupt() (print nothing before interrupt), and print that value in the loop before input().
- Rename any functions or classes that clash between the three files (for example two "stopped"
  nodes or two "State" classes). The parent state lists every key the three agents use.
- Handoff 1 to 2 builds Agent 2's user story from Agent 1's stories and design. Handoff 2 to 3 builds
  the pull request: a title, a description, a diff with "+" in front of every code line, and
  tests_passed from Agent 2's result. Each handoff appends exactly one line to handoffs.
Use one checkpointer and one thread_id and loop on interrupts so I can answer yes/no.
Copy the three agents' code into this one file (do not load them with exec, import or file reads) and
use each compiled agent graph directly as a node: parent.add_node("agent1", agent1_graph).
No shared modules and no imports from other days. Make a short plan first (under 15 lines);
do not use research helpers.
```

**Accept the PLAN only if:** it shows three agent nodes, two handoff nodes, a stop rule after Agent 1 and Agent 2, approval nodes that accept True/False, each agent's output shown at its approval pause, one file, and no cross-day imports.

### B3. Prompt 4 — build and run

```
Implement the plan. Do not run the program yourself: it asks me for several yes or no answers.
When the file is written, check that it compiles with
uv run python -m py_compile Day-19-SDLC-Agent-3-Review-Release\my_chain.py and fix any error.
Then tell me the exact command to run.
```

Before the chain, check that your Day 17 and Day 18 agents run on their own (`my_agent1.py` ends with a design, `my_agent2.py` ends with `Status: Code and tests approved`); ask your trainer for a working copy if not.

Run the chain yourself in a second Command Prompt window:

```cmd
uv run python Day-19-SDLC-Agent-3-Review-Release\my_chain.py
```

Answer `yes` to every question first.

### B4. Acceptance tests for the chain

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| D1 | Happy path | `yes`, `yes`, `yes` | Ends `Released`; the output shows the stories and requirement lists (Agent 1), then the code and its explanation (Agent 2), then the PR review, gates and documentation (Agent 3) |
| D2 | Stop at Agent 2 | `yes`, then `no` | Final status `Stopped in Agent 2`; **no Agent 3 output at all** |
| D3 | Stop at Agent 1 | `no` at the first question | Final status `Stopped in Agent 1`; nothing from Agents 2 or 3 |
| D4 | Handoff log | Read the Handoffs list after D1 | Exactly **two** entries: Agent 1 → Agent 2 and Agent 2 → Agent 3 (no duplicates) |
| D5 | Real hand-off | Compare Agent 1's stories with what Agent 2 builds | The function Agent 2 builds is about the leave request from the stories |

### B5. Scope checks

```cmd
dir Day-19-SDLC-Agent-3-Review-Release
findstr /i /c:"langchain" Day-19-SDLC-Agent-3-Review-Release\my_chain.py
findstr /c:"import example" /c:"from example" /c:"import my_agent" /c:"from my_agent" Day-19-SDLC-Agent-3-Review-Release\my_chain.py
```

Pass when: only the expected new files exist; no output from either `findstr` (no LangChain, no imports from your other agent files).

## Accept or reject

**ACCEPT Agent 3** only if C1–C8 and its scope checks pass (C9 is optional). **ACCEPT the chain** only if D1–D5 and its scope checks pass. On any failure, quote the test number and what you saw, ask for one specific fix, and re-run only the failed test.

- `Test D4 failed: the handoffs list has 4 entries. Each handoff must be recorded once.`
- `Test D2 failed: Agent 3 still ran after I said no at Agent 2. The parent must stop.`
- `Test C5 failed: release notes were still written after the gate blocked. Skip them when blocked.`
- `Test C8 failed: there is no documentation before the approval question. Add the documentation step with the four headings and a Python check.`
- `Test C7 failed: the findings do not say which added line they refer to. Include the line in each finding.`

## Acceptance sheet (hand this in)

| Test | Pass / Fail | Evidence |
| --- | --- | --- |
| C1 | | |
| C2 | | |
| C3 | | |
| C4 | | |
| C5 | | |
| C6 | | |
| C7 (PR review) | | |
| C8 (documentation) | | |
| C9 (optional) | | |
| Agent 3 scope checks | | |
| D1 | | |
| D2 | | |
| D3 | | |
| D4 | | |
| D5 | | |
| Chain scope checks | | |
| **Decision: Agent 3** | ACCEPT / REJECT | |
| **Decision: Chain** | ACCEPT / REJECT | |
