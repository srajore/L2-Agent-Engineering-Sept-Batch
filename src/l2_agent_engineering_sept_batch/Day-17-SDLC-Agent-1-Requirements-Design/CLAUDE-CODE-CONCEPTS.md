# Day 17 — Claude Code Concepts: Rules and Skills

**Your role:** you do not write these files. You specify them, let Claude Code create them, and **prove** they behave. Do this block **after** Agent 1 is built and running (about 30 minutes), so the agent is working before any extra material. The same prompts and tests are in `START-HERE`, Part 6, which is the file to follow in class. Nothing here depends on earlier days. The trainer keeps the reference files separately.

> **Expect a permission prompt.** Claude Code treats the `.claude` folder as sensitive, so it will **ask you before it writes there**. Read the prompt, check the file path is inside `.claude`, and allow it. (In our own tests, when that permission was refused, Claude Code printed the file contents instead so we could save them by hand.)

## Time plan

Both topics are covered in class. **Practise** = you do the tests. **Introduce** = the short version, shown or done as a class.

| Item | In class | Depth |
| --- | --- | --- |
| Rules R1, R2, R4 | About 15 min (includes the R3 poll) | Practise |
| R3 (how often is a rule followed?) | A class poll: each learner reports their number | Introduce |
| Skill S1 (create it); S2 after the agent is built | About 10 min | Practise |
| R5 (clean up), S3, S4 | Optional later | |

## Part A — Rules: instructions that load by folder or file

| Concept | What to know |
| --- | --- |
| Where | Markdown files in `.claude\rules\` |
| Always-on rule | A rule file with no `paths:` header loads at the start of every session |
| Path-scoped rule | A rule file starting with a `paths:` header (a list of file patterns) loads only when Claude Code works with matching files |
| Rules vs CLAUDE.md | `CLAUDE.md` is the one big file. Rules split instructions into small files, some of them scoped |
| Honest limit | Rules are **guidance**. Claude Code can read a rule and still not follow it. Day 18 shows what enforces instead |

### Prompt (plan mode, then approve)

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

### Tests

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| R1 | Files are exact | Read what Claude Code shows | Two files; the second has a `paths:` header with `Day-*/my_*.py` |
| R2 | Rules are loaded | Restart `claude`, ask: `Without opening files, quote the rules from .claude\rules.` | It quotes the always-on rule file. The path-scoped file loads only when a matching file is used (see R4) |
| R3 | **Measure compliance** | Ask three times (use `/clear` between): `Create Day-17-SDLC-Agent-1-Requirements-Design\scratch1.py that prints hello` (then scratch2, scratch3). Check each file's first line with `findstr /n "." file` or ask Claude Code | Record how many of 3 start with `# AGENT FILE`. **There is no pass or fail here: the lesson is the number** |
| R4 | Scoped rule fires | Create `my_demo.py` in the Day 17 folder with one print line, then ask: `Edit my_demo.py to also print done.` | The last line becomes `# REVIEWED BY RULE` |
| R5 | Clean up | Ask Claude Code to delete `scratch*.py` and `my_demo.py` | Files gone |

**Expected learning:** rules are loaded (R2) and followed *most* of the time, but R3 is rarely 3 of 3. When something must never be skipped, a rule is not enough. That is Day 18.

## Part B — Skills: reusable procedures you call with a slash command

| Concept | What to know |
| --- | --- |
| Where | `.claude\skills\<name>\SKILL.md` (project) or `~\.claude\skills\<name>\SKILL.md` (you, everywhere) |
| Header | `name`, `description` (when to use it), optional `argument-hint` |
| Call it | Type `/name arguments`. Claude Code can also pick it itself when the description matches |
| `$ARGUMENTS` | Inside the skill, replaced with whatever you typed after the name |
| Why | One command runs the same checklist every time, the same way for every learner |

### Prompt (plan mode, then approve)

```text
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
```

### Tests

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| S1 | Skill file is right | Read the file Claude Code shows and compare it with the text in the prompt | Identical: the same three `findstr` checks, `$ARGUMENTS` written with the dollar sign, a line saying it edits nothing, and no extra checks. If Claude Code "improved" it, reject and ask for the exact text |
| S2 | Accepts a good file | After the Agent 1 build: `/accept-check Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py` | Table of three PASS and `DECISION: ACCEPT` |
| S3 | Rejects a bad file | Ask Claude Code to create `bad.py` containing the line `import langchain`, then `/accept-check bad.py` (with its path) | At least one FAIL and `DECISION: REJECT` |
| S4 | It edits nothing | Compare the file before and after the skill ran | Unchanged |

Your Day 17 scope checks now take one command: use `/accept-check` for them.

## Accept or reject

**ACCEPT** only if R1, R2, R4, R5 and S1–S4 pass and you recorded the R3 number. Reject with evidence.

## Acceptance sheet (hand this in)

| Test | Pass / Fail | Evidence |
| --- | --- | --- |
| R1 | | |
| R2 | | |
| R3 (number out of 3 that started with `# AGENT FILE`) | n/a | |
| R4 | | |
| R5 | | |
| S1 | | |
| S2 | | |
| S3 | | |
| S4 | | |
| **Decision** | ACCEPT / REJECT | |
