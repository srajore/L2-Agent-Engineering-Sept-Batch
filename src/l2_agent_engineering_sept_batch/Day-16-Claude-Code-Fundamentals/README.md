# Day 16 — Claude Code Fundamentals

## What You'll Learn Today

- Explain what Claude Code is: an AI coding assistant that reads, plans and edits your project. Python and LangGraph are what actually run your agent.
- Install Claude Code (native installer, or `npm` if you have Node.js), connect it to Ollama's `gemma4:cloud` model (no Claude subscription), run a first prompt, and start it inside this repository. Optionally add the VS Code extension.
- Use the core controls: `/help`, `/init`, `CLAUDE.md`, `@file` references, plan mode, permission prompts, `/clear`, `/compact`.
- Understand and set up `CLAUDE.md` (memory), `@imports`, permission modes, allow and deny rules in `settings.json`, the trust dialog, `/context`, `/cost`, `/diff`, `/resume`, and MCP servers — and prove each one works (see `CLAUDE-CODE-CONCEPTS.md`).
- Write a good request: goal, context, constraints, and how to verify.
- Review every proposed change before accepting it.
- Make one small, safe edit to a LangGraph file and verify old and new behavior.
- Understand the plan for Days 17–19: three SDLC agents that you will build with Claude Code, then connect so they talk to each other.

## Why This Matters

From today until Day 19 you do not type every line yourself. You **specify**, Claude Code **drafts**, and you **review and validate**. That is the real skill: knowing what to ask for, noticing when the result is wrong, and proving that it is right. The agent you build stays your design — Claude Code is the fast pair of hands.

## Key Concepts

**Two Different Roles.** Claude Code is the *builder*: it edits files in your folder. Your LangGraph file is the *product*: it runs by itself later, using Ollama (`gpt-oss:120b-cloud`) as its model. Claude Code is not inside your agent. Keep these two roles separate in your head.

**No Claude subscription needed.** In this course Claude Code runs on a model served by **Ollama**, the same Ollama you already use for the agents. You do not create a Claude account and you do not sign in to Claude in a browser. The model is `gemma4:cloud`, a cloud model served through your Ollama account.

**Because the model is not a Claude model,** it may follow instructions less carefully than the examples you see online. That is exactly why this course is about *verifying and accepting*: never trust a result you have not checked. If something behaves very differently from this handout, tell your trainer.

**Install and Connect Claude Code (Windows).** Before class you need **Ollama**, with `ollama signin` already done, and **one** of the two install routes below. **You do not need Node.js** unless you choose the npm route.

*Route A: native installer (no Node.js needed).* In Windows Command Prompt:

```cmd
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

*Route B: npm (needs Node.js, which provides `npm`):*

```cmd
npm install -g @anthropic-ai/claude-code
```

Use Route A if you do not already have Node.js. Use whichever your trainer tells you. Installing Claude Code does **not** sign you in to anything: the Claude account step is skipped because you start it with `ollama launch claude` below.

Then close Command Prompt, open a new one, and check:

```cmd
claude --version
```

It must print a version number. If `claude` is "not recognized", open another new Command Prompt and try again. (The `ollama launch claude` command starts the `claude` program that you just installed, by either route. Your trainer will confirm this on your machine.)

Check that the model answers, then leave the chat with `/bye`:

```cmd
ollama run gemma4:cloud
```

Start Claude Code connected to Ollama:

```cmd
ollama launch claude
```

Always start Claude Code with `ollama launch claude`. If it asks which model to use, choose `gemma4:cloud`, or name it directly:

```cmd
ollama launch claude --model gemma4:cloud
```

Starting it with plain `claude` is not set up to use Ollama and may ask you to sign in with a Claude account. If it does, **close it and use `ollama launch claude` instead.**

**First test (outside the repository).** Make a scratch folder so the test file does not land in the course repository:

```cmd
mkdir %USERPROFILE%\claude-hello
cd %USERPROFILE%\claude-hello
ollama launch claude
```

Then give Claude Code this prompt:

```text
Create index.html file in the current folder. It should have heading as Hello World with yellow background color. Finally save this file into the workspace.
```

Allow the file write when Claude Code asks. Open `index.html` in a browser: you should see a **Hello World** heading on a **yellow** background. Check the result yourself — this is your first accept-or-reject decision. Then quit with `/exit`.

**Claude Code in VS Code (optional).** In VS Code open the Extensions view and install **Claude Code for VS Code**. The extension must use the same Ollama connection as `ollama launch claude`. If it asks you to sign in with a Claude account, do not: tell your trainer. Everything in this course works from the terminal, so the extension is a convenience, not a requirement.

**For the rest of the course,** go to the repository and start Claude Code there:

```cmd
cd L2-Agent-Engineering
ollama launch claude
```

**The Controls You Need.**

| Control | What it does |
| --- | --- |
| `/help` | Lists every command |
| `/init` | Creates a `CLAUDE.md` file that tells Claude Code about your project |
| `CLAUDE.md` | Standing instructions read at every start (this repo's rules live there) |
| `@file` | Type `@Day-16-Claude-Code-Fundamentals\example.py` to point at a file |
| Plan mode (Shift+Tab to cycle modes) | Claude Code proposes a plan and edits nothing until you agree |
| Permission prompt | Before editing a file or running a command it asks; read it, then allow or deny |
| `/clear` | Starts fresh when you switch tasks |
| `/compact` | Shortens a long conversation and keeps the key facts |

**A Good Request Has Four Parts.** *Goal* (what should be true after), *Context* (which file, which Day), *Constraints* (what must not change), *Verify* (how we will check). Example: "In `@Day-16...\example.py` add a `password` label for tickets that mention password. Keep VPN and general behavior unchanged. Only edit this file. Then run it with `uv run python Day-16-Claude-Code-Fundamentals\example.py` and show me three sample tickets."

**Review Before You Accept.** A diff shows removed lines (red) and added lines (green). Ask yourself: did it touch only the file I named? Did it add libraries or helper files? Is every added line understandable? If not, say "revert that part" and be specific. Never accept a change you cannot explain.

**Verify, Do Not Trust.** After an edit, run the file yourself and test old behavior too. A change that adds a feature but breaks an old one is a failed change.

**Claude Code Concepts You Will Set Up Over Days 16–19.** Each one is a small file or command you ask Claude Code to create and then *prove* works:

| Day | Concept | What it gives you |
| --- | --- | --- |
| 16 | `CLAUDE.md`, `@imports`, `/memory` | Standing instructions read every session |
| 16 | Permission modes, allow and deny rules, trust dialog | Control over what Claude Code may do |
| 16 | `/context`, `/cost`, `/diff`, `/clear`, `/compact`, `/resume` | A healthy, reviewable session |
| 16 | MCP servers (`.mcp.json`) | Tools outside your files |
| 17 | Rules (`.claude\rules\`) and skills (`/accept-check`) | Folder-scoped guidance and reusable procedures |
| 18 | Hooks and subagents | **Enforced** guard rails and a read-only reviewer |
| 19 | Everything together, and headless `claude -p` | A complete setup and a repeatable check |

Today's concept lab is in `CLAUDE-CODE-CONCEPTS.md` in this folder.

**Your Role From Today: Verify and Accept.** Before Day 16 you wrote agent code by hand. From now on Claude Code writes it, and you do not need to write or study the Python. You give a specification, review Claude Code's *plan*, run what it built, and **accept or reject** it using acceptance tests and "break it on purpose" checks. Your toolkit: (1) the four-part request, (2) a plan checklist, (3) running the program and comparing the output with what you expected, (4) asking Claude Code to attack its own work and show you the output, and (5) Command Prompt scope checks such as `dir` and `findstr`. Rejecting a build with clear evidence is a success, not a failure.

**The Road to Day 19.** Days 17–19 each have Claude Code build one SDLC agent that you verify. Day 17: requirements → design. Day 18: design → code → tests. Day 19: review → release, and then all three agents hand work to each other in one parent graph. Every agent keeps the same safety shape: model suggests, plain Python validates, a human approves.

## Code Walkthrough — `Day-16-Claude-Code-Fundamentals/example.py`

```python
def label_ticket(state):
    text = state["ticket"].lower()
    if "vpn" in text:
        label = "network"
    else:
        label = "general"
    return {"label": label}
```

One node, two labels, one printed result. Run it first:

```cmd
uv run python Day-16-Claude-Code-Fundamentals\example.py
```

Predict: `VPN is disconnected` prints `network`.

## In Class: 120 Minutes

Everything in this day is covered inside the 120 minutes. **Practise** means you do it yourself; **Introduce** means you see it, try the one-line version, and go deeper later if you want.

| Minutes | Activity | Depth |
| --- | --- | --- |
| 10 | Why and what: two roles, the verify-and-accept job (slides) | Introduce |
| 15 | Connect to Ollama (`ollama run gemma4:cloud`, `ollama launch claude`) and run the Hello World test. Ollama and the Claude Code install (native installer, or npm if you have Node.js) should be done **before class** | Practise |
| 10 | Controls, the four-part request, how to review a diff (slides) | Introduce |
| 20 | **Safe-edit lab** (steps 1–5 below) | Practise |
| 10 | **CLAUDE.md** (`CLAUDE-CODE-CONCEPTS.md` Part A): tests T1 and T2 | Practise |
| 15 | **Permissions** (Part B): tests P1 to P3. Do the safe-edit lab first, **then** add the deny rule | Practise |
| 10 | **Context and cost commands** (Part C): try `/context` and `/diff` (C1, C2); the rest are shown by the trainer | Introduce |
| 10 | **MCP** (Part D): add the docs server and run `claude mcp list` (M1, M2) | Introduce |
| 20 | Share results, questions, preview of Days 17–19, and buffer for slow model responses | |

### Safe-edit lab steps

1. Open Command Prompt in the repository and run `claude`.
2. Ask: `Explain @Day-16-Claude-Code-Fundamentals\example.py in plain words. Do not edit anything.` Compare with your own trace.
3. Press Shift+Tab until plan mode is on. Ask for the `password` label change using the four-part request. Read the plan. Approve it.
4. Review the diff. Accept only if it touches this file only and keeps the VPN branch.
5. Run the file with three tickets: `VPN is disconnected`, `I forgot my password`, `Printer is jammed`. Expected labels: `network`, `password`, `general`.

## Optional practice after class (about 45 minutes)

Not needed to move on. Do it if you want to go deeper.

1. The tests you only saw or skipped: T3 (`@imports`), P4 (plan mode edits nothing), C3 and C4 (`/clear`, `/resume`), and M3 (use the docs server to answer a question).
2. Ask Claude Code to remove the docs MCP server if your trainer asks (`claude mcp remove claude-docs`).
3. Ask Claude Code to `/init` a `CLAUDE.md` in a scratch copy of the folder (or read this repository's `CLAUDE.md`) and list two rules you would add for your own projects.
4. Fill in the acceptance sheet at the end of `CLAUDE-CODE-CONCEPTS.md` for every part.
5. **Assignment:** add a fourth label, `printer`, using only Claude Code and the four-part request. (If you added the deny rule on `example.py`, ask Claude Code to remove it first, or temporarily edit a scratch copy.) Submit your request text, a screenshot of the diff you accepted, and the four outputs.
6. Read `Day-17-SDLC-Agent-1-Requirements-Design\CLAUDE-CODE-PROMPTS.md` to preview the next session.

## Before You Move to Day 17

- `claude --version` works, and `ollama launch claude` starts Claude Code on `gemma4:cloud` with no Claude sign-in.
- Your Hello World `index.html` test worked, and you checked it in a browser.
- You can name the four parts of a good request.
- You reviewed a diff before accepting it.
- You ran old and new behavior after the change.
- You completed the concepts acceptance sheet: CLAUDE.md and permissions practised in class; context commands and MCP introduced in class, with the remaining tests optional afterwards.
