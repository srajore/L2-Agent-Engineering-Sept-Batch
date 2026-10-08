# Day 19 — If the build, a gate, the chain or a setup file fails

A failing test is the acceptance test doing its job. Spend **no more than 10 minutes** on one problem, then ask your trainer.

## The fix loop (use this for every failure)

1. **Name the test** that failed (for example `C5` or `D2`) and copy what you saw.
2. Send Claude Code **one** message in this shape:

   ```text
   Test D2 failed. I answered no at Agent 2 and Agent 3 still ran. I saw: <paste>.
   The parent graph must stop when an agent does not finish. Fix only that and rerun.
   ```

3. Rerun the failed test, **then rerun every test for that agent (C1 to C8) or the chain (D1 to D4)**. A fix can quietly break something that passed before. Keep each fix message short.
4. **After 2 fix messages** that do not work: `/clear`, paste the prompt again, and build into a new file name (for example `my_chain_v2.py`).
5. **Still failing?** Use the rescue below.

## Agent 3 problems

| What you see | Likely cause | Send this |
| --- | --- | --- |
| A gate does not block (C3, C4) | The gate is missing or checked by the model | `Test C3 failed. With tests_passed set to False the agent still released. Gates must be plain Python checks that block release. Fix and show the status.` |
| Release notes are written even though a gate failed (C5) | The blocked route is not before the notes | `When a gate fails, go to the blocked status and skip the release notes entirely.` |
| C7 fails: the output does not say it is reviewing a pull request, or findings do not name a line | The input is just a code string, or the prompt does not ask for the line | `Test C7 failed. Make the input a pull request (title, description, diff). Print "Reviewing PR: <title>" first, and ask the reviewer to quote the added line each finding refers to.` |
| C8 fails: no documentation, or headings are missing | The documentation step or its check is missing | `Test C8 failed. Add a documentation step with exactly the headings ## Purpose, ## Parameters, ## Returns, ## Example. Check in Python that all four and the function name are present, retry once, then block as "documentation incomplete". Print it before the approval question.` |
| An unreadable review counts as clean (C6) | No safe failure | `If the model review is not valid JSON, record one HIGH finding so that release is blocked.` |
| Stories or questions are printed twice at the first approval | The step re-runs when the graph resumes | Cosmetic. Do not reject for it |
| `ConnectionError: Failed to connect to Ollama` | The Ollama app is not running on this computer | Start Ollama (ask your trainer), then run again. Not a Claude Code problem |
| The run says Blocked on a good sample | The model labelled something HIGH | **Not a bug.** The reviewer's labels vary from run to run. Read the finding, decide if you agree, and run again |
| `EOFError` or a hang at an approval question | Claude Code's own run cannot type | **Run the program yourself** in Command Prompt, or have Claude Code run it with `echo yes\| uv run python ...` |
| The answer is treated as **no** | A trailing space or PowerShell piping | Use **Command Prompt** |
| Ollama error, 401 or model missing | Ollama is not signed in | `ollama signin` in a separate Command Prompt |

## Chain problems

| What you see | Likely cause | Send this |
| --- | --- | --- |
| D2: Agent 3 still runs after `no` at Agent 2 | No stop rule between agents | `After each agent, continue only if it finished successfully; otherwise end the chain.` |
| D4: the handoff log has **four** entries instead of two | A subgraph returns the whole state, so an appended list doubles | `Do not use an append reducer for handoffs. Each handoff step should set handoffs to the existing list plus one new entry.` |
| Agent 2 stops almost immediately | It inherited Agent 1's attempt counter | `Reset the attempt counter and the approved flag in the handoff from Agent 1 to Agent 2.` |
| The chain asks only one question, or ends early | An interrupt is not being resumed in a loop | `Loop on the interrupt: while the result has an interrupt, show the question, read my yes or no, and resume the same thread.` |
| I answer `yes` at Agent 1 but the chain says `Stopped in Agent 1` | Agent 1 compares the answer to the text "yes", but the loop sends True/False | `Every approval node must accept the loop's True/False answer: approved = answer is True or str(answer).strip().lower() == "yes". Fix Agent 1, Agent 2 and Agent 3 and rerun.` |
| The chain stops after Agent 1 even though I approved, or never stops when I say no | The agents do not set a status the parent can test | `Each agent must set state["status"] when it ends: "Agent 1 done" or "Stopped in Agent 1"; "Code and tests approved" or a "Stopped: ..." text. The parent continues only on those two done statuses; anything else goes to a stop node that sets "Stopped in Agent 1" or "Stopped in Agent 2".` |
| I answer a question but never saw the agent's output | The output was printed before the pause and lost, or not shown at all | `Build each agent's output into the text passed to interrupt() (print nothing before interrupt) and print that text in the loop before asking me.` |
| `NameError`, a node runs the wrong code, or `InvalidUpdateError: Expected node ...` | Two of the three files have a function or class with the same name (for example `stopped` or `State`) | `Rename the clashing functions and classes so each agent's are unique, and make sure the parent state lists every key the three agents use.` |
| The scope check finds `import my_agent` or `import example` | The chain imports your other files | `Make my_chain.py self-contained. Copy the node functions in; no imports from other files.` |
| `langchain` found | Claude Code used it | `Remove LangChain. Use LangGraph subgraphs only and ollama.chat directly.` |
| It created `shared.py` or other files | Claude Code split the work | `Put everything in my_chain.py and delete the extra files. Show me the folder listing.` |

## Setup files and headless problems

| Test | What you see | Try this |
| --- | --- | --- |
| H1 | `/hooks` shows nothing | `claude` was not restarted after `settings.json` changed, or the `hooks` entry is missing. Quit, run `ollama launch claude --model nemotron-3-ultra:cloud` again, accept the trust dialog, and check `.claude\settings.json` has the `hooks` entry |
| H2 | Even `hook_ok.txt` is refused | `.claude\active-day.txt` has the wrong folder name. Ask Claude Code to show it; it must be exactly `Day-19-SDLC-Agent-3-Review-Release` |
| H3, H4 | The guard does not refuse | The hook is not loaded (see H1), or `guard.py` does not exit with code 2. Ask Claude Code to show `.claude\hooks\guard.py` and compare it with the prompt |
| H1 | The hook errors instead of blocking (every edit fails with a Python error) | Take it out and carry on: ask Claude Code to remove the `hooks` key from `.claude\settings.json`, restart, and finish the day without the hook. Tell your trainer |
| H1 | Claude Code asks to write inside `.claude` | Normal. Check the path is inside `.claude`, then allow it |
| I1 | Rules, skill or agent missing | One of the earlier days' files was not saved or was removed. Ask Claude Code to list `.claude` and recreate the missing item from that day's spec. If the subagent is missing, rebuild it from `START-HERE` Part 4A |
| SA1, SA2 | `/agents` does not list `agent-reviewer`, or the review errors | `claude` was not restarted after the file was created, or the header is wrong. Ask Claude Code to show `.claude\agents\agent-reviewer.md`; `name` must be `agent-reviewer` and `tools` must be `Read, Grep, Glob`. If it errors on a `model` line, ask Claude Code to remove that line, then restart. Nothing later depends on it |
| SA3 | `my_agent3.py` changed after you asked the subagent to fix it | The file has an edit tool in `tools`. Ask Claude Code to set `tools` to only `Read, Grep, Glob`, restart, and repeat. The subagent is not accepted until this passes |
| I2 | The guard does not refuse | See H3 and H4 |
| I4 | `/accept-check` is not recognised | Restart `claude`; check `.claude\skills\accept-check\SKILL.md` exists |
| P1 | `claude -p` asks you to sign in with a Claude account | You used plain `claude`. Use `ollama launch claude --model nemotron-3-ultra:cloud -y -- -p "..." --allowedTools "Bash,Read"`, or run `/accept-check` inside a normal `ollama launch claude --model nemotron-3-ultra:cloud` session |
| P1 | `claude -p` asks for permission or hangs | In headless mode nothing can ask you. Add the tools: `--allowedTools "Bash,Read"`. Press Ctrl+C if it hangs |
| P1 | `findstr` output looks different | Check the file path is right and that you are in the repository root |

## Rescue: last resort

Tell your trainer. They may give you the matching known-good file **for that step only** (Agent 3, the chain, or a working Day 17 or Day 18 agent that the chain needs). You must run every acceptance test on it yourself and write **"used rescue"** and the reason on your acceptance sheet.
