# Day 17 — Build Agent 1 with Claude Code (you verify and accept)

**Your role today:** you do not write code. You give Claude Code a specification, review its *plan*, run what it builds, and **accept or reject** it using the acceptance tests below. Your trainer keeps the reference answer separately; you will not have a copy. If a build keeps failing, see `IF-BUILD-FAILS.md`.

Run every command in Windows Command Prompt from the repository root. Start Claude Code with `ollama launch claude --model nemotron-3-ultra:cloud`.

## 1. The specification (what Agent 1 must do)

| | |
| --- | --- |
| **Input** | A short business requirement in plain text |
| **Output** | User stories, Given/When/Then acceptance criteria, clarifying questions, **functional and non-functional requirements**, and a short design |
| **Must** | Number each requirement sentence (R1, R2...) and trace every story back to one |
| **Must** | **Decompose**: a sentence with more than one action ("approve **or** reject") becomes one story per action |
| **Must** | Ask a clarifying question for each vague word ("quickly", "secure", "easy") |
| **Must** | Check the model's output with plain-Python rules, retry at most 2 times, then stop |
| **Must** | Pause for a human yes/no before writing the design |
| **Must not** | Use LangChain, extra helper files, or edit any other day's folder |
| **Model** | `ollama.chat(model="gpt-oss:120b-cloud", ...)`, LangGraph `StateGraph` |

## 2. Prompt 1 — ask for a plan only

Press Shift+Tab until plan mode is on, then paste:

```
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

> **Tip from testing:** without that "short plan" line, Claude Code spent 8 to 23 minutes researching before it answered. Keep the line.

### Accept the PLAN only if it has all of these

- [ ] One file, named `my_agent1.py`
- [ ] A step that numbers the requirement sentences (R1, R2, R3)
- [ ] A step where the model produces stories, criteria, questions, and functional and non-functional requirements
- [ ] A separate step where Python (not the model) validates the output, including the decomposition and the two requirement lists
- [ ] A retry route with a limit of 2, and a stop route
- [ ] A human approval pause before the design is written
- [ ] No LangChain, no extra files

If anything is missing, reply with exactly what is missing and ask for a new plan. Do not approve a plan you cannot tick.

## 3. Prompt 2 — build and run

After you approve the plan:

```
Implement the plan. Do not run the program yourself: it stops to ask me to type yes or no,
and you cannot type for me. When the file is written, check that it compiles with
uv run python -m py_compile Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py and fix any error.
Then tell me the exact command to run.
```

Claude Code cannot type at a prompt, and it asks your permission before running programs. So **you run the agent yourself**, in a second Command Prompt window opened in the repository root:

```cmd
uv run python Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py
```

When asked "Approve these stories and criteria?", type `yes` first.

## 4. Acceptance tests (run them, record the result)

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| A1 | Full run | Run it, answer `yes` | Questions, stories, criteria and a design are printed; status is "Design ready" |
| A2 | Coverage | Count R-numbers shown beside the stories | R1, R2 and R3 each appear at least once |
| A3 | Ambiguity | Read the questions | There is a question for "quickly", for "secure" and for "easy to use" |
| A4 | Criteria | Read each story | Every story has a Given / When / Then line you could turn into a test |
| A5 | Human gate | Run again, answer `no` | Status says stopped; **no design is printed** |
| A7 | Functional and non-functional requirements | Read the two lists printed before the approval question | Functional lists what the system does (submit, approve, reject). Non-functional lists qualities (security, usability, speed) and covers "secure" and "easy to use" |
| A8 | Decomposition | Look at the stories tagged R2 | There are **two** stories tagged R2: one for approving and one for rejecting |
| A6 | Different input | Ask Claude Code: `Run it again with this requirement: "The system sends an email when a leave request is approved." Give the approval answer by piping it in with: echo yes\| uv run python ...` (or change the requirement and run it yourself) | It still works; stories trace to R1 |

## 5. Prove the safety rules by breaking things on purpose

Do not read code. Ask Claude Code to attack its own work and show you the output.

```
Temporarily change the validation so it always reports a problem. Run the agent and show me
the output, then restore the original. I need to see that it stops after exactly 2 attempts.
```

- **Accept when:** the output shows two analysis attempts and then a stop message, and Claude Code confirms the file was restored.

```
Temporarily make the model's reply invalid JSON (for example the text "hello"), run once,
show the output, then restore the original.
```

- **Accept when:** the agent reports a problem and retries or stops instead of crashing.

## 6. Scope checks (no code reading needed)

```cmd
dir Day-17-SDLC-Agent-1-Requirements-Design
findstr /i /c:"langchain" Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py
findstr /c:"gpt-oss:120b-cloud" Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py
findstr /c:"interrupt" Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py
```

| Check | Pass when |
| --- | --- |
| `dir` | Only `my_agent1.py` was added (plus the existing files) |
| `findstr ... langchain` | **No output** (nothing found) |
| `findstr ... gpt-oss:120b-cloud` | One or more lines found |
| `findstr ... interrupt` | One or more lines found |

## 7. Accept or reject

**ACCEPT** only if A1 to A8 pass, both break-it tests pass, and all four scope checks pass.
**REJECT** if any one fails. Rejecting is the correct and useful outcome: tell Claude Code *exactly* which test failed and what you saw, ask for a fix, then run only the failed tests again.

Useful reject messages:

- `Test A3 failed: there is no clarifying question about "secure". Fix it and rerun.`
- `Test A8 failed: R2 has one story but the sentence says approve OR reject. Split it into two stories and make validation require that.`
- `Test A7 failed: there is no non-functional requirement list. Add it and make validation require it.`
- `The scope check found "langchain" in my_agent1.py. Remove it, keep to CLAUDE.md, and rerun.`
- `You said it works but did not run it. Run it and show me the output.`

## 8. Acceptance sheet (hand this in)

| Test | Pass / Fail | Evidence (paste one line of output) |
| --- | --- | --- |
| A1 | | |
| A2 | | |
| A3 | | |
| A4 | | |
| A5 | | |
| A6 | | |
| A7 | | |
| A8 | | |
| Break-it 1 (2 attempts then stop) | | |
| Break-it 2 (invalid JSON) | | |
| Scope checks | | |
| **Decision** | ACCEPT / REJECT | One sentence why |
