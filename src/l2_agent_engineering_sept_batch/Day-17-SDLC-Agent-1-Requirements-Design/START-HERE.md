# Day 17: Agent 1 (Requirements → Design). START HERE (100 min)

**This is the only file you need today.** By the end, `my_agent1.py` is built by Claude Code and running.

**Your role:** you write no code. You give Claude Code a spec, check its plan, run what it builds, and accept or reject it.

## Before you start (about 10 min, once)

Do this ideally before class. It covers Days 17, 18 and 19.

Run these in Windows **Command Prompt**, from the course folder (the one containing `pyproject.toml`).

| Step | Command | You should see |
| --- | --- | --- |
| 1. Claude Code installed | `claude --version` | A version number. If not, ask your trainer for the install steps |
| 2. Sign in to Ollama | `ollama signin` | Signed in |
| 3. Models work | `ollama run gpt-oss:120b-cloud` and then `ollama run nemotron-3-ultra:cloud` (type `hi`, then `/bye` each time) | A reply from both. The agents you build call `gpt-oss:120b-cloud`; Claude Code itself runs on `nemotron-3-ultra:cloud` |
| 4. Install packages | `uv sync` | Finishes without errors |
| 5. You're in the course folder | `dir pyproject.toml` | The file is found |

**Claude Code in 60 seconds** (all you need for these three days):

| Do this | How |
| --- | --- |
| Start it (always this way, never plain `claude`) | `ollama launch claude --model nemotron-3-ultra:cloud` |
| Plan mode (it shows a plan and edits nothing) | Press **Shift+Tab** until the mode label says plan mode. Press again to leave it |
| Approve a plan | Choose the "yes / proceed" option when it offers one |
| Permission prompts | Claude Code asks before running commands or writing files. Read the path, then allow |
| Start a fresh chat | `/clear` |
| Quit | `/exit` |

## Setup (2 windows, both in the course folder)

- Window 1: `ollama launch claude --model nemotron-3-ultra:cloud`. This is where you paste prompts.
- Window 2: plain Command Prompt. This is where you run the agent. (Claude Code can't type `yes` for you.)

| Min     | Part                                 |
| ------- | ------------------------------------ |
| 0–10   | 1. The concept                       |
| 10–20  | 2. Plan (Prompt 1)                   |
| 20–35  | 3. Build and run (Prompt 2)          |
| 35–50  | 4. Tests                             |
| 50–60  | 5. Break it                          |
| 60–90  | 6. Claude Code feature: rule + skill |
| 90–100 | 7. Decide, wrap-up                   |

---

## 1. The concept (10 min)

```
Requirement --> [model writes stories] --> [Python checks them] --> [human says yes] --> Design
```

Agent 1 takes a short requirement and produces:

1. **User stories** ("As a / I want / so that")
2. **Given/When/Then** acceptance criteria
3. **Clarifying questions** for vague words ("quickly", "secure", "easy")
4. **Functional and non-functional** requirements
5. A short **design**, only after a human says yes

Ideas to teach:

- **Traceability:** each sentence gets an ID (R1, R2, R3). Every story names the ID it came from.
- **Decomposition:** "approve **or** reject" is two actions, so it must produce **two** stories.
- **Model suggests, Python validates, human approves.** The model never grades itself.
- **Bounded retry:** if the check fails, retry at most 2 times, then stop.

Good output looks like this (your wording will differ, the shape must match):

```output
Clarifying questions: how fast is "quickly"? what does "secure" require? ...
US-1 (R1): As an employee, I want to submit a leave request online, so that ...
   * Given logged in, when they submit, then the request is stored.
US-2 (R2): As a manager, I want to approve ...      US-3 (R2): ... reject ...
Functional: The system shall let managers approve / reject a request.
Non-functional: The system shall encrypt data in transit (security).
Approve these stories and criteria? (yes/no): yes
Status: Design ready
```

---

## 2. Plan first (10 min)

In Window 1 press **Shift+Tab until plan mode is on**, then paste:

```text
Create ONE new file: Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py,
a LangGraph requirements analyst agent.

Goal: convert a requirement into user stories, Given/When/Then acceptance criteria,
clarifying questions, functional requirements, non-functional requirements and a short
design, with human approval before the design. If a requirement sentence has more than
one action joined by "and" or "or", write a separate story for each action.
Context: the human approval uses interrupt and Command(resume=...). Use explicit
add_conditional_edges for every route.
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
no helper files, do not touch any other folder. Maximum 2 analysis attempts.
Verify: plain Python (not the model) must check: valid JSON, each story starts with "As a",
each criterion has given/when/then, every requirement ID is traced to a story, a sentence
with "and" or "or" has at least two stories, at least one clarifying question exists, and
both functional and non-functional requirement lists are non-empty.
Sample requirement: "Employees can request leave online. Managers approve or reject the
request quickly. The system must be secure and easy to use."
Graph shape: START -> number -> analyze -> validate. After validate: valid goes to approval; invalid
with fewer than 2 tries goes back to analyze; otherwise goes to stopped. After approval: yes goes to
design then END; no goes to stopped then END. The approval node only calls interrupt().
Every requirement sentence is numbered R1, R2, R3 (one per sentence) and every story names its R-number.
When the file is run (no arguments, no typing except the yes/no answer) it runs the sample
requirement through the graph and prints: "Clarifying questions for the stakeholder:" with each
question; "User stories:" with each story as "US-n (Rk): As a ..." followed by its Given/When/Then line;
"Functional requirements:" and "Non-functional requirements:" lists. Then it asks
"Approve these stories and criteria? (yes/no): " with input(). On yes it prints "Status: Design ready"
and the design. On no it prints "Status: Stopped: human rejected the stories" and no design. If
validation fails twice it prints "Status: Stopped: validation failed after 2 attempts". The file
must actually call the graph under if __name__ == "__main__".
Make a short plan first (under 15 lines). Do not explore other folders or use research helpers.
Do not edit files yet.
```

**Approve the plan only if it has all of these:**

- [ ] One file named `my_agent1.py`
- [ ] A step that numbers the sentences (R1, R2, R3)
- [ ] A model step producing stories, criteria, questions, functional and non-functional lists
- [ ] A **separate Python** step that validates (including decomposition and both lists)
- [ ] A retry route limited to 2, and a stop route
- [ ] A human approval pause before the design
- [ ] No LangChain, no extra files

If anything is missing, tell Claude Code exactly what and ask for a new plan.

---

## 3. Build and run (15 min)

Approve the plan, then paste:

```text
Implement the plan. Do not run the program yourself: it stops to ask me to type yes or no,
and you cannot type for me. When the file is written, check that it compiles with
uv run python -m py_compile Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py and fix any error.
Then tell me the exact command to run.
```

**Run it in Window 2** and type `yes` at the question:

```cmd
uv run python Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py
```

**The agent is now up and running.**

*If the build fails or stalls for more than 5 minutes:* tell your trainer. Don't keep retrying the same prompt. Send Claude Code one precise fix request instead (see the examples in Part 4).

---

## 4. Tests (15 min)

| #  | Test                                   | Pass when                                                                   |
| -- | -------------------------------------- | --------------------------------------------------------------------------- |
| A1 | Run, answer`yes`                     | Questions, stories, criteria, design printed. Status "Design ready"         |
| A2 | Count R-numbers                        | R1, R2, R3 each appear at least once                                        |
| A3 | Read the questions                     | One each for "quickly", "secure", "easy to use"                             |
| A7 | Read the two lists before the approval | Functional (submit/approve/reject) and non-functional (security, usability) |
| A8 | Stories tagged R2                      | **Two**: one approve, one reject                                      |
| A5 | Run again, answer`no`                | Status says stopped;**no design printed**                             |

**Fix loop (read this once):** the first build often has a bug. Send Claude Code **one short message** naming the failed test and what you saw. After every fix, **re-run all the tests**, not just the one that failed, because a fix can quietly break something that passed. Long, detailed fix messages can make Claude Code remove features. If it says "it works" or "it compiles" but shows no output, reply: `You said it works but did not run it. Run it and show me the output.` If two fixes don't work, ask your trainer.

If a test fails, **reject**. Tell Claude Code exactly what failed, for example:
`Test A8 failed: R2 has one story but the sentence says approve OR reject. Split it into two stories and make validation require that.`
Then re-run only the failed test.

---

## 5. Break it on purpose (10 min)

Paste in Window 1:

```text
Temporarily change the validation so it always reports a problem. Run the agent and show me
the output, then restore the original. I need to see that it stops after exactly 2 attempts.
```

**Accept when:** output shows two attempts, then a stop message, and the file is restored.

---

## 6. Claude Code feature: rule + skill (30 min)

**Concept.** A **rule** is a small instruction file in `.claude\rules\`. It's guidance, so Claude Code follows it *most* of the time, not always. A **skill** is a reusable `/command`: one command runs the same checklist every time.

> Claude Code will ask permission before writing in `.claude`. Check the path and allow it.

### 6a. Rules (15 min)

Plan mode, paste, then approve:

```text
Create two rule files, and nothing else.

1) .claude\rules\agent-style.md  (no paths header, always loaded). Content:
   - Every Python file you create must start with a first line that reads exactly: # AGENT FILE
   - Use ollama.chat(model="gpt-oss:120b-cloud", ...) directly. Never import LangChain.
   - One agent per file. Do not create helper modules.

2) .claude\rules\agent-files.md  which must begin with exactly this YAML header (the first line is three dashes):
---
paths:
  - "Day-*/my_*.py"
---
   Then the content:
   - Any change to one of these files must end by adding a last line comment: # REVIEWED BY RULE

Show me both files exactly as written.
```

- **Check:** two files; the second has a `paths:` header with `Day-*/my_*.py`.
- **R2 (rules are loaded):** restart `claude` and ask: `Without opening files, quote the rules from .claude\rules.` It must quote the always-on rule file (`agent-style.md`). The path-scoped file is *not* expected here: it loads only when a matching file is used (R4).
- **R4 (scoped rule fires):** ask Claude Code to create `Day-17-SDLC-Agent-1-Requirements-Design\my_demo.py` with one print line, then `Edit my_demo.py to also print done.` The last line of the file should become `# REVIEWED BY RULE`.
- **Poll (3 min):** restart `claude`. Ask three times (with `/clear` between): `Create Day-17-SDLC-Agent-1-Requirements-Design\scratch1.py that prints hello` (then scratch2, scratch3). Count how many files start with `# AGENT FILE`. There's no pass or fail: **the number is the lesson**. Rules are rarely 3 of 3.
- Afterwards ask Claude Code to delete `scratch*.py`.

### 6b. Skill (15 min)

Plan mode, paste, then approve:

````text
Create the file .claude\skills\accept-check\SKILL.md. Its content is the text between the lines
START and END below, character for character (not including those two lines). Do not add,
remove, reword or "improve" anything, do not add checks from other files or rules, and do not
create any other file. The word $ARGUMENTS must stay exactly as written, with the dollar sign.
START
---
name: accept-check
description: Run the scope checks on an agent file and print a PASS or FAIL table. Use when the user asks to check or accept an agent file.
argument-hint: <path to agent file>
---

Run the scope checks on the file $ARGUMENTS. Do not edit any file.

1. Run `findstr /i /c:"langchain" $ARGUMENTS`. PASS if nothing is printed.
2. Run `findstr /c:"gpt-oss:120b-cloud" $ARGUMENTS`. PASS if at least one line is printed.
3. Run `findstr /c:"interrupt" $ARGUMENTS`. PASS if at least one line is printed.

Then print a small table with one row per check and the word PASS or FAIL, and finish with
the line `DECISION: ACCEPT` only if all three passed, otherwise `DECISION: REJECT`.
END
Then show me the file.
````

Now use it on your agent:

```text
/accept-check Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py
```

**Pass when:** a table of three PASS and `DECISION: ACCEPT`.

---

## 7. Decide and wrap up (10 min)

Write **ACCEPT** or **REJECT** with one line of evidence. Accept only if A1–A8, the break-it test and `/accept-check` all passed.

**Homework:** run Agent 1 on your own two-sentence requirement. Hand in the requirement, your results, and one case where the output was weaker than you expected.

You're ready for Day 18 if you can name the 5 outputs, you checked a plan before approving, you saw the agent stop cleanly, and you know your rule-compliance number.

---

## Appendix: extra tests, scope checks and hand-in sheet (homework or spare time)

**Extra tests**

| #          | Test                                                                                                                                                                                             | Pass when                                                             |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| A4         | Read each story                                                                                                                                                                                  | Every story has a Given / When / Then line you could turn into a test |
| A6         | Ask Claude Code:`Run it again with this requirement: "The system sends an email when a leave request is approved." Give the approval answer by piping it in with: echo yes\| uv run python ...` | Still works; stories trace to R1                                      |
| Break-it 2 | Paste:`Temporarily make the model's reply invalid JSON (for example the text "hello"), run once, show the output, then restore the original.`                                                  | The agent reports a problem and retries or stops. It does not crash   |
| S3         | Ask Claude Code to create`bad.py` containing `import langchain`, then `/accept-check bad.py` (with its path)                                                                               | At least one FAIL and`DECISION: REJECT`                             |
| S4         | Compare the file before and after the skill ran                                                                                                                                                  | Unchanged. The skill edits nothing                                    |
| R5         | Ask Claude Code to delete`scratch*.py`                                                                                                                                                         | Files gone                                                            |

**Scope checks** (or just run `/accept-check`). Run in Window 2:

```cmd
dir Day-17-SDLC-Agent-1-Requirements-Design
findstr /i /c:"langchain" Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py
findstr /c:"gpt-oss:120b-cloud" Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py
findstr /c:"interrupt" Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py
```

| Check                  | Pass when                      |
| ---------------------- | ------------------------------ |
| `dir`                | Only`my_agent1.py` was added |
| `langchain`          | **No output**            |
| `gpt-oss:120b-cloud` | One or more lines              |
| `interrupt`          | One or more lines              |

**A hit can be a false alarm.** `findstr` reads text only. If `langchain` appears only inside a comment or a line saying *not* to use it, nothing is wrong, but the check still fails. Ask Claude Code to remove the word, or note it on your sheet and accept.

**Hand-in sheet**

| Test                                                      | Pass / Fail     | Evidence (one line of output) |
| --------------------------------------------------------- | --------------- | ----------------------------- |
| A1                                                        |                 |                               |
| A2                                                        |                 |                               |
| A3                                                        |                 |                               |
| A4                                                        |                 |                               |
| A5                                                        |                 |                               |
| A6                                                        |                 |                               |
| A7                                                        |                 |                               |
| A8                                                        |                 |                               |
| Break-it 1 (2 attempts then stop)                         |                 |                               |
| Break-it 2 (invalid JSON)                                 |                 |                               |
| Scope checks                                              |                 |                               |
| Rules: R3 number (out of 3 starting with`# AGENT FILE`) | n/a             |                               |
| Skill: S2`/accept-check` gives ACCEPT; S3; S4           |                 |                               |
| **Decision**                                        | ACCEPT / REJECT | One sentence why              |
