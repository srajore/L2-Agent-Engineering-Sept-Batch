# Day 10 — Advanced RAG

## What You'll Learn Today

- Explain why a correct source article can still fail to be retrieved if the user's wording doesn't overlap with it.
- Rewrite a known phrase into knowledge-base vocabulary before retrieval runs, while preserving the original question.
- Trace one question through a rewrite rule and see how the rewritten wording changes what gets retrieved.
- Explain the ideas of metadata filtering, ranking, and packing context within a size budget, even though this example keeps them simple.
- Run `example.py`, predict its output, then add one synonym to the rewrite rule and see how retrieval changes.

## Why This Matters

Session 9 showed that retrieval can miss a good source simply because of vocabulary mismatch — someone might ask about a "remote tunnel" when the actual article is about a VPN, and no keyword overlap means no match, even though the source itself is completely correct. Today's session is about closing that gap and about being honest with yourself when you claim retrieval got "better": you measure a baseline, change exactly one component, and compare results, because "better" only means something once it's tied to a defined test. The core technique here is question rewriting — replacing a user's phrasing with terms the knowledge base actually uses — while carefully preserving the original question alongside the rewritten one, since rewriting is meant to help retrieval, not to quietly change what the user actually asked.

## Key Concepts

**Rewriting and Preserving Intent.** The rewrite step replaces a known user phrase with the knowledge-base's own term (for example, turning "remote tunnel" into "vpn"), but the original question is kept and stored alongside the rewritten search query. Rewriting is a retrieval aid, not permission to alter the task the user actually asked for.

**Measuring Improvement with Labeled Cases (a concept, not built here).** To know whether a change actually helps, you'd pair a handful of questions with the source ID that's expected to rank first for each one, and count how many the system gets right before making a change — that's the baseline score. After adding the rewrite rule, you'd run the exact same labeled cases again and compare the new count to the baseline, keeping the data and labels unchanged so the comparison is fair. `example.py` doesn't build that scoring harness — it runs exactly one hardcoded question through exactly one rewrite rule so you can trace the mechanism by hand. The measurement idea above is worth carrying into any real retrieval work, even though this file doesn't demonstrate it.

**Multi-Query, with a Cost.** One way to extend recall further is to search a few different phrasings of the same question and merge the unique results together — this is discussed as an idea in this session, not required in the lab itself. It isn't free: extra searches add latency, cost, and can pull in irrelevant candidates, so any real system needs to cap how many alternative phrasings it tries.

**Filtering, Ranking, and Packing.** Before ranking anything, metadata filters (category, tenant, date, permission) should remove documents a user isn't even eligible to see — these are security filters, not optional ranking hints, and they apply first. What's left gets ranked by similarity score, keeping only a small `top_k` number of results. But a count limit like `top_k` is not the same as a size budget — two very long chunks can still overflow the space available for context, so packing means adding labeled results one at a time only until the character budget would be exceeded, while making sure to preserve each result's ID as you go.

**Validating Citations (a concept, not built here).** In a system that cites sources, once an answer names a source ID, that ID should be checked against the packed context that was actually given to the model — every cited ID must be present in what was retrieved. `ARTICLES` in this example, like Day 9's, has no source IDs at all, so there's nothing to cite or validate — `show_result` just reports the retrieved text as `answer`. This membership check is worth knowing about (and it's a useful but limited one: it confirms a citation's source was part of the context, not that every claim in the answer is fully supported by it), even though this file doesn't demonstrate it.

## Code Walkthrough — `Day-10-Advanced-RAG/example.py`

```python
"""Session 10: rewrite a question before retrieving context."""

from langgraph.graph import END, START, StateGraph


ARTICLES = {
    "password": "Use the self-service password reset page.",
    "vpn": "Reconnect the VPN client before contacting support.",
}


def rewrite_question(state):
    clearer = state["question"].lower().replace("login code", "password")
    return {"clearer_question": clearer}


def retrieve(state):
    context = "No match"
    for keyword, article in ARTICLES.items():
        if keyword in state["clearer_question"]:
            context = article
    return {"context": context}


def show_result(state):
    return {"answer": f"Retrieved: {state['context']}"}


graph_builder = StateGraph(dict)
graph_builder.add_node("rewrite", rewrite_question)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("show", show_result)
graph_builder.add_edge(START, "rewrite")
graph_builder.add_edge("rewrite", "retrieve")
graph_builder.add_edge("retrieve", "show")
graph_builder.add_edge("show", END)
graph = graph_builder.compile()

result = graph.invoke({"question": "I forgot my login code"})
print(result["answer"])
```

1. `ARTICLES` is the same small keyword-to-article knowledge base style used in Session 9, with `password` and `vpn` entries.
2. `rewrite_question` lowercases the incoming question and replaces the phrase `"login code"` with `"password"` — this is the rewrite rule that bridges vocabulary that doesn't match the knowledge base directly.
3. The rewritten text is returned as `clearer_question`, a separate field from the original `question` — nothing overwrites the original input.
4. `retrieve` checks the *rewritten* question for the `password` or `vpn` keyword and picks the matching article as `context`, or `"No match"` if neither appears.
5. `show_result` formats the final context into a printable `answer` string.
6. The graph runs `rewrite -> retrieve -> show` in sequence, and the sample input `"I forgot my login code"` gets rewritten to contain `"password"`, so it retrieves the password article even though the original question never used that word.

## Hands-On Lab (~30 minutes)

**Graph to draw:** `START -> rewrite -> retrieve -> show -> END`

**Setup and run (Windows Command Prompt, from the repository root):**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-10-Advanced-RAG\example.py
```

This example is fully deterministic and does not call Ollama or any live model. (An optional live run — asking about a "remote tunnel" and getting a VPN answer citing a source — is discussed in the slides as an extension, but is not required for this lab.)

**Steps:**
1. Open only `example.py` in the session folder.
2. Find each node function, then find `StateGraph` and the node registrations.
3. Follow the edges from `START` to `END`.
4. Predict the printed result before running the file.

**Small change to try:** Add one more synonym to the rewrite rule — for example, extend the `.replace(...)` logic (or chain a second `.replace(...)` call) so a phrase like `"remote tunnel"` also gets rewritten to `"vpn"`. Run the file again with a question using your new phrase and confirm it now retrieves the VPN article.

**Control question:** The developer controls both the rewrite rule and the retrieval rule — the model is not involved in either decision in this example.

## Assignment

**Goal:** Make one small change to `example.py` and explain how the result changes.

**Steps:**
1. Read the sample question near the bottom of the file and predict the current output without running it.
2. Run the example from the repository root using the command above.
3. Change only one input value or one short question.
4. Predict the new context or output before running again.
5. Run the same command again and compare to your prediction.
6. Write three short sentences: what you changed, what happened, and why.

**Rules:** Keep the example in one Python file. Use LangGraph directly. Do not add a test folder or helper package, and do not replace `uv` with another package manager. Use the Windows Command Prompt commands shown above. Do not add an Ollama call — this session's example is intentionally deterministic.

## Before You Move to Day 11

- The file runs successfully from the repository root.
- You can name the input, the nodes, the route, and the output.
- You can explain why a rewrite step can fix a retrieval miss caused by vocabulary mismatch, and why the original question is still kept.
- You can explain the difference between a count limit (`top_k`) and a size budget (packing), even at a conceptual level.
- Your one-change assignment ran twice and your three-sentence explanation matches what you actually observed.
