# Day 9 — RAG Engineering

## What You'll Learn Today

- Explain what RAG (retrieval-augmented generation) means: retrieve approved evidence first, then generate an answer from it.
- Describe why a model's fluent recall is not the same as evidence — private, current, and sourceable facts belong in managed documents instead.
- Trace the two-step RAG sequence in a graph: a deterministic retrieval step, followed by a model generation step.
- Explain why constraining the generation prompt to only the retrieved context helps keep the model's answer grounded in your own data.
- Run `example.py`, then ask one password question and one VPN question to see retrieval change the context.

## Why This Matters

A model's training gives it fluent, confident-sounding answers, but fluency is not evidence — it can't know your company's private, current, or sourceable facts unless you give them to it directly. RAG solves this by changing what the model sees, not by changing the model itself: first you retrieve a piece of approved context, then you ask the model to generate an answer using only that context. This session builds the smallest version of that idea using an intentionally inspectable retriever — plain Python and a small dictionary of articles, with no hidden magic — so you can see exactly what gets retrieved and why before adding any real complexity later.

## Key Concepts

**Ingestion and Chunks (the preparation step).** Before any question is asked, source material has to be loaded, cleaned, split, labeled, and indexed — this is called ingestion, and the sample data in this session is already prepared for you. When documents are split up, each resulting piece is called a chunk. A good chunk is focused enough to match a specific question, but complete enough to actually answer it — chunking is a quality choice you make deliberately, not a fixed magic number.

**Metadata.** Alongside the actual text, real documents usually carry descriptive fields like an ID, title, category, date, and access label, so an answer can always be traced back to where it came from. This example skips metadata entirely to keep things simple — `ARTICLES` is just a keyword mapped to a plain text string, with no ID attached to either.

**Vectors and Similarity (the idea behind matching).** One way to compare a question against a document is to turn both into numbers — a list of features that a similarity function can compare, sometimes as simple as counting how often each lowercase word appears in each piece of text. Cosine similarity is one common way to score how close two of these number lists are: shared terms push the score up. The intuition matters more than the formula — a representation like this is transparent, but it can miss a match if the question uses a different word than the document does (a limitation Day 10 addresses directly).

**The Retrieval Node and the Grounded Prompt.** In the graph, a question comes in and the retrieval node returns context — this lookup is ordinary application code, not a model decision. The generation prompt is then deliberately constrained to that context: `"Use only this context: {context}\nQuestion: {question}"`. A constraint like this helps keep the model's answer grounded, though it still doesn't replace validating the output afterward.

**No-Match Handling.** `ARTICLES` in this example has no source IDs, so there's no citation (like a `KB-101` label) to name in the answer — that's a real RAG capability worth knowing about, but it isn't built into this file. What happens on a miss matters just as much: if no keyword in `ARTICLES` matches the question, `context` is set to a fixed `"No matching article found."` string — but the `answer` node still runs and still calls the model with that context. Generation is never skipped here; a more complete pipeline might abstain and skip generation entirely on a miss, to save cost and avoid the model guessing at an unsupported answer.

## Code Walkthrough — `Day-09-RAG-Engineering/example.py`

```python
"""Session 9: retrieve local text and give it to Ollama."""

import sys

import ollama
from langgraph.graph import END, START, StateGraph

sys.stdout.reconfigure(encoding="utf-8")  # the model may answer with punctuation Command Prompt cannot print


MODEL = "gpt-oss:120b-cloud"
ARTICLES = {
    "password": "Reset a password at portal.example/reset.",
    "vpn": "For VPN issues, reconnect and enter your company password.",
}


def retrieve(state):
    question = state["question"].lower()
    context = "No matching article found."
    for keyword, article in ARTICLES.items():
        if keyword in question:
            context = article
    return {"question": state["question"], "context": context}


def answer(state):
    prompt = f"Use only this context: {state['context']}\nQuestion: {state['question']}"
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return {"answer": response["message"]["content"]}


graph_builder = StateGraph(dict)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("answer", answer)
graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "answer")
graph_builder.add_edge("answer", END)
graph = graph_builder.compile()

result = graph.invoke({"question": "How do I reset my password?"})
print(result["answer"])
```

1. `sys.stdout.reconfigure(encoding="utf-8")` makes sure Command Prompt can print any punctuation the model's answer might contain.
2. `ARTICLES` is a small local knowledge base — two entries, keyed by the keyword `password` or `vpn`.
3. `retrieve` lowercases the incoming question and checks whether either keyword appears in it. If a keyword matches, its article becomes the `context`; if nothing matches, the context stays `"No matching article found."` This is a simple, transparent stand-in for the vector-similarity search idea discussed in the slides — it works by direct keyword matching rather than by comparing number vectors.
4. `retrieve` returns both the original `question` and the chosen `context` into state.
5. `answer` builds one prompt telling the model to "use only this context," then calls `ollama.chat` with the fixed `MODEL` and returns the model's reply as `answer`.
6. The graph runs `retrieve` then `answer` in sequence, and the last line prints the final grounded answer.

## Hands-On Lab (~30 minutes)

**Graph to draw:** `START -> retrieve -> answer -> END`

**Setup and run (Windows Command Prompt, from the repository root):**

```cmd
cd L2-Agent-Engineering
uv sync
uv run python Day-09-RAG-Engineering\example.py
```

This example calls `ollama.chat` with the fixed model `gpt-oss:120b-cloud`, so make sure Ollama is running locally and signed in with that model available before you run it.

**Steps:**
1. Open only `example.py` in the session folder.
2. Find each node function, then find `StateGraph` and the node registrations.
3. Follow the edges from `START` to `END`.
4. Predict the printed result before running the file.

**Small change to try:** Ask one password question and one VPN question — for example, change the question near the bottom of the file to something about VPN issues, then run it again and compare the retrieved context and the model's answer to the password version.

**Control question:** Retrieval is fixed by the keyword rules in `ARTICLES`. The model only writes an answer from the context it's given — it does not choose what to retrieve.

## Assignment

**Goal:** Make one small change to `example.py` and explain how the result changes.

**Steps:**
1. Read the sample question near the bottom of the file and predict the current output without running it.
2. Run the example from the repository root using the command above.
3. Change only one input value or one short question.
4. Predict the new context or output before running again.
5. Run the same command again and compare to your prediction.
6. Write three short sentences: what you changed, what happened, and why.

**Rules:** Keep the example in one Python file. Use LangGraph directly. Do not add a test folder or helper package, and do not replace `uv` with another package manager. Use the Windows Command Prompt commands shown above. Keep `MODEL = "gpt-oss:120b-cloud"` unchanged.

## Before You Move to Day 10

- The file runs successfully from the repository root.
- You can name the input, the nodes, the route, and the output.
- You can explain the two-step RAG sequence (retrieve, then generate) and which step is deterministic.
- You can explain why the prompt constrains the model to the retrieved context, and what actually happens in this example when nothing matches.
- Your one-change assignment ran twice and your three-sentence explanation matches what you actually observed.
