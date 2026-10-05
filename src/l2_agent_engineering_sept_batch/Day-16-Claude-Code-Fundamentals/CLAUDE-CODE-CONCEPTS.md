# Day 16 — Claude Code Concepts: Memory, Permissions, Context and MCP

**Your role:** you do not write these files. You ask Claude Code to create or change them, then **prove** they work. Run `claude` from the repository root in Windows Command Prompt. Commands that start with `/` are typed inside Claude Code. Commands without `/` are typed in Command Prompt.

If a `/command` is not recognised on your version, type `/help` to see what you have.

> **Expect permission prompts.** Claude Code treats the `.claude` folder (where `settings.local.json` lives) as sensitive, so it will **ask before it writes there**. Allow it when the path is the one you asked for.

## Time plan

All four parts are covered in class. **Practise** = you do the tests. **Introduce** = you try the one-line version and the trainer shows the rest.

| Part | In class | Depth | Optional later |
| --- | --- | --- | --- |
| A — CLAUDE.md | T1, T2 (10 min) | Practise | T3 |
| B — Permissions | P1, P2, P3 (15 min, after the safe-edit lab) | Practise | P4 |
| C — Context and cost | C1, C2 (10 min) | Introduce | C3, C4 |
| D — MCP | M1, M2 (10 min) | Introduce | M3 |

## Part A — CLAUDE.md: the project's standing instructions

| Question | Answer |
| --- | --- |
| What is it? | A markdown file Claude Code reads at the start of every session |
| Where? | `CLAUDE.md` in the project (shared with the team); `~\.claude\CLAUDE.md` (just you, all projects); `CLAUDE.local.md` (just you, this project) |
| What goes in it? | Build and run commands, conventions, "never do" rules. Keep it short (a few dozen lines) |
| `/init` | Asks Claude Code to look at the project and draft a `CLAUDE.md` |
| `/memory` | Opens the memory files so you can read and edit them |
| `@imports` | A line like `@README.md` inside `CLAUDE.md` pulls that file in |

**Honest limit:** `CLAUDE.md` is guidance, not enforcement. Claude Code reads it and usually follows it, but not every time. You will measure this yourself on Day 17.

### Tests

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| T1 | It is loaded | Ask: `Without opening any file, quote the rules you have from this project's CLAUDE.md.` | It quotes real rules from this repo's `CLAUDE.md` |
| T2 | You can extend it | Ask: `Add one rule to CLAUDE.md: "End every answer about code with the line: Verify by running it."` Then `/clear` and ask any code question | The new rule appears in the file; check whether the next answer follows it and note yes or no |
| T3 | Imports work | Ask Claude Code to add a line `@CODE_GUIDE.md` to `CLAUDE.md`, restart `claude`, and ask what `CODE_GUIDE.md` says about the model name | It answers `gpt-oss:120b-cloud` |

Undo T2 and T3 afterwards: ask Claude Code to remove the lines it added.

## Part B — Permissions and settings: who is allowed to do what

| Concept | What to know |
| --- | --- |
| Permission prompt | Before editing a file or running a command, Claude Code asks. You read it, then allow or deny |
| Modes (Shift+Tab) | **default** asks each time; **plan** proposes only, edits nothing; **acceptEdits** auto-approves file edits. Your version may list more |
| `/permissions` | Shows and edits the allow and deny rules |
| Settings files | `.claude\settings.json` (project, shared); `.claude\settings.local.json` (just you, this project); `~\.claude\settings.json` (just you, everywhere) |
| Allow rule | `"Bash(findstr *)"` lets Claude Code run `findstr ...` without asking |
| Deny rule | `"Edit(Day-16-Claude-Code-Fundamentals/example.py)"` blocks edits to that file (patterns like `Day-*/...` also work). **Use `Edit(...)`**: it covers every file-editing tool. A `Write(...)` rule is not matched |
| Deny wins | If a command matches both allow and deny, deny wins |
| Trust dialog | The first time you open a folder, Claude Code asks whether you trust it. **Until you accept, the project's allow rules are ignored.** Only trust folders you know |

### Prompt (use plan mode, then approve)

```text
Create .claude\settings.local.json with these permission rules only:
allow Bash(findstr *), allow Bash(dir *), allow Read; deny Edit(Day-16-Claude-Code-Fundamentals/example.py).
Show me the file. Do not change any other file.
```

**Order matters:** do the safe-edit lab first (Day 16 README), *then* add the deny rule, because the deny rule would also block that lab edit.

### Tests

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| P1 | File is exactly as specified | Read the file Claude Code shows | Three allow rules, one deny rule, nothing else |
| P2 | Allow works | Ask: `Run findstr /c:StateGraph Day-16-Claude-Code-Fundamentals\example.py` | It runs without asking you for permission |
| P3 | Deny works | Ask: `Add a comment line to Day-16-Claude-Code-Fundamentals\example.py` | The edit is refused because of your permission settings; the file is unchanged |
| P4 | Plan mode edits nothing | Shift+Tab to plan mode and ask for any file change | You get a plan; no file changes |

## Part C — Context and cost: keeping a session healthy

| Command | What it shows or does |
| --- | --- |
| `/context` | What is filling the context window (CLAUDE.md, history, tools) |
| `/cost` (or `/usage`) | Tokens and cost for this session. With Ollama the cost may show as zero or as not available: that is fine |
| `/diff` | The changes Claude Code made, so you can review before accepting |
| `/clear` | Starts a fresh conversation (use between unrelated tasks) |
| `/compact` | Summarises a long conversation and keeps the key facts |
| `/resume` | Returns to an earlier conversation |
| `claude -c` | From Command Prompt: continue the last conversation |

### Tests

| # | Test | Pass when |
| --- | --- | --- |
| C1 | Run `/context` | You can name the biggest item in the list |
| C2 | Make a small edit, then run `/diff` | You see the changed lines |
| C3 | Run `/clear`, then ask what we were just doing | It no longer remembers |
| C4 | Run `/resume` and pick the earlier session | The earlier conversation is back |

## Part D — MCP: connecting Claude Code to outside tools

MCP (Model Context Protocol) lets Claude Code use tools that live outside your computer's files, such as a documentation server.

| Concept | What to know |
| --- | --- |
| Add a server | `claude mcp add --scope project --transport http claude-docs https://code.claude.com/docs/mcp` (typed in Command Prompt) |
| Where it is saved | `.mcp.json` in the project, which you can share. Other scopes save to your user config |
| `claude mcp list` / `/mcp` | Show servers and whether they are connected |
| Safety | Only add servers from sources you trust. Never paste keys or tokens into prompts or files |

### Prompt (plan mode)

```text
Add the Claude documentation MCP server to this project only, using project scope:
claude mcp add --scope project --transport http claude-docs https://code.claude.com/docs/mcp
Then show me the .mcp.json file and the output of: claude mcp list
```

### Tests

| # | Test | Pass when |
| --- | --- | --- |
| M1 | `.mcp.json` exists | It contains a `claude-docs` entry with the URL above and nothing secret |
| M2 | `claude mcp list` | `claude-docs` appears in the list |
| M3 | Use it | Ask: `Use the claude-docs server to explain what a hook is in two sentences.` The answer comes from the docs |

Afterwards ask Claude Code to remove the server if your trainer says so (`claude mcp remove claude-docs`).

## Accept or reject

**ACCEPT** your setup only if T1–T3, P1–P4, C1–C4 and M1–M3 pass. Reject with evidence: name the test, quote what you saw, ask for one fix.

## Acceptance sheet (hand this in)

| Test | Pass / Fail | Evidence |
| --- | --- | --- |
| T1 | | |
| T2 (did the next answer follow the rule? yes / no) | | |
| T3 | | |
| P1 | | |
| P2 | | |
| P3 | | |
| P4 | | |
| C1–C4 (one line) | | |
| M1 | | |
| M2 | | |
| M3 | | |
| **Decision** | ACCEPT / REJECT | |
