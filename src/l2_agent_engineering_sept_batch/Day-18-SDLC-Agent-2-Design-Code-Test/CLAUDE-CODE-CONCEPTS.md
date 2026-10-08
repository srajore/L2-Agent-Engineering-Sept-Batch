# Day 18 — Claude Code Concepts: Hooks and Subagents

**Your role:** you do not write these files. You specify them, let Claude Code create them, and **prove** they behave. Do the hook **after** Agent 2 is built and running (about 23 minutes, `START-HERE` Part 7). The subagent is optional practice (appendix of `START-HERE`). The same prompts and tests are in `START-HERE`, which is the file to follow in class. Nothing here depends on earlier days. The trainer keeps the reference files separately.

> **Expect a permission prompt.** Claude Code treats the `.claude` folder as sensitive, so it will **ask you before it writes there**. Read the prompt, check the file path is inside `.claude`, and allow it. Editing `settings.json` there is the same: you will be asked.

## Time plan

Both topics are covered in class. **Practise** = you do the tests. **Introduce** = the short version.

| Item | In class | Depth |
| --- | --- | --- |
| Guard hook H1–H4 | About 23 min | Practise |
| Subagent Part B: create it (A1) and run one review (A2) | Optional practice | |
| H5, H6, H7; subagent A3 and A4 | Optional practice | |

## Part A — Hooks: rules that are enforced, not just suggested

On Day 17 you measured that a rule is followed *most* of the time. A **hook** is different: it is a small program that Claude Code runs automatically at a fixed moment, and it can **block** the action.

| Concept | What to know |
| --- | --- |
| Where | The `hooks` section of `.claude\settings.json` (project, shared) or your local settings |
| Event | `PreToolUse` runs just before a tool runs (can block it). `PostToolUse` runs after. Others exist (`SessionStart`, `UserPromptSubmit`, `Stop`) |
| Matcher | Which tools it applies to, for example `Edit` or `Write` joined with a pipe character |
| Command | What to run. Claude Code sends the tool's details to it as JSON |
| Block | The hook **exits with code 2** and prints a message. Claude Code stops the action and shows the message |
| `/hooks` | Shows the hooks Claude Code has loaded |
| Rule vs hook | A rule asks politely. A hook can say no every time |

### The specification you will give Claude Code

A guard that runs before every file edit or write and **blocks** it when:

1. the file is named `example.py` or `chain.py` (the trainer's reference files), or
2. the file is inside a `Day-` folder other than the one named in `.claude\active-day.txt`.

Everything else is allowed. The blocked message must say why.

### Prompt (plan mode, then approve)

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

### Accept the PLAN only if

- [ ] It creates exactly three things: `active-day.txt`, `guard.py`, and the entry in `settings.json`
- [ ] The hook event is `PreToolUse` with matcher `Edit|Write`
- [ ] The script blocks by exiting with code 2 (not just by printing)
- [ ] Nothing else in the repository is changed

### Tests

After approving, **restart `claude`** (settings load at start) and accept the trust dialog if asked.

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| H1 | Hook is loaded | `/hooks` | A `PreToolUse` hook with matcher Edit-or-Write is listed |
| H2 | Allowed edit works | Ask: `Create Day-18-SDLC-Agent-2-Design-Code-Test\hook_ok.txt containing hello.` | The file is created |
| H3 | Reference names protected | Ask: `Create a file named example.py in Day-18-SDLC-Agent-2-Design-Code-Test containing a print line.` | **Refused** with the guard's message; no file created |
| H4 | Other day protected | Ask: `Create Day-17-SDLC-Agent-1-Requirements-Design\hook_no.txt containing hi.` | **Refused**: "today's folder is Day-18-..." |
| H5 | Hook follows the file | Ask Claude Code to change `active-day.txt` to the Day 17 folder name, then repeat H4 | Now allowed. Change it back to the Day 18 name afterwards |
| H6 | Reading is not blocked | Ask Claude Code to read `pyproject.toml` and say how many lines it has | It answers (the guard only watches edits and writes) |
| H7 | Clean up | Ask Claude Code to delete `hook_ok.txt` and `hook_no.txt` if created | Files gone |

**Why `active-day.txt`?** From now on set it to the day you are on. It stops Claude Code from wandering into another day's work, and it protects the reference answers.

### Another way to deny: permission rules

A permission **deny rule** in `.claude\settings.local.json`, such as `"Edit(Day-*/example.py)"`, also blocks an edit with no script. A hook is better when the decision needs logic (like "any day except today's"). Use deny rules for simple fixed blocks.

## Part B — Subagents: a specialist with limited powers

| Concept | What to know |
| --- | --- |
| Where | `.claude\agents\<name>.md` (project) or `~\.claude\agents\<name>.md` (you, everywhere) |
| Header | `name`, `description` (when to use it), `tools` (the **only** tools it may use), `model` |
| Why | A separate helper with its own focus and a **short list of allowed tools**. A read-only reviewer cannot change anything even if it wants to |
| Call it | Ask in plain words: "Use the agent-reviewer subagent to review ..." |

### Prompt (plan mode, then approve)

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

### Tests

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| A1 | File is right | Read it | `tools` lists only Read, Grep, Glob; it says it never edits |
| A2 | It reviews | After the Agent 2 build: `Use the agent-reviewer subagent to review Day-18-SDLC-Agent-2-Design-Code-Test\my_agent2.py` | A numbered list of at most 5 items, each with a way to test it, ending `REVIEWER: DONE` |
| A3 | It cannot edit | Ask: `Use the agent-reviewer subagent to fix the problems it found in my_agent2.py.` | The file does **not** change (it has no edit tool) |
| A4 | Use its findings | Turn one finding into a break-it prompt from today's lab and run it | You have a new test you did not have before |

## Accept or reject

**ACCEPT** only if H1–H7 and A1–A4 pass. Reject with evidence: name the test, quote what you saw, ask for one fix.

## Acceptance sheet (hand this in)

| Test | Pass / Fail | Evidence |
| --- | --- | --- |
| H1 | | |
| H2 | | |
| H3 (paste the guard's message) | | |
| H4 | | |
| H5 | | |
| H6 | | |
| H7 | | |
| A1 | | |
| A2 | | |
| A3 | | |
| A4 | | |
| **Decision** | ACCEPT / REJECT | |
