# Session 16 Trainer Guide — Claude Code Fundamentals

## Outcome

By the end of the session every learner has Claude Code installed and running on Ollama's `gemma4:cloud` model (no Claude subscription, no Claude sign-in), has had Claude Code make one small edit that they reviewed and verified (they do not write the code), and understands that from Day 17 their job is to specify, verify and accept or reject what Claude Code builds.

## Files to Use

- `example.py` — the tiny file learners edit with Claude Code
- `README.md` — the participant handout (install steps, controls, lab, assignment)
- `slides.pptx` — 18-slide classroom deck, organised as Why, What, How, then lab (speaker notes included)

## Before the Session (do this a day earlier)

**Participants do not have a Claude subscription.** Claude Code runs on a model served by Ollama, so the pre-work is:

1. **Node.js is optional.** It is only needed for the npm route. Without Node.js use the native installer (`curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd` in Command Prompt).
2. Ollama installed and signed in (`ollama signin`). Ollama must be **version 0.35 or newer** so that `ollama launch` exists (0.35.0 on the machine I checked).
3. Claude Code installed by one route (native installer, or `npm install -g @anthropic-ai/claude-code`), then `claude --version`. **I have not confirmed that `ollama launch claude` finds a natively installed `claude`.** On the machine I used, `claude` was installed natively and `ollama launch` lists `claude` as an integration, but I could not start it because Ollama was off. Test one native-installed machine before class; if it fails, use the npm route for everyone.
4. `ollama run gemma4:cloud` answers a question (leave with `/bye`).
5. `ollama launch claude` opens Claude Code, and the Hello World `index.html` test works.

Ask every learner to do steps 1–5 **before class** and send you a screenshot of the Hello World page. Do the install with anyone blocked during the first 15 minutes; the corporate proxy is the usual cause of failure. Check that learners can reach the installer download (or the npm registry) and Ollama's cloud from the network.

**Important caveat for the whole block (Days 16–19).** I built and live-tested all the Day 17–19 prompts, checks and fail pages with a **Claude model**. Participants will use `gemma4:cloud`, which I have **not** tested. Expect it to follow instructions less reliably, plan more slowly or more loosely, and handle the skill, hook and agent prompts differently. Before teaching, run the Day 16 test, the Day 17 plan and build prompts, and the Day 18 hook prompt yourself on `gemma4:cloud`, and adjust the prompts or timings if needed. The acceptance tests are the safeguard: they judge the result whichever model produced it.

The VS Code extension ("Claude Code for VS Code") is optional. I have not verified how it is pointed at Ollama; confirm that on your machine before telling learners to use it.

## Setup in Windows Command Prompt

```cmd
uv sync
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
npm install -g @anthropic-ai/claude-code
claude --version
ollama run gemma4:cloud
ollama launch claude
uv run python Day-16-Claude-Code-Fundamentals\example.py
```

Agent code uses Ollama (`gpt-oss:120b-cloud`) as its runtime model, and Claude Code uses Ollama (`gemma4:cloud`) as its builder model. Both need `ollama signin`; neither needs a Claude account.

## Claude Code Concepts Block (added)

Learners follow `CLAUDE-CODE-CONCEPTS.md`: CLAUDE.md (T1–T3), permissions and settings (P1–P4), context and cost commands (C1–C4), MCP (M1–M3). Allow about 45 minutes. `_trainer-only\Day-16-Claude-Code-Fundamentals\trainer-reference\` holds sample `settings.json` and `.mcp.json` files to compare against. See also `IF-BUILD-FAILS.md` for setup problems.

Verified while preparing this session (Claude Code 2.1.266 on Windows):

- `claude mcp add --scope project --transport http claude-docs https://code.claude.com/docs/mcp` creates a correct `.mcp.json`; `claude mcp list` shows servers.
- A deny rule `Edit(path/**)` blocked a *Write* to that folder. A `Write(path)` rule is not matched; Claude Code itself says to use `Edit(...)`.
- Project allow rules are **ignored until the folder is trusted** (Claude Code prints "this workspace has not been trusted"). Learners must accept the trust dialog in an interactive session first.
- Not verified here (confirm in your own session before class): the exact output of `/context`, `/cost` or `/usage`, `/diff` and `/resume`, which can differ by version. Learners are told to use `/help` if a command is missing.
- Do the safe-edit lab **before** adding the Day 16 deny rule, since the rule blocks that file.

Time note: the session is 120 minutes and covers every topic; deeper tests are optional practice after class (see the flow below).

## Suggested 120-Minute Flow

Everything is covered in class. **Introduce** topics get the one-line version and a trainer demo; **Practise** topics are done by learners.

1. **10 minutes — Frame (WHY and WHAT), Introduce:** two roles; the verify-and-accept job. Draw it.
2. **15 minutes — Connect, Practise:** check the pre-work screenshots; everyone runs `ollama run gemma4:cloud`, `ollama launch claude` and the Hello World test in the scratch folder. Fix blockers in pairs; anyone still blocked finishes after class.
3. **10 minutes — Controls, Introduce:** `/help`, plan mode, permission prompts, the four-part request, how to review a diff.
4. **20 minutes — Safe-edit lab, Practise:** explain, plan, edit, review diff, run three tickets (README steps 1–5).
5. **10 minutes — CLAUDE.md, Practise:** T1 and T2.
6. **15 minutes — Permissions, Practise:** P1, P2, P3, after the safe-edit lab.
7. **10 minutes — Context and cost, Introduce:** learners try `/context` and `/diff` (C1, C2); you show the rest.
8. **10 minutes — MCP, Introduce:** learners add the docs server and run `claude mcp list` (M1, M2); remind them it is a sensitive topic (only trusted servers, no secrets).
9. **20 minutes — Share, questions, preview of Days 17–19, and buffer** for slow model responses. If you are behind, cut this block first, then shorten step 8.

### Optional practice after class (about 45 minutes)

T3, P4, C3, C4, M3; the `/init` reflection; the acceptance sheet; the `printer` label assignment; read the Day 17 prompts file. Nothing here blocks Day 17. Collect the acceptance sheet if you want a record.

## Code Walkthrough Questions

1. Which file is Claude Code allowed to change today?
2. Who decides the next step in this graph — you, Claude Code, or a model?
3. What did the diff add, and did it remove anything?
4. Which three inputs prove old and new behavior?

## Common Mistakes

- Treating Claude Code as part of the running agent. It is only the builder.
- Accepting the first diff without reading it.
- Vague requests ("make it better"), which produce wide, unreviewable changes.
- Asking Claude Code to add LangChain classes or helper files — reject; see `CLAUDE.md`.
- Skipping the run after an edit.
- Pasting API keys into the chat.

## Exit Check

Ask each learner to state: the four parts of a request, one thing they rejected or questioned in a diff, and the Day 17 agent's input and output.
