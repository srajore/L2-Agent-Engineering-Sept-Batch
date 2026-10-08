# Day 17 — If the build or a test fails

A failing test is not your failure: it is the acceptance test doing its job. Work down this page. Spend **no more than 10 minutes** on one problem, then ask your trainer.

## The fix loop (use this for every failure)

1. **Name the test** that failed (for example `A3`) and copy what you saw.
2. Send Claude Code **one** message in this shape:

   ```text
   Test A3 failed. The questions do not include one about "secure". I saw: <paste the output>.
   Fix only that, keep everything else, and rerun the agent. Do not create any new file.
   ```

3. Rerun the failed test, **then rerun every test A1 to A8**. A fix can quietly break something that passed before. Keep each fix message short.
4. **After 2 fix messages** that do not work: type `/clear`, paste Prompt 1 again, and rebuild into a **new** file name such as `my_agent1_v2.py`. Compare the plan with the checklist before approving.
5. **Still failing?** Use the rescue below.

## Common problems and the message to send

| What you see | Likely cause | Send this |
| --- | --- | --- |
| "Ollama" connection error, 401, or the model is not found | Ollama is not signed in on this computer | Not a Claude Code problem. In a **separate** Command Prompt run `ollama signin`, then rerun. Ask your trainer if it still fails |
| `ModuleNotFoundError` (for example `langgraph`) | The course environment is not installed | In Command Prompt from the repository root run `uv sync`, then rerun |
| The run stops with `EOFError` or hangs at "Approve…? (yes/no)" | The program asks you to type, but Claude Code's own run cannot type for you | **Run the program yourself** in Command Prompt: `uv run python Day-17-SDLC-Agent-1-Requirements-Design\my_agent1.py`, and type `yes` there. Or ask Claude Code: "run it with `echo yes\| uv run python ...`" |
| The answer you typed is treated as **no** | A trailing space or PowerShell piping | Use **Command Prompt**, not PowerShell, and type the answer |
| Output is not valid JSON, or the agent crashes on the model's reply | The model wrapped its answer in markdown fences or added text | `The agent crashed on the model's reply. Strip any markdown fences, parse safely, and treat unreadable output as a validation problem that triggers the retry. Keep the 2-attempt limit.` |
| A7 fails: no functional or non-functional requirements | The prompt output lacks them, or validation does not require them | `Test A7 failed. Ask the model for functional and non-functional requirement lists, print both before the approval question, and make validation fail when either list is empty.` |
| A8 fails: "approve or reject" is one story | Decomposition is missing | `Test A8 failed: R2 has one story but the sentence has two actions. Tell the model to write one story per action joined by "and" or "or", and make validation require at least two stories for such a sentence.` |
| A1 passes but A3 fails (no question for a vague word) | Validation does not require questions, or the prompt does not ask | `Test A3 failed. Make the validation fail when there is no clarifying question, and make the analyze prompt ask for one question per vague word.` |
| The graph runs to the end without pausing for approval | The approval pause is missing or skipped | `The agent did not pause for approval. Add a human approval step using interrupt before the design, with a checkpointer and a thread id, and a route that stops on "no".` |
| Answering `yes` after the pause does nothing | No checkpointer or thread id, so it cannot resume | `The paused run cannot resume. Compile the graph with InMemorySaver and pass a thread_id in the config when invoking and resuming.` |
| The retry limit is not respected | A loop without a counter | `The agent can retry more than twice. Count attempts in the state and stop after 2, going to the stop route.` |
| Scope check shows `langchain` | Claude Code used LangChain | `Remove every LangChain import. Use ollama.chat directly with model gpt-oss:120b-cloud. Follow CLAUDE.md.` |
| More than one new file appeared | Claude Code split the work | `Put everything in my_agent1.py and delete the extra files you created. Show me the folder listing.` |
| A break-it prompt left the file changed | The temporary change was not restored | `Restore my_agent1.py to the version before the temporary change and show me that the validation rules are back.` |
| The wording is different from the example | Models vary every run | Not a failure. Check **shape and rules**, not exact words |

## Problems with rules and skills (concepts block)

| Test | What you see | Try this |
| --- | --- | --- |
| R1, S1 | Claude Code says it cannot write into `.claude`, and prints the file text instead | `.claude` is a sensitive folder, so it needs your permission. Ask again and **allow** the write when prompted. If it still will not write, save the printed text into the file path it showed (your trainer can help) |
| R2 | It does not quote the rules | Rules load when a session **starts**. Quit and start `claude` again from the repository root |
| R3 | You get 0 or 1 out of 3 | That is a real result. Record it. Do not "fix" it: it is the lesson |
| R4 | The last line marker did not appear | The scoped rule loads when Claude Code works with a matching file. Make sure the file is named `my_*.py` inside a `Day-*` folder and ask it to edit that existing file |
| S1 | The skill has different checks from the prompt | Claude Code "improved" it. Say: `Replace the file with exactly the text between START and END in my prompt, character for character. Change nothing else.` |
| S2 | `/accept-check` is not recognised | Restart `claude`. Skills are found at session start. Check that the file is `.claude\skills\accept-check\SKILL.md` |
| S3 | It does not reject a bad file | Show me the skill file and make sure the langchain check says PASS only if nothing is printed |

## Rescue: last resort

If you have followed the fix loop and it still fails, tell your trainer. They may hand you the matching known-good file **for that step only**. You must then run all the acceptance tests on it yourself, and write **"used rescue"** and the reason on your acceptance sheet. Using the rescue is allowed. Hiding it is not.
