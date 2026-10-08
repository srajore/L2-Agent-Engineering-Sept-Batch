# Day 19 — Claude Code Concepts: Putting It All Together

**Your role:** today you add no new file types. You prove that the Claude Code features (rules and skill from Day 17, and the hook and subagent you build today) work **together** while Claude Code builds Agent 3 and the chain, and you learn headless mode. Nothing here needs Day 16. The same steps are in `START-HERE`, which is the file to follow in class. The hook (Part 2) and the subagent (Part 4A) are built during class; the integration tests below run alongside the Agent 3 and chain builds.

## Time plan

Everything is covered in class. **Practise** = you do the tests. **Introduce** = the short version.

| Item | In class | Depth |
| --- | --- | --- |
| Guard hook H1–H4 (`START-HERE` Part 2) | About 20 min | Practise |
| Subagent SA1–SA3 (`START-HERE` Part 4A) | About 8 min | Practise |
| I1, I2, I4 | About 5 min | Practise |
| I3 | It is the agent and chain build itself | Practise |
| Headless P1 (one `claude -p` run) | About 5 min | Introduce |
| Part C — driver's check (13 tasks) | Read the list and tick what you already did today (5 min) | Introduce |
| I5, P2, and finishing the driver's check | Optional later | |

## Part A — Everything on, at once

Your project now has:

| From | Item | What it does |
| --- | --- | --- |
| Course folder | `CLAUDE.md` | Standing instructions Claude Code loads automatically |
| Day 17 | `.claude\rules\` | Guidance (always-on and path-scoped) |
| Day 17 | `.claude\skills\accept-check` | `/accept-check <file>` |
| Day 19 | `.claude\hooks\guard.py` + hook in `settings.json` | **Enforced** protection of reference files and other days |
| Day 19 | `.claude\agents\agent-reviewer.md` | Read-only reviewer |

**The guard hook is built at the start of today (`START-HERE`, Part 2), and it already points `.claude\active-day.txt` at today's folder.** Day 18 ran out of time before hooks and subagents, so both are built today. If you did build the hook on Day 18, ask Claude Code to set `active-day.txt` to `Day-19-SDLC-Agent-3-Review-Release`, or the guard will block writes to today's folder. The guard then protects every other day.

### Subagent tests (built in `START-HERE` Part 4A)

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| SA1 | File is right | Ask Claude Code to show `.claude\agents\agent-reviewer.md` | `tools` lists only Read, Grep, Glob; it says it never edits |
| SA2 | It reviews | `Use the agent-reviewer subagent to review Day-19-SDLC-Agent-3-Review-Release\my_agent3.py` | A numbered list of at most 5 items, each with a way to test it, ending `REVIEWER: DONE` |
| SA3 | It cannot edit | `Use the agent-reviewer subagent to fix the problems it found in my_agent3.py.` | `my_agent3.py` does **not** change (it has no edit tool) |
| SA4 | Use its findings (optional) | Turn one finding into a break-it prompt and run it | You have a new test you did not have before |

### Integration tests

| # | Test | How | Pass when |
| --- | --- | --- | --- |
| I1 | Setup survived | `/hooks`, then ask Claude Code to list the files under `.claude` | Hook listed; rules, skill, agent, hook script and settings all present |
| I2 | Guard still protects | Ask: `Create a file named chain.py in Day-19-SDLC-Agent-3-Review-Release containing a print line.` | Refused with the guard's message; no file created |
| I3 | Build with everything on | Build `my_agent3.py` and `my_chain.py` using Prompts 1–4 | Agent 3 and chain tests pass (see `CLAUDE-CODE-PROMPTS.md`) |
| I4 | One-command acceptance | `/accept-check Day-19-SDLC-Agent-3-Review-Release\my_agent3.py` | `DECISION: ACCEPT` (Agent 3 has `interrupt` and the model name; it has no LangChain) |
| I5 | Reviewer attack on the chain | `Use the agent-reviewer subagent to review my_chain.py` | A list of at most 5 failure ideas; turn one into a test and run it |

Note for I4: `/accept-check` checks for `interrupt`, which `my_chain.py` also contains, so it works on that file too.

## Part B — Headless mode: Claude Code without the chat

`claude -p "..."` runs one prompt and prints the answer, then exits. Use it for repeatable checks and automation.

```cmd
claude -p "/accept-check Day-19-SDLC-Agent-3-Review-Release\my_agent3.py" --allowedTools "Bash,Read"
```

**In this course Claude Code runs through Ollama.** Plain `claude` is not connected to Ollama, so start it the way you did in the interactive sessions and pass the same arguments after `--`:

```cmd
ollama launch claude --model nemotron-3-ultra:cloud -y -- -p "/accept-check Day-19-SDLC-Agent-3-Review-Release\my_agent3.py" --allowedTools "Bash,Read"
```

(This form was confirmed to work headless on `gpt-oss:120b-cloud` in the trainer's pilot. If it fails on your machine, run `/accept-check` inside a normal `ollama launch claude --model nemotron-3-ultra:cloud` session instead; the check is the same.)

| Piece | Meaning |
| --- | --- |
| `-p "..."` | Run this prompt, print the result, exit |
| `--allowedTools "Bash,Read"` | The tools it may use without asking. In headless mode nothing can ask you |
| `claude -c` | Continue your last conversation (interactive) |

### Tests

| # | Test | Pass when |
| --- | --- | --- |
| P1 | Run the command above in Command Prompt | The same PASS table and a DECISION line print, then the command returns to the prompt |
| P2 | Run it again on a file with `import langchain` | `DECISION: REJECT` |

## Part C — Your Claude Code driver's check

Do each task without help and tick it when you can show proof.

| # | Task | Proof |
| --- | --- | --- |
| 1 | Install and sign in | `claude --version` |
| 2 | Start Claude Code in a project folder with the right model | The launch command you used |
| 3 | Use plan mode and reject a bad plan | A plan you sent back, with your reason |
| 4 | Use `@file` to point at a file | The command you typed |
| 5 | Read a diff and reject a change | Your reject message |
| 6 | Explain allow, deny and the trust dialog | One sentence each |
| 7 | (Optional, not covered in Days 17-19) Add an MCP server at project scope | `.mcp.json` entry |
| 8 | Create a rule and explain why it is not a guarantee | Your R3 number from Day 17 |
| 9 | Create and run a skill | `/accept-check` output |
| 10 | Create a hook that blocks an action, and prove it | The guard's message |
| 11 | Create a read-only subagent and prove it cannot edit | Test SA3 |
| 12 | Run Claude Code headless | The `claude -p` output |
| 13 | Build and accept three agents and a chain | Your acceptance sheets for Days 17–19 |

## Accept or reject

**ACCEPT** your Claude Code setup only if H1–H4, SA1–SA3, I1–I5 and P1–P2 pass. Hand in the driver's check with proof for each row you ticked.

## Acceptance sheet (hand this in)

| Test | Pass / Fail | Evidence |
| --- | --- | --- |
| H1–H4 | | |
| SA1–SA3 | | |
| I1 | | |
| I2 | | |
| I3 | | |
| I4 | | |
| I5 | | |
| P1 | | |
| P2 | | |
| Driver's check rows ticked (out of 13) | | |
| **Decision** | ACCEPT / REJECT | |
