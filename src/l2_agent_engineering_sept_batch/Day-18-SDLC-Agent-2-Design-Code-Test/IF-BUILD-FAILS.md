# Day 18 — If the build, a test or a hook fails

A failing test is the acceptance test doing its job. Work down this page. Spend **no more than 10 minutes** on one problem, then ask your trainer.

## The fix loop (use this for every failure)

1. **Name the test** that failed (for example `B3`) and copy what you saw.
2. Send Claude Code **one** message in this shape:

   ```text
   Test B3 failed. The generated tests contain "def validate_leave_request". I saw: <paste>.
   Make the validation reject tests that define the function, then rerun. Keep everything else.
   ```

3. Rerun the failed test, **then rerun every test B1 to B6**. A fix can quietly break something that passed before. Keep each fix message short.
4. **After 2 fix messages** that do not work: `/clear`, paste Prompt 1 again, and build into a new file name such as `my_agent2_v2.py`.
5. **Still failing?** Use the rescue below.

## Build and test problems

| What you see | Likely cause | Send this |
| --- | --- | --- |
| "ALL TESTS PASSED" but the tests contain `def validate_leave_request` | A **vacuous pass**: the tests test their own copy | `The tests redefine the function, so they prove nothing. Reject any tests that define validate_leave_request, require at least 4 asserts, and have the tests call the real function.` |
| B5 fails: the test-data table is missing, has no invalid case, or the agent stops with "could not produce valid test data" | The data step or its check is missing, or the model keeps returning bad JSON or unreal dates | `Test B5 failed. Add a test-data step: the model returns a JSON list of 5 to 8 cases; plain Python checks at least 4 cases, both valid and invalid outcomes, and real dates (an unreal date only in a case that expects invalid); retry up to 3 times; and run every case against the code in the same subprocess as the asserts.` |
| B6 fails: no explanation, or it is full of jargon | The explain step is missing | `Test B6 failed. After the tests pass, ask the model to explain the final code in 3 to 6 short plain-English lines for a non-programmer, and print it before the approval question.` |
| The weak-tests check: **every** test still passes on the broken copy | The tests are weak | `The tests did not catch the missing end-before-start check. Strengthen the test generation so that case is covered, then repeat the check.` |
| `SyntaxError` in the generated code | The model wrapped code in markdown fences | `The generated code starts with markdown fences. Strip them before parsing and running.` |
| Tests fail only because of different error text | Exact-text assertions | `Do not assert the reason text. For invalid requests assert only the first value, for example result[0] is False.` |
| The run hangs | Generated code loops, or it runs inside the agent's own process | Press **Ctrl+C**, then: `Run generated code only in a subprocess with a 15 second timeout, never inside this process.` |
| More than 3 attempts, or it never stops | No retry limit | `Count attempts in the state. After 3 attempts go to the stop route and say why.` |
| `EOFError` or a hang at "Approve…? (yes/no)" | Claude Code's own run cannot type for you | **Run the program yourself** in Command Prompt and type `yes`, or have Claude Code run it with `echo yes\| uv run python ...` |
| The answer is treated as **no** | A trailing space or PowerShell piping | Use **Command Prompt** and type the answer |
| Ollama connection error, 401, or the model is missing | Ollama is not signed in | In a separate Command Prompt run `ollama signin` |
| `langchain` or `pytest` found by the scope check | Claude Code used them | `Remove LangChain and pytest. Use plain assert statements and ollama.chat directly. Follow CLAUDE.md.` |
| A break-it prompt left the file changed | The temporary change was not restored | `Restore my_agent2.py to how it was before the temporary change and show me.` |

## The guard hook does not work

| Test | What you see | Try this |
| --- | --- | --- |
| H1 | Claude Code will not write the hook files | `.claude` is a sensitive folder, so Claude Code needs your permission. Ask again and **allow** the writes (including the edit to `settings.json`). If it only prints the text, save it into the paths it showed |
| H1 | `/hooks` shows nothing | **Restart `claude`.** Settings load when a session starts. Accept the trust dialog if asked |
| H2 | Even a normal file is refused | The hook is blocking too much. Ask: `The guard blocks files in today's folder. Show me guard.py and active-day.txt. active-day.txt must contain exactly today's folder name.` |
| H3, H4 | Nothing is blocked | Check the hook is registered in `.claude\settings.json` with event `PreToolUse`, matcher for Edit and Write, and a command of `uv run python .claude/hooks/guard.py`. Ask Claude Code to show the file and compare with the spec |
| H3, H4 | An error about Python or `uv` | The command must run from the repository root. Run `uv run python .claude/hooks/guard.py` by hand to see the real error |
| H5 | Changing `active-day.txt` makes no difference | The script must read the file on every run, not store the value. Ask Claude Code to check |
| Hook blocks `active-day.txt` itself | The rule is too broad | The guard should only block files named `example.py` or `chain.py`, and files inside a **different** `Day-` folder |

## The reviewer subagent does not work

| Test | What you see | Try this |
| --- | --- | --- |
| A1–A2 | It is not found | The file must be `.claude\agents\agent-reviewer.md`. **Restart `claude`** |
| A3 | It **did** change the file | Its `tools` line must list only `Read, Grep, Glob`. Fix that line and rerun the test |
| A2 | It asks permission for tools | Approve the read-only tools; it has no edit tool |

## Rescue: last resort

Tell your trainer. They may give you the matching known-good file **for that step only**. You must run every acceptance test on it yourself and write **"used rescue"** and the reason on your acceptance sheet.
