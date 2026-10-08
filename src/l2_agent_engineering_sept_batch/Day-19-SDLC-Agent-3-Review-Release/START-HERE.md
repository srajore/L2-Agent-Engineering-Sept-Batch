# Day 19: Hooks + Agent 3 (Review → Release) + the Agent Chain. START HERE (100 min)

**This is the only file you need today.** By the end, the guard hook and a read-only subagent are working, and `my_agent3.py` and `my_chain.py` (all three agents connected) are built by Claude Code and running.

**Your role:** you write no code. You specify, check the plan, run, and accept or reject.

**Setup (2 windows, both in the course folder):**
- Window 1: `ollama launch claude --model nemotron-3-ultra:cloud`. This is where you paste prompts.
- Window 2: plain Command Prompt. This is where you run the agents.

**Before you start:**
- Complete the "Before you start" table at the top of the Day 17 `START-HERE.md` (Claude Code installed, `ollama signin`, `uv sync`).
- Hooks (Part 2) need nothing from earlier days. Day 18 ran out of time before hooks, so you do them today.
- The subagent (Part 4A) needs nothing from earlier days. It was optional on Day 18, so you build it today.
- Agent 3 (Parts 3–5) needs nothing from earlier days.
- The chain (Parts 6–8) needs working `Day-17-...\my_agent1.py` and `Day-18-...\my_agent2.py`. Part 7 checks them first. If one is missing or broken, ask your trainer for a working copy.
- Part 9 (headless mode) uses the `/accept-check` skill from Day 17.

| Min | Part |
| --- | --- |
| 0–5 | 1. The concept |
| 5–25 | 2. Claude Code feature: the guard hook (do this first) |
| 25–31 | 3. Agent 3 plan (Prompt 1) |
| 31–41 | 4. Agent 3 build and run (Prompt 2) |
| 41–49 | 4A. Claude Code feature: a read-only subagent |
| 49–57 | 5. Agent 3 tests |
| 57–64 | 6. Chain concept and plan (Prompt 3) |
| 64–72 | 7. Chain build and run (Prompt 4) |
| 72–82 | 8. Chain tests |
| 82–90 | 9. Claude Code feature: headless mode |
| 90–100 | 10. Decide, wrap-up |

---

## 1. The concept (5 min)

```
Pull request --> [model reviews] --> [Python gates] --> release notes + docs --> [human yes] --> Released
                                          |
                                     any gate fails --> Blocked (no release notes)
```

Agent 3 input is a **pull request** (title, description, diff). Output: findings (HIGH/MEDIUM/LOW, each quoting the added line), gate results, verification debt, changelog, release notes, documentation, final status.

Ideas to teach:
- **Gates are plain Python, not the model:** tests passed; no HIGH finding; no forbidden calls (`eval(`, `exec(`, `os.system(`, `TODO`). The model can't talk its way past a gate.
- **Unreadable review = HIGH.** If the model's review isn't valid JSON, count it as a HIGH finding.
- **Verification debt:** non-HIGH findings are listed at approval so the human sees them.
- **Documentation** with four headings (Purpose, Parameters, Returns, Example), checked by Python.
- **A chain** is three agents (each its own graph) inside one parent graph, with small **handoff nodes** between them and a rule: **stop if an agent doesn't finish**.

---

## 2. Claude Code feature: the guard hook (20 min)

**Concept.** On Day 17 you measured that a rule is followed *most* of the time. A **hook** is a small program Claude Code runs automatically at a fixed moment, and it can **block** the action. A `PreToolUse` hook runs just before a tool and blocks by exiting with **code 2**. A rule asks politely; a hook says no every time. Hooks live in the `hooks` section of `.claude\settings.json`, and `/hooks` shows what is loaded.

Today's guard runs before every file edit or write and blocks it when the file is named `example.py` or `chain.py` (the trainer's reference files) or when it is inside a `Day-` folder other than the one named in `.claude\active-day.txt`. Your own `my_agent3.py` and `my_chain.py` are **not** blocked.

> **Expect a permission prompt.** Claude Code treats `.claude` as sensitive and will ask before writing there. Check the path is inside `.claude`, then allow it.

In Window 1 turn **plan mode on** (Shift+Tab), then paste:

```text
Create exactly three files for a hook guard, and nothing else. Each file's content is the text
between its START and END lines, character for character (not including those lines). Do not add,
remove, reword or "improve" anything, and do not copy anything from any other settings file. If
.claude\settings.json already exists, change only its "hooks" key and keep everything else.

FILE 1: .claude\active-day.txt
START
Day-19-SDLC-Agent-3-Review-Release
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

**Approve the plan only if:**
- [ ] It creates exactly three things: `active-day.txt`, `guard.py`, and the `hooks` entry in `settings.json`
- [ ] The event is `PreToolUse` with matcher `Edit|Write`
- [ ] The script blocks by exiting with code 2
- [ ] Nothing else in the repository changes

Approve it, then **quit and restart Claude Code** (`ollama launch claude --model nemotron-3-ultra:cloud`) because settings load at start. Accept the trust dialog if asked.

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| H1 | Hook is loaded | `/hooks` | A `PreToolUse` hook with matcher Edit-or-Write is listed |
| H2 | Allowed edit works | `Create Day-19-SDLC-Agent-3-Review-Release\hook_ok.txt containing hello.` | The file is created |
| H3 | Reference names protected | `Create a file named chain.py in Day-19-SDLC-Agent-3-Review-Release containing a print line.` | **Refused** with the guard's message; no file created |
| H4 | Other day protected | `Create Day-18-SDLC-Agent-2-Design-Code-Test\hook_no.txt containing hi.` | **Refused**: "today's folder is Day-19-..." |

Then ask Claude Code: `Delete hook_ok.txt.`

**Trouble?** If every edit is refused, `active-day.txt` has the wrong folder name: ask Claude Code to show it. If the hook errors instead of blocking, ask Claude Code to remove the `hooks` key from `.claude\settings.json`, restart, and carry on: the rest of the day does not need the hook.

**Why `active-day.txt`?** Set it to the day you are on. It stops Claude Code from wandering into another day's work and protects the reference answers.

---

## 3. Agent 3 plan (6 min)

In Window 1 press **Shift+Tab until plan mode is on**, then paste:

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

**Approve the plan only if:**
- [ ] Input is a pull request (title, description, diff)
- [ ] Gates are Python, not model calls
- [ ] An unreadable review counts as HIGH
- [ ] A blocked route skips the release notes
- [ ] A documentation step with a Python check
- [ ] Approval comes **after** release notes and documentation
- [ ] One file, no LangChain

---

## 4. Agent 3 build and run (10 min)

```text
Implement the plan. Do not run the program yourself: it stops to ask me to type yes or no,
and you cannot type for me. When the file is written, check that it compiles with
uv run python -m py_compile Day-19-SDLC-Agent-3-Review-Release\my_agent3.py and fix any error.
Then tell me the exact command to run.
```

**Run it in Window 2** and type `yes`:

```cmd
uv run python Day-19-SDLC-Agent-3-Review-Release\my_agent3.py
```

**Agent 3 is now up and running.**

*If it stalls for more than 5 minutes:* tell your trainer. Don't keep retrying the same prompt. Send Claude Code one precise fix request instead (see Part 5).

---

## 4A. Claude Code feature: a read-only subagent (8 min)

**Concept.** A **subagent** is a specialist helper with its own focus and a **short list of allowed tools**. It lives in `.claude\agents\<name>.md` and its header lists `name`, `description` (when to use it) and `tools` (the **only** tools it may use). A hook blocks an action; a subagent simply has no power to do it. A reviewer with only `Read, Grep, Glob` cannot change a file even if it wants to. You call it in plain words: "Use the agent-reviewer subagent to review ...".

In Window 1 turn **plan mode on** (Shift+Tab), then paste. (Claude Code will ask before writing in `.claude`: check the path and allow it.)

```text
Create the subagent .claude\agents\agent-reviewer.md.
Header: name agent-reviewer; description: read-only reviewer that tries to find ways an agent
file could fail; tools: Read, Grep, Glob only. Do not add a model line.
Body: you are a strict read-only reviewer of small LangGraph agent files and never edit files.
Read the file you are given and report a numbered list of at most 5 items: the most likely ways
it could fail or be unsafe (missing validation, no retry limit, no human approval, unbounded
loop, model output trusted without checks). For each item, say how a person could test it
without reading code. End with the line REVIEWER: DONE.
Show me the file.
```

**Approve the plan only if:**
- [ ] It creates exactly one file, `.claude\agents\agent-reviewer.md`
- [ ] `tools` lists only Read, Grep, Glob
- [ ] The body says it never edits files

Approve it, then **quit and restart Claude Code** so the subagent loads. Run `/agents` to see it listed.

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| SA1 | File is right | Ask Claude Code to show `.claude\agents\agent-reviewer.md` | `tools` lists only Read, Grep, Glob; it says it never edits |
| SA2 | It reviews | `Use the agent-reviewer subagent to review Day-19-SDLC-Agent-3-Review-Release\my_agent3.py` | A numbered list of at most 5 items, each with a way to test it, ending `REVIEWER: DONE` |
| SA3 | It cannot edit | `Use the agent-reviewer subagent to fix the problems it found in my_agent3.py.` | `my_agent3.py` does **not** change (it has no edit tool) |
| SA4 | Use its findings (optional) | Turn one finding into a break-it prompt and run it | You have a new test you did not have before |

**Trouble?** If the subagent is not listed or errors, ask Claude Code to show the file header and fix only the header, then restart. If it still fails, tell your trainer and carry on: nothing later depends on it.

---

## 5. Agent 3 tests (8 min)

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| C1 | Full run | Run, answer `yes` | Findings, 3 gates, debt, changelog, notes, then `Released` |
| C7 | PR review | Read the first lines | Starts `Reviewing PR: <title>`; each finding names the added line |
| C8 | Documentation | Read before the question | Four headings, names the function, printed **before** approval |
| C2 | Human gate | Run, answer `no` | Status says declined; not Released |
| C4 | Forbidden call | Ask Claude Code: `Run it with the code containing eval( and show the status.` | `Blocked ... no forbidden calls` |
| C5 | HIGH finding | Ask: `Pretend the model review returned one HIGH finding, run it, show the status.` | `Blocked ... no HIGH findings`, **no release notes printed** |

**Note:** the reviewer model doesn't label severity the same way every run. If C1 comes back Blocked because of a HIGH finding, it isn't a defect. Run again and read the finding to decide whether you agree. (C2 needs a run that reaches the question, so re-run if the first one is Blocked.)

**Fix loop (read this once):** the first build often has a bug. Send Claude Code **one short message** naming the failed test and what you saw. After every fix, **re-run all the tests**, not just the one that failed, because a fix can quietly break something that passed. Long, detailed fix messages can make Claude Code remove features. If it says "it works" or "it compiles" but shows no output, reply: `You said it works but did not run it. Run it and show me the output.` If two fixes don't work, ask your trainer.

Reject with a precise message, for example: `Test C5 failed: release notes were still written after the gate blocked. Skip them when blocked.`

**Decision for Agent 3:** ACCEPT only if C1, C2, C4, C5, C7 and C8 pass.

---

## 6. The chain: concept and plan (7 min)

Three agents become three **nodes** of one parent graph. Between them sit **handoff nodes** that convert one agent's output into the next agent's input and record a line in a `handoffs` list. The Agent 2 → Agent 3 handoff packages Agent 2's code as a pull request.

In plan mode, paste:

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

**Approve the plan only if** it shows: 3 agent nodes, 2 handoff nodes, a stop rule after Agent 1 and Agent 2, approval nodes that accept True/False, each agent's output shown at its approval pause, one file, no cross-day imports.

---

## 7. Chain build and run (8 min)

**First check your inputs (2 min).** The chain copies your Day 17 and Day 18 agents, so each must run on its own. In Window 2 run each and type `yes`:

```cmd
uv run python Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py
uv run python Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py
```

Agent 1 should end with a design; Agent 2 should end with `Status: Code and tests approved`. If either crashes, don't start the chain: ask your trainer for a working copy.

```text
Implement the plan. Do not run the program yourself: it asks me for several yes or no answers.
When the file is written, check that it compiles with
uv run python -m py_compile Day-19-SDLC-Agent-3-Review-Release\my_chain.py and fix any error.
Then tell me the exact command to run.
```

**Run it in Window 2.** Answer `yes` to every question:

```cmd
uv run python Day-19-SDLC-Agent-3-Review-Release\my_chain.py
```

**The full SDLC chain is now up and running.**

*If it stalls:* tell your trainer, or send Claude Code one precise fix request (see Part 8).

---

## 8. Chain tests (12 min)

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| D1 | Happy path | `yes`, `yes`, `yes` | Ends `Released`. You see stories (Agent 1), then code + explanation (Agent 2), then PR review, gates, docs (Agent 3) |
| D2 | Stop at Agent 2 | `yes`, then `no` | `Stopped in Agent 2`; **no Agent 3 output at all** |
| D3 | Stop at Agent 1 | `no` at the first question | `Stopped in Agent 1`; nothing from Agents 2 or 3 |
| D4 | Handoff log | Read the Handoffs list after D1 | Exactly **two** entries: 1→2 and 2→3 |

Reject with a precise message, for example: `Test D2 failed: Agent 3 still ran after I said no at Agent 2. The parent must stop.`

**Note:** if D1 ends `Blocked by quality gates: no HIGH findings`, that is the same reviewer variance as Agent 3. Run D1 again and read the finding.

**Decision for the chain:** ACCEPT only if D1–D4 pass.

---

## 9. Claude Code feature: headless mode (10 min)

**Concept.** `claude -p "..."` runs one prompt, prints the answer, and exits. No chat. Use it for repeatable checks and automation. In headless mode nothing can ask permission, so you list the allowed tools with `--allowedTools`.

This needs the `/accept-check` skill from Day 17. Because Claude Code runs through Ollama here, use:

```cmd
ollama launch claude --model nemotron-3-ultra:cloud -y -- -p "/accept-check Day-19-SDLC-Agent-3-Review-Release\my_agent3.py" --allowedTools "Bash,Read"
```

**Pass when:** the PASS table and `DECISION: ACCEPT` print, then the command returns to the prompt.

If that form doesn't work on your machine (tell your trainer), run `/accept-check Day-19-SDLC-Agent-3-Review-Release\my_agent3.py` inside a normal Claude Code session. The check is identical.

*(5 min, optional)* Skim the **driver's check** in the appendix and tick what you can already prove.

---

## 10. Decide and wrap up (8 min)

Write **ACCEPT** or **REJECT** for Agent 3 and for the chain, each with one line of evidence.

**Homework:** tests C3, C6, C9, D5; finish the driver's check; and fill in the acceptance sheets for Days 17–19.

You've finished the course if you can explain why the gates are Python and not the model, and how the chain stops when an agent doesn't finish.

---

## Appendix: extra tests, scope checks, driver's check and hand-in sheet (homework or spare time)

**Extra tests**

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| C3 | Tests failed | Ask Claude Code: `Run the agent with tests_passed set to False and show the status.` | `Blocked ... tests passed` |
| C6 | Broken review | `Pretend the model review is the text "hello" (not JSON). Run and show the status.` | Blocked, treated as a HIGH finding |
| C9 | Incomplete docs | `Pretend the documentation never has an Example heading. Run and show the status.` | After one retry: `Blocked ... documentation incomplete` |
| D5 | Real hand-off | Compare Agent 1's stories with what Agent 2 builds | The function Agent 2 builds is about the leave request from the stories |
| H5 | Hook follows the file | Ask Claude Code to change `.claude\active-day.txt` to the Day 18 folder name, then repeat H4 with the Day 18 path | Now allowed. Change it back to the Day 19 name afterwards |
| H6 | Reading is not blocked | Ask Claude Code to read `pyproject.toml` and say how many lines it has | It answers (the guard only watches edits and writes) |
| I5 | Reviewer attack (uses the Part 4A subagent) | `Use the agent-reviewer subagent to review my_chain.py` | At most 5 failure ideas; turn one into a test and run it |
| P2 | Headless reject | Run the headless command from Part 9 on a file with `import langchain` | `DECISION: REJECT` |

**Scope checks.** Run in Window 2:

```cmd
dir Day-19-SDLC-Agent-3-Review-Release
findstr /i /c:"langchain" Day-19-SDLC-Agent-3-Review-Release\my_agent3.py
findstr /c:"interrupt" /c:"gpt-oss:120b-cloud" Day-19-SDLC-Agent-3-Review-Release\my_agent3.py
findstr /i /c:"langchain" Day-19-SDLC-Agent-3-Review-Release\my_chain.py
findstr /c:"import example" /c:"from example" /c:"import my_agent" /c:"from my_agent" Day-19-SDLC-Agent-3-Review-Release\my_chain.py
```

Pass when: only the expected new files exist; the `langchain` and import checks print nothing; `interrupt` and the model name are found in `my_agent3.py`.

**A hit can be a false alarm.** `findstr` reads text only. If `langchain` or `pytest` appears only inside a comment or inside a prompt telling the model *not* to use it, nothing is wrong, but the check still fails. Ask Claude Code to remove the word, or note it on your sheet and accept.

**Your Claude Code driver's check.** Tick each task you can prove.

| # | Task | Proof |
| --- | --- | --- |
| 1 | Install and sign in | `claude --version` |
| 2 | Start Claude Code in a project folder with the right model | The launch command you used |
| 3 | Use plan mode and reject a bad plan | A plan you sent back, with your reason |
| 4 | Use `@file` to point at a file | The command you typed |
| 5 | Read a diff and reject a change | Your reject message |
| 6 | Explain allow, deny and the trust dialog | One sentence each |
| 7 | (Optional, not covered in these three days) Add an MCP server at project scope | `.mcp.json` entry |
| 8 | Create a rule and explain why it is not a guarantee | Your R3 number from Day 17 |
| 9 | Create and run a skill | `/accept-check` output |
| 10 | Create a hook that blocks an action, and prove it | The guard's message (H3 or H4) |
| 11 | Create a read-only subagent and prove it cannot edit | Part 4A test SA3 |
| 12 | Run Claude Code headless | The `claude -p` output |
| 13 | Build and accept three agents and a chain | Your acceptance sheets for Days 17–19 |

**Hand-in sheet**

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
| Hook H1–H4 | | |
| Subagent SA1–SA3 | | |
| Headless P1 / P2 | | |
| Driver's check rows ticked (out of 13) | | |
| **Decision: Agent 3** | ACCEPT / REJECT | |
| **Decision: Chain** | ACCEPT / REJECT | |
