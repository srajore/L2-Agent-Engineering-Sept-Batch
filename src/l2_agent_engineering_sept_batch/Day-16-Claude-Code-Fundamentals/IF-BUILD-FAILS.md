# Day 16 — If something does not work

Stay calm. A failure with clear evidence is useful. Work down this page. Spend **no more than 10 minutes** on any one problem, then ask your trainer.

## First: collect evidence

Before you ask anyone, write down (or copy):

1. Which step or test (for example `P3`).
2. The exact message on screen.
3. What you typed.

## Setup problems

| What you see | Try this |
| --- | --- |
| `npm` is "not recognized" | You do not have Node.js. **You do not need it:** use Route A (the native installer) from the README instead |
| The native installer (`curl ... install.cmd`) fails | Copy the message to your trainer. A network or proxy block is the usual cause. If `curl` is missing, ask your trainer for the PowerShell form of the installer |
| `npm install -g @anthropic-ai/claude-code` fails | Copy the message to your trainer. A network or proxy block, or a permissions error, is the usual cause. Do not run Command Prompt "as administrator" unless your trainer says so |
| `claude` is "not recognized" after the install | Close Command Prompt, open a **new** one, run `claude --version`. If it still fails, rerun your install command from the README and open another new window |
| `ollama launch claude` cannot find Claude Code | Check `claude --version` works in the same window. If it does and Ollama still cannot find it, tell your trainer: they may switch you to the other install route |
| `ollama` is "not recognized", or it cannot connect | Ollama is not installed or not running. Start the Ollama app and try again. Ask your trainer |
| `ollama run gemma4:cloud` says the model is not found, or asks you to sign in | Run `ollama signin` (the same sign-in you use for the course), then try again |
| `ollama run gemma4:cloud` is very slow or times out | Cloud models depend on the network. Wait a minute and retry. If it keeps failing, tell your trainer |
| `ollama launch claude` is not a command | Your Ollama is too old for this. Ask your trainer to update Ollama |
| Claude Code asks you to **sign in with a Claude account** | You started it with plain `claude`. Close it and start with `ollama launch claude` (or `ollama launch claude --model gemma4:cloud`). Do not create a Claude account |
| Claude Code starts but answers are slow, odd, or ignore instructions | This model is not a Claude model. Make your request shorter and more specific, one step at a time, and **check every result**. Tell your trainer if it is unusable |
| The Hello World test: no `index.html`, or the wrong colour | Check you are in the scratch folder (`cd %USERPROFILE%\claude-hello`). Then send one fix message, for example: `index.html is missing. Create it in the current folder with an h1 Hello World and a yellow background.` Then open it in a browser |
| The VS Code extension asks for a Claude sign-in | Do not sign in. Close it and use the terminal route (`ollama launch claude`); tell your trainer |
| `uv` is not recognized | You are not in the course setup. Ask your trainer; the course uses `uv sync` once from the repository root |

## Problems with the concept tests

| Test | What you see | Try this |
| --- | --- | --- |
| T1 | It does not quote any rules | Make sure you started `claude` from the **repository root** (the folder that contains `CLAUDE.md`). Quit with `/exit`, `cd` to the right folder, start again |
| T3 | It cannot answer about `CODE_GUIDE.md` | `@imports` are read when a session **starts**. Quit and start `claude` again, then ask |
| P1 | Claude Code will not write `.claude\settings.local.json` | `.claude` is a sensitive folder: it needs your permission. Ask again and **allow** the write when prompted |
| P2 | It still asks permission to run `findstr` | Project rules are ignored until you **accept the trust dialog** for this folder. Quit, start `claude`, accept the dialog, and check `/permissions` |
| P3 | The edit was **not** refused | Check the deny rule is written as `Edit(...)`, not `Write(...)`, and that the path matches exactly. Ask Claude Code to show you `.claude\settings.local.json` and compare it with the spec |
| P4 | Plan mode still changed a file | You may not have been in plan mode. Press Shift+Tab until the mode line says plan, then try again |
| C1–C4 | A `/command` is not recognized | Your version may name it differently. Type `/help` and look for the closest command |
| M1–M3 | The server does not show as connected | Run `claude mcp list`. If it says needs authentication or failed, tell your trainer. Do not add other servers to try to fix it |

## If Claude Code gives you the wrong thing

Do not argue and do not accept a change you cannot check. Send **one precise message**:

```text
Test P3 failed. You edited Day-16-Claude-Code-Fundamentals\example.py even though the deny rule
exists. Show me .claude\settings.local.json exactly as it is now, and tell me what is wrong with it.
Do not change anything else.
```

Rules for fix messages:

- Name the test.
- Quote what you saw.
- Ask for **one** fix.
- Then rerun **only** the failed test.

If two fix messages do not work, type `/clear`, paste the original prompt again, and start that part fresh.

## Still stuck? Use the rescue

Ask your trainer. They may give you a known-good file **for that step only**. You must then run the tests on it yourself, and you write "used rescue" and the reason on your acceptance sheet.
